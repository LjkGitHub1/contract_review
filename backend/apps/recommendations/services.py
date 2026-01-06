"""
智能推荐服务模块
"""
import json
import logging
from typing import Dict, List, Optional
from django.db.models import Q, Count, Avg
from django.utils import timezone
from apps.contracts.models import Contract, Template
from apps.reviews.models import ReviewTask, ReviewResult, ReviewOpinion
from apps.rules.models import ReviewRule
from apps.recommendations.models import Recommendation
from apps.users.models import User
from apps.reviews.services import AIService

logger = logging.getLogger(__name__)


class RecommendationService:
    """智能推荐服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def recommend_clauses(
        self,
        contract: Contract,
        user: User,
        context: str = 'drafting'
    ) -> List[Dict]:
        """
        推荐合同条款
        
        Args:
            contract: 合同对象
            user: 用户对象
            context: 推荐场景（drafting/modifying/reviewing/negotiating）
            
        Returns:
            List[Dict]: 推荐条款列表
        """
        try:
            recommendations = []
            
            # 1. 基于合同类型的条款推荐
            contract_type_clauses = self._get_clauses_by_contract_type(contract.contract_type)
            for clause in contract_type_clauses:
                recommendations.append({
                    'type': 'clause',
                    'item_type': 'clause',
                    'item_content': clause,
                    'score': 0.8,
                    'reason': f'基于合同类型"{contract.contract_type}"的推荐条款',
                    'context': context
                })
            
            # 2. 基于用户习惯的条款推荐
            user_habit_clauses = self._get_clauses_by_user_habit(user, contract.contract_type)
            for clause in user_habit_clauses:
                recommendations.append({
                    'type': 'clause',
                    'item_type': 'clause',
                    'item_content': clause,
                    'score': 0.7,
                    'reason': '基于您历史使用习惯的推荐条款',
                    'context': context
                })
            
            # 3. 基于AI的智能条款推荐
            if self.ai_service.enabled:
                ai_clauses = self._get_ai_recommended_clauses(contract, context)
                for clause in ai_clauses:
                    recommendations.append({
                        'type': 'clause',
                        'item_type': 'clause',
                        'item_content': clause['content'],
                        'score': clause.get('score', 0.6),
                        'reason': clause.get('reason', 'AI智能推荐条款'),
                        'context': context
                    })
            
            # 4. 基于相似合同的条款推荐
            similar_clauses = self._get_clauses_from_similar_contracts(contract)
            for clause in similar_clauses:
                recommendations.append({
                    'type': 'clause',
                    'item_type': 'clause',
                    'item_content': clause['content'],
                    'score': clause.get('score', 0.65),
                    'reason': f'来自相似合同（{clause.get("source", "未知")}）的条款',
                    'context': context
                })
            
            # 去重并按分数排序
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            # 保存推荐记录
            self._save_recommendations(contract, user, unique_recommendations, 'clause', context)
            
            return unique_recommendations[:10]  # 返回前10个推荐
            
        except Exception as e:
            logger.error(f'条款推荐失败: {str(e)}')
            return []
    
    def recommend_templates(
        self,
        contract_type: str,
        industry: str = '',
        user: Optional[User] = None
    ) -> List[Dict]:
        """
        推荐合同模板
        
        Args:
            contract_type: 合同类型
            industry: 所属行业
            user: 用户对象（可选）
            
        Returns:
            List[Dict]: 推荐模板列表
        """
        try:
            recommendations = []
            
            # 1. 基于合同类型和行业的模板推荐
            templates = Template.objects.filter(
                is_deleted=False,
                is_public=True
            )
            
            if contract_type:
                templates = templates.filter(contract_type=contract_type)
            
            if industry:
                templates = templates.filter(industry=industry)
            
            # 按使用次数排序
            templates = templates.order_by('-usage_count', '-created_at')
            
            for template in templates[:5]:
                score = 0.7
                reason = f'基于合同类型"{contract_type}"和行业"{industry}"的推荐模板'
                
                # 如果模板使用次数多，提高分数
                if template.usage_count > 10:
                    score = 0.85
                elif template.usage_count > 5:
                    score = 0.75
                
                recommendations.append({
                    'type': 'template',
                    'item_type': 'template',
                    'item_id': template.id,
                    'item_content': template.name,
                    'score': score,
                    'reason': reason
                })
            
            # 2. 基于用户习惯的模板推荐
            if user:
                user_templates = self._get_templates_by_user_habit(user, contract_type)
                for template in user_templates:
                    recommendations.append({
                        'type': 'template',
                        'item_type': 'template',
                        'item_id': template.id,
                        'item_content': template.name,
                        'score': 0.8,
                        'reason': '基于您历史使用习惯的推荐模板'
                    })
            
            # 去重并按分数排序
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            # 保存推荐记录
            if user:
                self._save_recommendations(None, user, unique_recommendations, 'template', 'drafting')
            
            return unique_recommendations[:5]  # 返回前5个推荐
            
        except Exception as e:
            logger.error(f'模板推荐失败: {str(e)}')
            return []
    
    def recommend_risk_responses(
        self,
        contract: Contract,
        review_result: Optional[ReviewResult] = None,
        user: Optional[User] = None
    ) -> List[Dict]:
        """
        推荐风险应对建议
        
        Args:
            contract: 合同对象
            review_result: 审核结果对象（可选）
            user: 用户对象（可选）
            
        Returns:
            List[Dict]: 风险应对建议列表
        """
        try:
            recommendations = []
            
            # 1. 基于审核结果的风险应对建议
            if review_result:
                opinions = ReviewOpinion.objects.filter(
                    review_result=review_result,
                    risk_level__in=['high', 'medium']
                ).order_by('-risk_level')
                
                for opinion in opinions[:5]:
                    # 使用AI生成风险应对建议
                    if self.ai_service.enabled:
                        response = self._get_ai_risk_response(contract, opinion)
                    else:
                        response = self._get_default_risk_response(opinion)
                    
                    recommendations.append({
                        'type': 'risk_response',
                        'item_type': 'risk_response',
                        'item_id': opinion.id,
                        'item_content': response['content'],
                        'score': 0.9 if opinion.risk_level == 'high' else 0.7,
                        'reason': f'针对"{opinion.clause_content[:50]}..."的风险应对建议',
                        'context': 'reviewing'
                    })
            
            # 2. 基于规则的风险应对建议
            rules = ReviewRule.objects.filter(
                is_active=True,
                risk_level__in=['high', 'medium']
            )
            
            if contract.industry:
                rules = rules.filter(
                    Q(industry=contract.industry) | Q(rule_type='general')
                )
            
            for rule in rules[:3]:
                recommendations.append({
                    'type': 'risk_response',
                    'item_type': 'risk_response',
                    'item_id': rule.id,
                    'item_content': rule.legal_basis or rule.description,
                    'score': 0.75,
                    'reason': f'基于规则"{rule.rule_name}"的风险应对建议',
                    'context': 'reviewing'
                })
            
            # 去重并按分数排序
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            # 保存推荐记录
            if user:
                self._save_recommendations(contract, user, unique_recommendations, 'risk_response', 'reviewing')
            
            return unique_recommendations[:5]  # 返回前5个推荐
            
        except Exception as e:
            logger.error(f'风险应对建议推荐失败: {str(e)}')
            return []
    
    def _get_clauses_by_contract_type(self, contract_type: str) -> List[str]:
        """根据合同类型获取推荐条款"""
        clause_templates = {
            'procurement': [
                '合同标的条款',
                '交货方式条款',
                '验收标准条款',
                '付款方式条款',
                '质量保证条款',
                '违约责任条款'
            ],
            'sales': [
                '合同标的条款',
                '交货方式条款',
                '验收标准条款',
                '付款方式条款',
                '质量保证条款',
                '违约责任条款'
            ],
            'service': [
                '服务内容条款',
                '服务标准条款',
                '服务费用条款',
                '验收标准条款',
                '知识产权条款',
                '保密条款'
            ],
            'labor': [
                '工作内容条款',
                '工作地点条款',
                '工作时间条款',
                '劳动报酬条款',
                '社会保险条款',
                '保密和竞业限制条款'
            ]
        }
        return clause_templates.get(contract_type, [])
    
    def _get_clauses_by_user_habit(self, user: User, contract_type: str) -> List[str]:
        """根据用户习惯获取推荐条款"""
        # 查询用户历史使用的合同
        contracts = Contract.objects.filter(
            drafter=user,
            contract_type=contract_type,
            is_deleted=False
        ).order_by('-created_at')[:5]
        
        clauses = []
        for contract in contracts:
            if contract.content:
                # 从合同内容中提取常用条款（简化实现）
                if isinstance(contract.content, dict):
                    # 提取条款关键词
                    pass
                elif isinstance(contract.content, str):
                    # 简单的文本分析
                    if '违约责任' in contract.content:
                        clauses.append('违约责任条款')
                    if '付款方式' in contract.content:
                        clauses.append('付款方式条款')
        
        return list(set(clauses))  # 去重
    
    def _get_ai_recommended_clauses(self, contract: Contract, context: str) -> List[Dict]:
        """使用AI推荐条款"""
        try:
            prompt = f"""请根据以下合同信息，推荐3-5个应该包含的合同条款：

合同类型：{contract.contract_type}
所属行业：{contract.industry or '通用'}
推荐场景：{context}

请以JSON格式返回，格式如下：
[
  {{
    "content": "条款名称和简要说明",
    "score": 0.8,
    "reason": "推荐理由"
  }}
]"""
            
            response = self.ai_service._call_ai_api(prompt)
            
            if isinstance(response, dict) and 'overall_evaluation' in response:
                # 如果返回的是审核建议格式，转换为条款推荐格式
                return []
            
            # 尝试解析JSON
            try:
                if isinstance(response, str):
                    import json
                    clauses = json.loads(response)
                elif isinstance(response, list):
                    clauses = response
                else:
                    clauses = []
                
                return clauses[:5]
            except:
                return []
                
        except Exception as e:
            logger.error(f'AI条款推荐失败: {str(e)}')
            return []
    
    def _get_clauses_from_similar_contracts(self, contract: Contract) -> List[Dict]:
        """从相似合同中获取条款"""
        similar_contracts = Contract.objects.filter(
            contract_type=contract.contract_type,
            industry=contract.industry,
            is_deleted=False
        ).exclude(id=contract.id).order_by('-created_at')[:3]
        
        clauses = []
        for similar_contract in similar_contracts:
            if similar_contract.content:
                clauses.append({
                    'content': f'参考合同：{similar_contract.title}',
                    'score': 0.65,
                    'source': similar_contract.title
                })
        
        return clauses
    
    def _get_templates_by_user_habit(self, user: User, contract_type: str) -> List[Template]:
        """根据用户习惯获取推荐模板"""
        # 查询用户使用过的模板
        contracts = Contract.objects.filter(
            drafter=user,
            contract_type=contract_type,
            template__isnull=False,
            is_deleted=False
        ).select_related('template')
        
        template_ids = contracts.values_list('template_id', flat=True).distinct()
        templates = Template.objects.filter(
            id__in=template_ids,
            is_deleted=False
        ).order_by('-usage_count')
        
        return list(templates[:3])
    
    def _get_ai_risk_response(self, contract: Contract, opinion: ReviewOpinion) -> Dict:
        """使用AI生成风险应对建议"""
        try:
            prompt = f"""请针对以下合同风险问题，提供具体的应对建议：

风险问题：{opinion.opinion_content}
风险等级：{opinion.risk_level}
法律依据：{opinion.legal_basis or '无'}

请提供：
1. 具体的修改建议
2. 风险控制措施
3. 预防措施

请以JSON格式返回，格式如下：
{{
  "content": "详细的应对建议",
  "measures": ["措施1", "措施2"],
  "prevention": "预防措施"
}}"""
            
            response = self.ai_service._call_ai_api(prompt)
            
            if isinstance(response, dict):
                return {
                    'content': response.get('content', opinion.suggestion or '请根据审核意见进行修改'),
                    'measures': response.get('measures', []),
                    'prevention': response.get('prevention', '')
                }
            else:
                return {
                    'content': opinion.suggestion or '请根据审核意见进行修改',
                    'measures': [],
                    'prevention': ''
                }
                
        except Exception as e:
            logger.error(f'AI风险应对建议生成失败: {str(e)}')
            return self._get_default_risk_response(opinion)
    
    def _get_default_risk_response(self, opinion: ReviewOpinion) -> Dict:
        """获取默认风险应对建议"""
        return {
            'content': opinion.suggestion or '请根据审核意见进行修改',
            'measures': [],
            'prevention': ''
        }
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """去重推荐列表"""
        seen = set()
        unique = []
        for rec in recommendations:
            key = (rec.get('type'), rec.get('item_id'), rec.get('item_content', '')[:50])
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        return unique
    
    def _save_recommendations(
        self,
        contract: Optional[Contract],
        user: User,
        recommendations: List[Dict],
        recommendation_type: str,
        context: str = 'drafting'
    ):
        """保存推荐记录到数据库"""
        try:
            for rec in recommendations:
                Recommendation.objects.create(
                    user=user,
                    contract=contract,
                    recommendation_type=recommendation_type,
                    recommendation_context=context,
                    item_type=rec.get('item_type', ''),
                    item_id=rec.get('item_id'),
                    item_content=rec.get('item_content', ''),
                    score=rec.get('score', 0.5),
                    reason=rec.get('reason', '')
                )
        except Exception as e:
            logger.error(f'保存推荐记录失败: {str(e)}')

