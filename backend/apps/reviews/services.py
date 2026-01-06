"""
审核服务模块 - 包含AI审核建议生成等功能
"""
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from apps.reviews.models import ReviewFocusConfig, ReviewTask, ReviewResult, ReviewOpinion
from apps.contracts.models import Contract
from apps.users.models import User

try:
    import requests
except ImportError:
    requests = None
    logging.warning('requests模块未安装，AI API调用功能将不可用')

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类 - 用于调用AI接口生成审核建议"""
    
    def __init__(self, config=None):
        """
        初始化AI服务
        
        Args:
            config: AIModelConfig对象，如果为None则从数据库获取默认配置
        """
        if config is None:
            # 从数据库获取默认配置
            try:
                from .models import AIModelConfig
                config = AIModelConfig.objects.filter(is_default=True, is_active=True).first()
            except Exception:
                config = None
        
        if config:
            self.api_key = config.api_key
            self.api_url = config.api_base_url.rstrip('/') + '/chat/completions'
            self.available_models = config.available_models or []
            self.model = config.default_model or (self.available_models[0] if self.available_models else '')
            self.enabled = config.is_active
            self.temperature = config.temperature
            self.max_tokens = config.max_tokens
            self.timeout = config.timeout
            self.provider = config.provider
            
            # 验证模型配置
            if self.enabled and not self.model:
                logger.warning(f'AI服务已启用但未配置默认模型，将使用模拟数据')
                logger.warning(f'可用模型列表: {self.available_models}')
                self.enabled = False  # 如果模型未配置，禁用AI服务
            elif self.enabled and self.model and self.available_models and self.model not in self.available_models:
                logger.warning(f'默认模型 {self.model} 不在可用模型列表中，将使用模拟数据')
                logger.warning(f'可用模型列表: {self.available_models}')
                self.enabled = False  # 如果模型不在列表中，禁用AI服务
        else:
            # 从settings中读取AI配置（兼容旧配置）
            self.api_key = getattr(settings, 'AI_API_KEY', None)
            self.api_url = getattr(settings, 'AI_API_URL', 'https://api.openai.com/v1/chat/completions')
            self.model = getattr(settings, 'AI_MODEL', 'gpt-3.5-turbo')
            self.enabled = getattr(settings, 'AI_ENABLED', False)
            self.temperature = 0.7
            self.max_tokens = 2000
            self.timeout = 30
            self.provider = 'openai'
    
    def generate_review_suggestions(
        self,
        contract_content: str,
        reviewer_level: str,
        focus_config: ReviewFocusConfig
    ) -> Dict:
        """
        根据审核员层级和审核重点配置，生成AI审核建议
        
        Args:
            contract_content: 合同内容（文本）
            reviewer_level: 审核员层级 (level1/level2/level3)
            focus_config: 审核重点配置对象
            
        Returns:
            Dict: 包含审核建议的字典
        """
        if not self.enabled or not self.model:
            error_msg = 'AI服务未启用或未配置模型，无法生成审核建议。请管理员在AI模型配置中启用AI服务并配置正确的模型。'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # 构建AI提示词
            prompt = self._build_prompt(contract_content, reviewer_level, focus_config)
            
            # 调用AI接口
            suggestions = self._call_ai_api(prompt)
            
            # 验证返回结果
            if not suggestions or (isinstance(suggestions, dict) and suggestions.get('error')):
                error_msg = suggestions.get('error', 'AI返回结果无效') if isinstance(suggestions, dict) else 'AI返回结果为空'
                logger.error(f'AI审核建议生成失败: {error_msg}')
                raise Exception(f'AI审核建议生成失败: {error_msg}')
            
            return suggestions
        except Exception as e:
            logger.error(f'AI审核建议生成失败: {str(e)}')
            raise Exception(f'AI审核建议生成失败: {str(e)}。请检查AI模型配置和网络连接。')
    
    def _build_prompt(
        self,
        contract_content: str,
        reviewer_level: str,
        focus_config: ReviewFocusConfig
    ) -> str:
        """构建AI提示词"""
        focus_points = ', '.join(focus_config.focus_points)
        attention_items = ', '.join(focus_config.attention_items or [])
        
        prompt = f"""你是一位专业的合同审核专家，请根据以下要求对合同进行审核：

审核员层级：{focus_config.level_name}
审核重点：{focus_points}
审核标准：{focus_config.review_standards}
关注事项：{attention_items}

合同内容：
{contract_content[:5000]}  # 限制长度避免超出token限制

请按照以下格式返回审核建议：
1. 总体评价（简要说明合同整体情况）
2. 发现的问题（列出发现的问题，每个问题包含：问题描述、风险等级、法律依据、修改建议）
3. 重点关注事项（根据审核重点，列出需要特别关注的内容）
4. 审核结论（通过/不通过/需要修改）

请以JSON格式返回，格式如下：
{{
    "overall_evaluation": "总体评价",
    "issues": [
        {{
            "clause_id": "条款ID或位置",
            "clause_content": "条款内容",
            "issue_description": "问题描述",
            "risk_level": "high/medium/low",
            "legal_basis": "法律依据",
            "suggestion": "修改建议"
        }}
    ],
    "focus_points": [
        {{
            "point": "关注点",
            "status": "正常/异常/需关注",
            "description": "说明"
        }}
    ],
    "conclusion": "通过/不通过/需要修改",
    "summary": "审核摘要"
}}
"""
        return prompt
    
    def test_api_connection(self) -> Dict:
        """
        测试API连接 - 真正调用API，不使用模拟数据
        
        Returns:
            Dict: 包含测试结果的字典
            
        Raises:
            Exception: 如果API调用失败，抛出异常
        """
        if not self.enabled or not self.api_key:
            raise Exception('AI服务未启用或未配置API密钥')
        
        if requests is None:
            raise Exception('requests模块未安装，无法调用AI API')
        
        if not self.model:
            raise Exception('未配置默认模型')
        
        try:
            # 构建简单的测试消息
            messages = [
                {"role": "system", "content": "你是一位专业的助手。"},
                {"role": "user", "content": "你好，请回复'连接成功'"}
            ]
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': 0.3,
                'max_tokens': 50  # 测试时使用较少的token
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=10  # 测试时使用较短的超时时间
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析响应
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return {
                        'success': True,
                        'message': 'API连接测试成功',
                        'response': content,
                        'model': self.model
                    }
                else:
                    raise Exception('API响应格式错误：未找到choices字段')
            else:
                # 解析错误响应
                try:
                    error_data = response.json()
                    error_code = error_data.get('code', '')
                    error_message = error_data.get('message', response.text)
                    
                    # 特殊处理模型不存在的错误
                    if error_code == 20012 or 'Model does not exist' in error_message:
                        raise Exception(f"AI模型 '{self.model}' 不存在。错误代码：{error_code}，错误信息：{error_message}")
                    
                    raise Exception(f'API调用失败（状态码：{response.status_code}）：{error_message}')
                except ValueError:
                    # 如果响应不是JSON格式
                    raise Exception(f'API调用失败（状态码：{response.status_code}）：{response.text[:200]}')
                    
        except requests.exceptions.Timeout:
            raise Exception('API调用超时，请检查网络连接或API服务状态')
        except requests.exceptions.ConnectionError:
            raise Exception('无法连接到API服务，请检查网络连接和API地址配置')
        except Exception as e:
            # 重新抛出异常，不返回模拟数据
            raise
    
    def _call_ai_api(self, prompt: str) -> Dict:
        """
        调用AI API
        支持硅基流动、OpenAI等
        """
        if not self.enabled or not self.api_key:
            error_msg = 'AI服务未启用或未配置API密钥，无法调用AI API。请管理员在AI模型配置中启用AI服务并配置API密钥。'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        if requests is None:
            error_msg = 'requests模块未安装，无法调用AI API。请安装requests库: pip install requests'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            
            # 构建请求数据
            messages = [
                {"role": "system", "content": "你是一位专业的合同审核专家。"},
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': min(self.temperature, 0.5),  # 降低温度以加快响应
                'max_tokens': min(self.max_tokens, 3000)  # 限制最大token数
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析响应（兼容不同API格式）
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    # 尝试解析JSON，如果失败则返回原始内容
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，返回文本内容
                        return {
                            'overall_evaluation': content,
                            'issues': [],
                            'focus_points': [],
                            'conclusion': '需要修改',
                            'summary': content[:200]
                        }
                else:
                    raise Exception('API响应格式错误')
            else:
                # 解析错误响应
                try:
                    error_data = response.json()
                    error_code = error_data.get('code', '')
                    error_message = error_data.get('message', response.text)
                    
                    # 特殊处理模型不存在的错误
                    if error_code == 20012 or 'Model does not exist' in error_message:
                        available_models_str = ', '.join(self.available_models[:5]) if self.available_models else '无'
                        error_msg = (f"AI模型 '{self.model}' 不存在。可能的原因：\n"
                                   f"1. 模型名称拼写错误\n"
                                   f"2. 该模型在当前API服务中不可用\n"
                                   f"3. API密钥权限不足\n\n"
                                   f"当前配置的可用模型列表：{available_models_str}\n\n"
                                   f"请管理员在'AI模型配置'页面检查并更新模型配置。")
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    error_msg = f'API调用失败: {response.status_code} - {error_message}'
                except:
                    error_msg = f'API调用失败: {response.status_code} - {response.text}'
                
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = 'AI API调用超时，请检查网络连接或增加超时时间设置'
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            # 如果是我们抛出的异常，直接重新抛出
            if isinstance(e, Exception) and not isinstance(e, requests.exceptions.RequestException):
                raise
            error_msg = f'AI API调用失败: {str(e)}'
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _generate_mock_suggestions(
        self,
        contract_content: str,
        reviewer_level: str,
        focus_config: ReviewFocusConfig
    ) -> Dict:
        """生成模拟审核建议（用于测试或AI未启用时）"""
        # 根据层级生成不同的建议
        if reviewer_level == 'level1':
            return {
                "overall_evaluation": "合同格式基本规范，基础信息完整，但部分条款编号需要检查。",
                "issues": [
                    {
                        "clause_id": "条款1",
                        "clause_content": "合同主体信息",
                        "issue_description": "合同主体信息不够详细",
                        "risk_level": "low",
                        "legal_basis": "《合同法》要求合同主体信息明确",
                        "suggestion": "建议补充完整的合同主体信息，包括名称、地址、联系方式等"
                    }
                ],
                "focus_points": [
                    {
                        "point": "格式规范",
                        "status": "正常",
                        "description": "合同格式符合要求"
                    },
                    {
                        "point": "基础条款完整性",
                        "status": "需关注",
                        "description": "部分基础条款需要补充"
                    }
                ],
                "conclusion": "需要修改",
                "summary": "合同基础信息完整，但需要补充部分细节"
            }
        elif reviewer_level == 'level2':
            return {
                "overall_evaluation": "合同条款基本符合法律法规，但存在一些风险点需要关注。",
                "issues": [
                    {
                        "clause_id": "违约责任条款",
                        "clause_content": "违约责任约定",
                        "issue_description": "违约责任约定不够明确，可能产生争议",
                        "risk_level": "medium",
                        "legal_basis": "《合同法》第107条",
                        "suggestion": "建议明确违约责任的承担方式和计算标准"
                    }
                ],
                "focus_points": [
                    {
                        "point": "法律合规性",
                        "status": "正常",
                        "description": "合同条款符合法律法规"
                    },
                    {
                        "point": "风险识别",
                        "status": "需关注",
                        "description": "发现中等风险点"
                    }
                ],
                "conclusion": "需要修改",
                "summary": "合同基本合规，但需要完善风险控制条款"
            }
        else:  # level3
            return {
                "overall_evaluation": "合同整体风险可控，符合企业战略方向，建议批准签署。",
                "issues": [
                    {
                        "clause_id": "战略风险",
                        "clause_content": "合同整体评估",
                        "issue_description": "合同对企业战略影响较小，风险可控",
                        "risk_level": "low",
                        "legal_basis": "企业战略评估",
                        "suggestion": "建议批准签署，但需要持续关注合同执行情况"
                    }
                ],
                "focus_points": [
                    {
                        "point": "重大风险",
                        "status": "正常",
                        "description": "未发现重大风险"
                    },
                    {
                        "point": "战略层面",
                        "status": "正常",
                        "description": "符合企业战略"
                    }
                ],
                "conclusion": "通过",
                "summary": "合同风险可控，建议批准"
            }
    
    def _generate_mock_suggestions_from_prompt(self, prompt: str) -> Dict:
        """从提示词生成模拟建议（简化版）"""
        # 这里可以根据prompt内容生成更智能的模拟数据
        return {
            "overall_evaluation": "AI生成的总体评价",
            "issues": [],
            "focus_points": [],
            "conclusion": "需要修改",
            "summary": "AI生成的审核摘要"
        }
    
    def chat(self, message: str, history: List[Dict] = None) -> str:
        """
        AI对话功能
        
        Args:
            message: 用户消息
            history: 对话历史，格式：[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            
        Returns:
            str: AI回复内容
        """
        if not self.enabled or not self.api_key:
            logger.warning('AI服务未启用或未配置API密钥，返回模拟回复')
            return "抱歉，AI服务未启用或未配置。请管理员在AI模型配置中设置API密钥和模型。"
        
        if requests is None:
            logger.error('requests模块未安装，无法调用AI API')
            return "抱歉，系统配置错误，无法使用AI服务。"
        
        try:
            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是一位专业的合同审核专家助手，擅长解答合同审核、法律合规、风险识别等相关问题。请用专业、友好、易懂的方式回答用户的问题。"}
            ]
            
            # 添加历史对话
            if history:
                for h in history[-10:]:  # 只保留最近10轮对话
                    if h.get('role') in ['user', 'assistant'] and h.get('content'):
                        messages.append({
                            "role": h['role'],
                            "content": h['content']
                        })
            
            # 添加当前消息
            messages.append({"role": "user", "content": message})
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析响应
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return content
                else:
                    raise Exception('API响应格式错误')
            else:
                # 解析错误响应
                try:
                    error_data = response.json()
                    error_code = error_data.get('code', '')
                    error_message = error_data.get('message', response.text)
                    
                    # 特殊处理模型不存在的错误
                    if error_code == 20012 or 'Model does not exist' in error_message:
                        logger.error(f'AI模型不存在: {self.model} - 请检查AI模型配置')
                        available_models_str = ', '.join(self.available_models[:5]) if self.available_models else '无'
                        return f"抱歉，配置的AI模型 '{self.model}' 在API服务中不存在。\n\n" \
                               f"可能的原因：\n" \
                               f"1. 模型名称拼写错误\n" \
                               f"2. 该模型在当前API服务中不可用\n" \
                               f"3. API密钥权限不足\n\n" \
                               f"当前配置的可用模型列表：{available_models_str}\n\n" \
                               f"请管理员在'AI模型配置'页面检查并更新模型配置。"
                    
                    error_msg = f'API调用失败: {error_message}'
                except:
                    error_msg = f'API调用失败: {response.status_code} - {response.text}'
                
                logger.error(error_msg)
                return f"抱歉，AI服务调用失败：{error_msg}\n\n如果问题持续，请联系管理员检查AI模型配置。"
                
        except requests.exceptions.Timeout:
            logger.error('AI API调用超时')
            return "抱歉，AI服务响应超时，请稍后重试。如果问题持续，请联系管理员检查网络连接和API服务状态。"
        except Exception as e:
            logger.error(f'AI对话调用失败: {str(e)}')
            # 如果是模型相关错误，提供更详细的帮助
            error_str = str(e)
            if 'model' in error_str.lower() or '20012' in error_str:
                return f"抱歉，AI模型配置有问题：{error_str}\n\n请管理员检查AI模型配置，确保：\n1. 模型名称正确\n2. API密钥有效\n3. 模型在服务商处可用"
            return f"抱歉，发生了错误：{error_str}\n\n如果问题持续，请联系管理员。"


class ReviewService:
    """审核服务类 - 处理审核相关业务逻辑"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_ai_suggestions_for_reviewer(
        self,
        contract: Contract,
        reviewer: User,
        review_task: Optional[ReviewTask] = None
    ) -> Dict:
        """
        为指定审核员生成AI审核建议
        
        Args:
            contract: 合同对象
            reviewer: 审核员对象
            review_task: 审核任务对象（可选）
            
        Returns:
            Dict: 包含AI审核建议的字典
        """
        # 检查审核员是否有层级
        if not reviewer.reviewer_level:
            return {
                'error': '该用户未设置审核员层级',
                'suggestions': None
            }
        
        # 获取审核重点配置
        try:
            focus_config = ReviewFocusConfig.objects.get(
                level=reviewer.reviewer_level,
                is_active=True
            )
        except ReviewFocusConfig.DoesNotExist:
            return {
                'error': f'未找到{reviewer.get_reviewer_level_display()}的审核重点配置',
                'suggestions': None
            }
        
        # 获取合同内容
        contract_content = self._extract_contract_content(contract)
        
        # 调用AI生成建议
        suggestions = self.ai_service.generate_review_suggestions(
            contract_content=contract_content,
            reviewer_level=reviewer.reviewer_level,
            focus_config=focus_config
        )
        
        # 保存AI建议到审核结果（如果提供了review_task）
        if review_task:
            self._save_ai_suggestions(review_task, suggestions, reviewer, focus_config)
        
        return {
            'reviewer_level': reviewer.reviewer_level,
            'reviewer_level_name': reviewer.get_reviewer_level_display(),
            'focus_config': {
                'level': focus_config.level,
                'level_name': focus_config.level_name,
                'focus_points': focus_config.focus_points,
                'review_standards': focus_config.review_standards
            },
            'suggestions': suggestions
        }
    
    def _extract_contract_content(self, contract: Contract) -> str:
        """提取合同内容为文本"""
        if contract.content:
            # 如果content是JSON，转换为文本
            if isinstance(contract.content, dict):
                return json.dumps(contract.content, ensure_ascii=False, indent=2)
            elif isinstance(contract.content, str):
                return contract.content
        
        # 如果有文件，可以读取文件内容
        if contract.file_path:
            # TODO: 实现文件内容读取
            pass
        
        return contract.title or "合同内容"
    
    def _save_ai_suggestions(
        self,
        review_task: ReviewTask,
        suggestions: Dict,
        reviewer: User,
        focus_config: ReviewFocusConfig
    ):
        """保存AI建议到审核结果"""
        # 获取或创建审核结果
        review_result, created = ReviewResult.objects.get_or_create(
            review_task=review_task,
            defaults={
                'contract': review_task.contract,
                'summary': suggestions.get('summary', ''),
                'review_data': {
                    'ai_suggestions': suggestions,
                    'reviewer_level': reviewer.reviewer_level,
                    'focus_config_id': focus_config.id,
                    'generated_at': timezone.now().isoformat()
                }
            }
        )
        
        if not created:
            # 更新现有结果
            review_result.summary = suggestions.get('summary', review_result.summary)
            if not review_result.review_data:
                review_result.review_data = {}
            review_result.review_data['ai_suggestions'] = suggestions
            review_result.review_data['reviewer_level'] = reviewer.reviewer_level
            review_result.review_data['focus_config_id'] = focus_config.id
            review_result.review_data['generated_at'] = timezone.now().isoformat()
            review_result.save()
        
        # 保存审核意见
        issues = suggestions.get('issues', [])
        for issue in issues:
            ReviewOpinion.objects.create(
                review_result=review_result,
                reviewer=reviewer,
                clause_id=issue.get('clause_id', ''),
                clause_content=issue.get('clause_content', ''),
                opinion_type='risk' if issue.get('risk_level') else 'suggestion',
                risk_level=issue.get('risk_level', 'low'),
                opinion_content=issue.get('issue_description', ''),
                legal_basis=issue.get('legal_basis', ''),
                suggestion=issue.get('suggestion', ''),
                status='pending'
            )

