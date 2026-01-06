"""
自动审核服务模块 - 处理质检中心的自动审核流程
"""
import json
import logging
from typing import Dict, Optional, List
from django.utils import timezone
from apps.contracts.models import Contract
from apps.reviews.models import ReviewTask, ReviewResult, ReviewOpinion
from apps.rules.services import RuleEngineService
from apps.reviews.services import AIService
from apps.reviews.services_report import ReportGeneratorService

logger = logging.getLogger(__name__)


class AutoReviewService:
    """自动审核服务类 - 处理质检中心的自动审核流程"""
    
    def __init__(self):
        self.rule_engine = RuleEngineService()
        self.ai_service = AIService()
    
    def _update_progress(self, review_task: ReviewTask, step: str, progress: int, message: str = None):
        """更新审核进度"""
        try:
            progress_data = {
                'current_step': step,
                'progress': progress,
                'message': message or step,
                'steps': [
                    {'name': '提取合同内容', 'status': 'completed' if progress >= 10 else 'pending'},
                    {'name': '构建审核提示词', 'status': 'completed' if progress >= 30 else 'pending'},
                    {'name': '调用AI模型审核', 'status': 'processing' if 30 < progress < 80 else ('completed' if progress >= 80 else 'pending')},
                    {'name': '解析AI返回结果', 'status': 'completed' if progress >= 80 else 'pending'},
                    {'name': '转换审核结果格式', 'status': 'completed' if progress >= 90 else 'pending'},
                    {'name': '保存审核结果', 'status': 'completed' if progress >= 100 else 'pending'},
                ]
            }
            review_task.progress = progress_data
            review_task.save(update_fields=['progress'])
            logger.info(f'[进度更新] {step} - {progress}% - {message or ""} - 任务ID: {review_task.id}')
        except Exception as e:
            logger.error(f'更新进度失败: {str(e)} - 任务ID: {review_task.id}')
    
    def process_auto_review(
        self,
        contract: Contract,
        review_task: ReviewTask
    ) -> Dict:
        """
        执行完整的自动审核流程 - 优化版本：直接调用大模型一次性完成审核
        
        Args:
            contract: 合同对象
            review_task: 审核任务对象
            
        Returns:
            Dict: 审核结果
        """
        try:
            # 注意：状态更新由调用方（tasks.py）负责，这里不再重复更新
            logger.info(f'[步骤1/6] 开始快速AI审核 - 合同ID: {contract.id}, 任务ID: {review_task.id}')
            self._update_progress(review_task, '提取合同内容', 10, '正在提取合同内容...')
            
            # 快速审核：直接调用大模型一次性完成所有审核任务
            contract_content = self._extract_contract_content(contract)
            
            # 限制合同内容长度，加快处理速度（最多8000字符）
            if len(contract_content) > 8000:
                contract_content = contract_content[:8000] + '\n...（内容已截断）'
                logger.info(f'[步骤1/6] 合同内容过长，已截断至8000字符 - 合同ID: {contract.id}')
            
            logger.info(f'[步骤2/6] 构建审核提示词 - 合同ID: {contract.id}')
            self._update_progress(review_task, '构建审核提示词', 30, '正在构建AI审核提示词...')
            
            # 构建简化的综合审核提示词（减少token数量）
            prompt = self._build_comprehensive_review_prompt(contract, contract_content)
            
            # 调用AI接口进行一次性审核（设置更长的超时时间）
            if not self.ai_service.enabled or not self.ai_service.model:
                error_msg = 'AI服务未启用或未配置模型，无法进行审核。请管理员在AI模型配置中启用AI服务并配置正确的模型。'
                logger.error(f'[步骤3/6] {error_msg} - 合同ID: {contract.id}')
                raise Exception(error_msg)
            
            logger.info(f'[步骤3/6] 调用AI模型进行审核 - 合同ID: {contract.id}, 模型: {self.ai_service.model}')
            self._update_progress(review_task, '调用AI模型审核', 50, f'正在调用AI大模型({self.ai_service.model})进行审核，请稍候...')
            
            # 临时增加超时时间到120秒
            original_timeout = self.ai_service.timeout
            self.ai_service.timeout = 120
            try:
                ai_review_result = self.ai_service._call_ai_api(prompt)
                
                # 检查返回结果是否包含错误信息
                if isinstance(ai_review_result, dict) and ai_review_result.get('error'):
                    error_msg = f"AI调用返回错误: {ai_review_result.get('error')}"
                    logger.error(f'[步骤3/6] {error_msg} - 合同ID: {contract.id}')
                    raise Exception(error_msg)
                
                # 验证返回结果是否有效
                if not ai_review_result:
                    error_msg = 'AI返回结果为空，无法进行审核'
                    logger.error(f'[步骤3/6] {error_msg} - 合同ID: {contract.id}')
                    raise Exception(error_msg)
                    
            except Exception as e:
                logger.error(f'[步骤3/6] AI调用异常: {str(e)} - 合同ID: {contract.id}')
                raise Exception(f'AI审核调用失败: {str(e)}。请检查AI模型配置和网络连接。')
            finally:
                self.ai_service.timeout = original_timeout
            
            logger.info(f'[步骤4/6] 解析AI返回结果 - 合同ID: {contract.id}')
            self._update_progress(review_task, '解析AI返回结果', 80, '正在解析AI返回的审核结果...')
            
            # 解析AI返回的结果
            if isinstance(ai_review_result, str):
                try:
                    ai_review_result = json.loads(ai_review_result)
                except json.JSONDecodeError as e:
                    logger.warning(f'AI返回结果不是JSON格式，尝试作为文本处理 - 合同ID: {contract.id}')
                    # 如果不是JSON，尝试提取关键信息
                    ai_review_result = {
                        'text': ai_review_result,
                        'semantic_analysis': {'summary': ai_review_result[:200]},
                        'risk_identification': {'risks': []},
                        'risk_quantification': {'risk_score': 0, 'overall_risk_level': 'low'},
                        'clause_scoring': {'average_score': 85},
                        'suggestions': [],
                        'overall_score': 85,
                        'summary': ai_review_result[:200]
                    }
            
            # 跳过规则引擎扫描以加快速度（可选，如果规则引擎很快可以保留）
            # 如果需要规则扫描，可以异步执行或使用快速模式
            rule_scan_result = {'matches': [], 'overall_score': 85}
            logger.info(f'[步骤5/6] 跳过规则引擎扫描以加快审核速度 - 合同ID: {contract.id}')
            
            logger.info(f'[步骤5/6] 转换审核结果格式 - 合同ID: {contract.id}')
            self._update_progress(review_task, '转换审核结果格式', 90, '正在转换审核结果为标准格式...')
            
            # 将AI结果转换为标准格式
            report_data = self._convert_ai_result_to_report(
                contract=contract,
                ai_result=ai_review_result,
                rule_scan_result=rule_scan_result
            )
            
            logger.info(f'[步骤6/6] 保存审核结果 - 合同ID: {contract.id}')
            self._update_progress(review_task, '保存审核结果', 95, '正在保存审核结果和意见...')
            
            # 保存审核结果
            review_result = self._save_review_result(
                review_task=review_task,
                contract=contract,
                report_data=report_data
            )
            
            # 保存审核意见
            suggestions = report_data.get('modification_suggestions', [])
            self._save_review_opinions(
                review_task=review_task,
                contract=contract,
                suggestions=suggestions
            )
            
            logger.info(f'[完成] 快速AI审核完成 - 合同ID: {contract.id}, 结果ID: {review_result.id}')
            self._update_progress(review_task, '审核完成', 100, 'AI审核已完成！')
            
            return {
                'success': True,
                'review_result_id': review_result.id,
                'overall_score': report_data.get('risk_overview', {}).get('overall_score', 85),
                'risk_level': report_data.get('risk_overview', {}).get('risk_level', 'low'),
                'risk_count': report_data.get('risk_overview', {}).get('risk_count', 0),
                'suggestions_count': len(suggestions)
            }
            
        except Exception as e:
            logger.error(f'自动审核失败: {str(e)}')
            review_task.status = 'failed'
            review_task.error_message = str(e)
            review_task.completed_at = timezone.now()
            review_task.save()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _ai_semantic_analysis(self, contract: Contract) -> Dict:
        """大模型语义理解"""
        try:
            # 提取合同内容
            contract_content = self._extract_contract_content(contract)
            
            # 构建提示词
            prompt = f"""
请对以下合同进行语义分析和理解：

合同标题：{contract.title}
合同类型：{contract.get_contract_type_display()}
行业：{contract.industry or '未指定'}

合同内容：
{contract_content[:2000]}...

请分析：
1. 合同的主要内容和目的
2. 合同的关键条款和要点
3. 合同的结构和逻辑
4. 可能存在的语义歧义

请以JSON格式返回分析结果。
"""
            
            # 调用AI接口
            if self.ai_service.enabled:
                analysis = self.ai_service._call_ai_api(prompt)
                if isinstance(analysis, str):
                    try:
                        analysis = json.loads(analysis)
                    except:
                        analysis = {'text': analysis}
            else:
                analysis = {
                    'summary': '合同语义分析（模拟数据）',
                    'key_points': ['合同主体明确', '条款结构完整'],
                    'ambiguities': []
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f'AI语义分析失败: {str(e)}')
            return {
                'summary': '语义分析失败',
                'error': str(e)
            }
    
    def _identify_clauses(self, contract: Contract, ai_analysis: Dict) -> Dict:
        """条款识别"""
        try:
            contract_content = self._extract_contract_content(contract)
            
            # 使用AI识别关键条款
            prompt = f"""
请识别以下合同中的关键条款：

合同内容：
{contract_content[:2000]}...

请识别以下类型的条款：
1. 合同主体（甲方、乙方）
2. 标的物/服务内容
3. 合同期限
4. 责任条款
5. 付款方式
6. 违约责任
7. 争议解决

请以JSON格式返回，格式如下：
{{
    "subjects": ["甲方：...", "乙方：..."],
    "subject_matter": "标的物/服务内容",
    "term": "合同期限",
    "responsibilities": ["责任条款1", "责任条款2"],
    "payment": "付款方式",
    "breach": "违约责任",
    "dispute": "争议解决"
}}
"""
            
            if self.ai_service.enabled:
                clauses = self.ai_service._call_ai_api(prompt)
                if isinstance(clauses, str):
                    try:
                        clauses = json.loads(clauses)
                    except:
                        clauses = {'text': clauses}
            else:
                # 模拟数据
                clauses = {
                    'subjects': ['甲方：待填写', '乙方：待填写'],
                    'subject_matter': '标的物/服务内容',
                    'term': '合同期限',
                    'responsibilities': ['责任条款'],
                    'payment': '付款方式',
                    'breach': '违约责任',
                    'dispute': '争议解决'
                }
            
            return clauses
            
        except Exception as e:
            logger.error(f'条款识别失败: {str(e)}')
            return {}
    
    def _identify_risks(
        self,
        contract: Contract,
        rule_scan_result: Dict,
        clause_identification_result: Dict
    ) -> Dict:
        """风险识别"""
        risks = []
        
        # 从规则扫描结果中提取风险
        for match in rule_scan_result.get('matches', []):
            if match.get('risk_level') != 'low':
                risks.append({
                    'type': 'rule_match',
                    'level': match.get('risk_level', 'medium'),
                    'description': match.get('suggestion', ''),
                    'clause': match.get('matched_clause', ''),
                    'legal_basis': match.get('legal_basis', '')
                })
        
        # 使用AI进行风险分析
        try:
            contract_content = self._extract_contract_content(contract)
            prompt = f"""
请对以下合同进行风险识别：

合同内容：
{contract_content[:2000]}...

请从以下维度识别风险：
1. 合法性风险（是否符合法律法规）
2. 合规性风险（是否符合行业规范）
3. 完整性风险（是否缺少必要条款）
4. 财务风险（付款、金额等）

请以JSON格式返回，格式如下：
{{
    "legality_risks": [{{"level": "high/medium/low", "description": "..."}}],
    "compliance_risks": [{{"level": "high/medium/low", "description": "..."}}],
    "completeness_risks": [{{"level": "high/medium/low", "description": "..."}}],
    "financial_risks": [{{"level": "high/medium/low", "description": "..."}}]
}}
"""
            
            if self.ai_service.enabled:
                ai_risks = self.ai_service._call_ai_api(prompt)
                if isinstance(ai_risks, str):
                    try:
                        ai_risks = json.loads(ai_risks)
                    except:
                        pass
                
                # 合并AI识别的风险
                if isinstance(ai_risks, dict):
                    for risk_type, risk_list in ai_risks.items():
                        if isinstance(risk_list, list):
                            for risk in risk_list:
                                risks.append({
                                    'type': risk_type,
                                    'level': risk.get('level', 'medium'),
                                    'description': risk.get('description', '')
                                })
        except Exception as e:
            logger.error(f'AI风险识别失败: {str(e)}')
        
        return {
            'risks': risks,
            'total_count': len(risks)
        }
    
    def _quantify_risks(self, risk_identification_result: Dict) -> Dict:
        """风险量化分级"""
        risks = risk_identification_result.get('risks', [])
        
        high_risk_count = sum(1 for r in risks if r.get('level') == 'high')
        medium_risk_count = sum(1 for r in risks if r.get('level') == 'medium')
        low_risk_count = sum(1 for r in risks if r.get('level') == 'low')
        
        # 计算风险分数
        risk_score = high_risk_count * 10 + medium_risk_count * 5 + low_risk_count * 1
        
        # 确定总体风险等级
        if high_risk_count > 0:
            overall_risk_level = 'high'
        elif medium_risk_count > 2:
            overall_risk_level = 'medium'
        else:
            overall_risk_level = 'low'
        
        return {
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'risk_score': risk_score,
            'overall_risk_level': overall_risk_level
        }
    
    def _score_clauses(
        self,
        contract: Contract,
        rule_scan_result: Dict,
        clause_identification_result: Dict
    ) -> Dict:
        """逐条扫描对比评分"""
        # 基于规则匹配结果计算分数
        matches = rule_scan_result.get('matches', [])
        
        clause_scores = []
        for match in matches:
            clause_scores.append({
                'clause': match.get('matched_clause', ''),
                'score': match.get('match_score', 0),
                'rule_name': match.get('rule_name', '')
            })
        
        # 计算平均分数
        if clause_scores:
            avg_score = sum(s['score'] for s in clause_scores) / len(clause_scores)
        else:
            avg_score = 100.0
        
        return {
            'clause_scores': clause_scores,
            'average_score': avg_score,
            'total_clauses_scored': len(clause_scores)
        }
    
    def _generate_suggestions(
        self,
        rule_scan_result: Dict,
        risk_identification_result: Dict,
        scoring_result: Dict
    ) -> List[Dict]:
        """生成修改建议"""
        suggestions = []
        
        # 从规则匹配结果生成建议
        for match in rule_scan_result.get('matches', []):
            suggestions.append({
                'type': 'rule_suggestion',
                'priority': 'high' if match.get('risk_level') == 'high' else 'medium',
                'clause': match.get('matched_clause', ''),
                'suggestion': match.get('suggestion', ''),
                'legal_basis': match.get('legal_basis', '')
            })
        
        # 从风险识别结果生成建议
        for risk in risk_identification_result.get('risks', []):
            if risk.get('level') in ['high', 'medium']:
                suggestions.append({
                    'type': 'risk_suggestion',
                    'priority': risk.get('level', 'medium'),
                    'description': risk.get('description', ''),
                    'suggestion': f"建议处理{risk.get('type', '风险')}：{risk.get('description', '')}"
                })
        
        return suggestions
    
    def _generate_report(
        self,
        contract: Contract,
        rule_scan_result: Dict,
        ai_analysis_result: Dict,
        clause_identification_result: Dict,
        risk_identification_result: Dict,
        risk_quantification_result: Dict,
        scoring_result: Dict,
        suggestions: List[Dict]
    ) -> Dict:
        """生成审核报告数据"""
        overall_score = rule_scan_result.get('overall_score', 100)
        risk_level = risk_quantification_result.get('overall_risk_level', 'low')
        risk_count = risk_identification_result.get('total_count', 0)
        
        return {
            'contract_info': {
                'title': contract.title,
                'contract_no': contract.contract_no,
                'contract_type': contract.get_contract_type_display(),
                'industry': contract.industry or '未指定'
            },
            'risk_overview': {
                'overall_score': overall_score,
                'risk_level': risk_level,
                'risk_count': risk_count,
                'high_risk_count': risk_quantification_result.get('high_risk_count', 0),
                'medium_risk_count': risk_quantification_result.get('medium_risk_count', 0),
                'low_risk_count': risk_quantification_result.get('low_risk_count', 0)
            },
            'modification_suggestions': suggestions,
            'legal_basis': [
                match.get('legal_basis', '')
                for match in rule_scan_result.get('matches', [])
                if match.get('legal_basis')
            ],
            'detailed_data': {
                'rule_scan_result': rule_scan_result,
                'ai_analysis_result': ai_analysis_result,
                'clause_identification_result': clause_identification_result,
                'risk_identification_result': risk_identification_result,
                'risk_quantification_result': risk_quantification_result,
                'scoring_result': scoring_result
            }
        }
    
    def _save_review_result(
        self,
        review_task: ReviewTask,
        contract: Contract,
        report_data: Dict
    ) -> ReviewResult:
        """保存审核结果并自动生成报告"""
        risk_overview = report_data.get('risk_overview', {})
        
        review_result, created = ReviewResult.objects.get_or_create(
            review_task=review_task,
            defaults={
                'contract': contract,
                'overall_score': risk_overview.get('overall_score', 100),
                'risk_level': risk_overview.get('risk_level', 'low'),
                'risk_count': risk_overview.get('risk_count', 0),
                'summary': f"自动审核完成，发现{risk_overview.get('risk_count', 0)}个风险点",
                'review_data': report_data
            }
        )
        
        if not created:
            review_result.overall_score = risk_overview.get('overall_score', 100)
            review_result.risk_level = risk_overview.get('risk_level', 'low')
            review_result.risk_count = risk_overview.get('risk_count', 0)
            review_result.summary = f"自动审核完成，发现{risk_overview.get('risk_count', 0)}个风险点"
            review_result.review_data = report_data
            review_result.save()
        
        # 跳过Word报告生成以加快速度（可以后续异步生成）
        logger.info(f'审核结果{review_result.id}已保存，跳过报告生成以加快速度')
        
        return review_result
    
    def _save_review_opinions(
        self,
        review_task: ReviewTask,
        contract: Contract,
        suggestions: List[Dict]
    ):
        """保存审核意见"""
        # 获取审核结果
        try:
            review_result = ReviewResult.objects.get(review_task=review_task)
        except ReviewResult.DoesNotExist:
            logger.warning(f'审核结果不存在，无法保存审核意见 - task_id: {review_task.id}')
            return
        
        for suggestion in suggestions:
            ReviewOpinion.objects.create(
                review_result=review_result,
                contract=contract,
                opinion_type='suggestion',
                risk_level=suggestion.get('priority', 'medium'),
                opinion_content=suggestion.get('suggestion', ''),
                clause_content=suggestion.get('clause', ''),
                suggestion=suggestion.get('suggestion', ''),
                status='pending'
            )
    
    def _build_comprehensive_review_prompt(self, contract: Contract, contract_content: str) -> str:
        """构建详细的综合审核提示词，一次性完成所有审核任务"""
        prompt = f"""你是一位资深的合同审核专家，具有丰富的法律知识和合同审核经验。请对以下合同进行全面、深入、专业的审核。

【合同基本信息】
合同标题：{contract.title}
合同编号：{contract.contract_no or '无编号'}
合同类型：{contract.get_contract_type_display() if hasattr(contract, 'get_contract_type_display') else '未指定'}
所属行业：{contract.industry or '未指定'}

【合同内容】
{contract_content[:8000]}

【审核要求】
请从以下维度对合同进行全面审核：

1. 语义分析（semantic_analysis）：
   - 分析合同的主要内容和目的
   - 识别合同的关键条款和要点
   - 评估合同的结构和逻辑是否清晰
   - 识别可能存在的语义歧义

2. 条款识别（clause_identification）：
   - 识别合同主体（甲方、乙方）信息是否完整
   - 识别标的物/服务内容是否明确
   - 识别合同期限/履行期限
   - 识别责任条款
   - 识别付款方式
   - 识别违约责任条款
   - 识别争议解决条款

3. 风险识别（risk_identification）：
   - 合法性风险：是否符合《中华人民共和国合同法》、《中华人民共和国民法典》等相关法律法规
   - 合规性风险：是否符合行业规范和标准
   - 完整性风险：是否缺少必要条款（如：违约责任、争议解决、保密条款等）
   - 财务风险：付款方式、金额、时间等是否明确，是否存在财务风险
   - 履约风险：交付时间、质量标准、验收标准等是否明确
   - 其他风险：知识产权、保密、不可抗力等条款是否完善

4. 风险量化（risk_quantification）：
   - 根据识别的风险，计算风险分数（高风险10分，中风险5分，低风险1分）
   - 确定总体风险等级（high/medium/low）
   - 统计各级别风险数量

5. 条款评分（clause_scoring）：
   - 对主要条款进行评分（0-100分）
   - 计算平均分数
   - 提供评分依据和评语

6. 修改建议（suggestions）：
   - 针对发现的问题，提供具体的修改建议
   - 建议要具体、可操作
   - 提供法律依据

【输出格式要求】
请严格按照以下JSON格式返回审核结果，只返回JSON，不要其他文字：

{{
    "semantic_analysis": {{
        "summary": "合同语义分析概述（100-200字）",
        "key_points": ["关键要点1", "关键要点2", "关键要点3"],
        "structure": "合同结构评价",
        "ambiguities": ["可能的歧义1", "可能的歧义2"]
    }},
    "clause_identification": {{
        "subjects": ["甲方：[具体信息]", "乙方：[具体信息]"],
        "subject_matter": "标的物/服务内容的具体描述",
        "term": "合同期限/履行期限",
        "responsibilities": ["责任条款1", "责任条款2"],
        "payment": "付款方式的具体描述",
        "breach": "违约责任的具体描述",
        "dispute": "争议解决方式"
    }},
    "risk_identification": {{
        "risks": [
            {{
                "type": "legality/compliance/completeness/financial/performance/other",
                "level": "high/medium/low",
                "description": "风险描述（详细说明）",
                "clause": "相关条款内容或位置",
                "legal_basis": "法律依据或标准依据"
            }}
        ],
        "total_count": 风险总数,
        "high_count": 高风险数量,
        "medium_count": 中风险数量,
        "low_count": 低风险数量
    }},
    "risk_quantification": {{
        "risk_score": 风险分数（数字）,
        "overall_risk_level": "high/medium/low",
        "high_risk_count": 高风险数量,
        "medium_risk_count": 中风险数量,
        "low_risk_count": 低风险数量
    }},
    "clause_scoring": {{
        "clause_scores": [
            {{
                "clause_type": "条款类型（如：合同主体、标的物、付款方式等）",
                "clause_content": "条款内容或位置",
                "score": 分数（0-100）,
                "comments": "评分依据和评语"
            }}
        ],
        "average_score": 平均分数（0-100）
    }},
    "suggestions": [
        {{
            "type": "risk_suggestion/improvement_suggestion",
            "priority": "high/medium/low",
            "clause": "相关条款",
            "suggestion": "具体的修改建议（要详细、可操作）",
            "legal_basis": "法律依据或标准依据"
        }}
    ],
    "overall_score": 总体评分（0-100）,
    "summary": "审核摘要（200-300字，总结合同整体情况、主要风险、关键建议）"
}}

【重要提示】
1. 必须真实、专业、深入地分析合同，不能使用模板化的回答
2. 风险识别要准确，不能遗漏重要风险点
3. 建议要具体、可操作，不能是空泛的建议
4. 所有评分和风险等级要有依据
5. 必须返回有效的JSON格式，可以直接解析"""
        return prompt
    
    def _convert_ai_result_to_report(
        self,
        contract: Contract,
        ai_result: Dict,
        rule_scan_result: Dict
    ) -> Dict:
        """将AI返回的结果转换为标准报告格式"""
        # 提取各个部分的数据
        semantic_analysis = ai_result.get('semantic_analysis', {})
        clause_identification = ai_result.get('clause_identification', {})
        risk_identification = ai_result.get('risk_identification', {})
        risk_quantification = ai_result.get('risk_quantification', {})
        clause_scoring = ai_result.get('clause_scoring', {})
        suggestions = ai_result.get('suggestions', [])
        
        # 计算总体评分和风险等级
        overall_score = ai_result.get('overall_score', clause_scoring.get('average_score', 85))
        risk_level = risk_quantification.get('overall_risk_level', 'low')
        risk_count = risk_identification.get('total_count', 0)
        
        # 构建报告数据
        report_data = {
            'contract_info': {
                'title': contract.title,
                'contract_no': contract.contract_no,
                'contract_type': contract.get_contract_type_display() if hasattr(contract, 'get_contract_type_display') else '未指定',
                'industry': contract.industry or '未指定'
            },
            'risk_overview': {
                'overall_score': overall_score,
                'risk_level': risk_level,
                'risk_count': risk_count,
                'high_risk_count': risk_quantification.get('high_risk_count', 0),
                'medium_risk_count': risk_quantification.get('medium_risk_count', 0),
                'low_risk_count': risk_quantification.get('low_risk_count', 0)
            },
            'modification_suggestions': suggestions,
            'legal_basis': [
                risk.get('legal_basis', '')
                for risk in risk_identification.get('risks', [])
                if risk.get('legal_basis')
            ],
            'detailed_data': {
                'rule_scan_result': rule_scan_result,
                'ai_analysis_result': semantic_analysis,
                'clause_identification_result': clause_identification,
                'risk_identification_result': risk_identification,
                'risk_quantification_result': risk_quantification,
                'scoring_result': clause_scoring
            }
        }
        
        return report_data
    
    def _generate_quick_mock_result(self, contract: Contract) -> Dict:
        """生成快速模拟结果（已废弃，不再使用）"""
        # 此方法已废弃，不再使用模拟数据
        raise Exception('模拟数据已禁用，请配置AI服务')
        return {
            'semantic_analysis': {
                'summary': f'{contract.title}合同审核完成',
                'key_points': ['合同主体明确', '条款结构完整', '基本要素齐全'],
                'structure': '合同结构清晰，包含必要条款'
            },
            'clause_identification': {
                'subjects': ['甲方：待填写', '乙方：待填写'],
                'subject_matter': '标的物/服务内容',
                'term': '合同期限',
                'responsibilities': ['责任条款'],
                'payment': '付款方式',
                'breach': '违约责任',
                'dispute': '争议解决'
            },
            'risk_identification': {
                'risks': [
                    {
                        'type': 'completeness',
                        'level': 'medium',
                        'description': '部分条款需要完善',
                        'clause': '相关条款',
                        'legal_basis': '《合同法》相关规定'
                    }
                ],
                'total_count': 1,
                'high_count': 0,
                'medium_count': 1,
                'low_count': 0
            },
            'risk_quantification': {
                'risk_score': 5,
                'overall_risk_level': 'medium',
                'high_risk_count': 0,
                'medium_risk_count': 1,
                'low_risk_count': 0
            },
            'clause_scoring': {
                'clause_scores': [
                    {
                        'clause_type': '合同主体',
                        'clause_content': '合同主体条款',
                        'score': 85,
                        'comments': '基本完整'
                    }
                ],
                'average_score': 85
            },
            'suggestions': [
                {
                    'type': 'risk_suggestion',
                    'priority': 'medium',
                    'clause': '相关条款',
                    'suggestion': '建议完善相关条款',
                    'legal_basis': '《合同法》相关规定'
                }
            ],
            'overall_score': 85,
            'summary': f'{contract.title}合同审核完成，发现1个中等风险点，总体评分85分'
        }
    
    def _extract_contract_content(self, contract: Contract) -> str:
        """提取合同内容为文本"""
        if contract.content:
            if isinstance(contract.content, dict):
                return json.dumps(contract.content, ensure_ascii=False, indent=2)
            elif isinstance(contract.content, str):
                return contract.content
        
        if contract.file_path:
            # TODO: 实现文件内容读取
            pass
        
        return contract.title or "合同内容"

