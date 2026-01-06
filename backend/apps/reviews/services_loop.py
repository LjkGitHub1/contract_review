"""
审核意见闭环服务模块 - 处理审核意见的汇总、反馈、修改、重新提交
"""
import json
import logging
from typing import Dict, List, Optional
from django.utils import timezone
from django.db.models import Q
from apps.contracts.models import Contract, ContractVersion
from apps.reviews.models import ReviewTask, ReviewOpinion, ReviewResult
from apps.users.models import User

logger = logging.getLogger(__name__)


class ReviewOpinionLoopService:
    """审核意见闭环服务类"""
    
    def summarize_opinions(
        self,
        contract: Contract,
        review_tasks: Optional[List[ReviewTask]] = None
    ) -> Dict:
        """
        自动汇总各层级审核意见
        
        Args:
            contract: 合同对象
            review_tasks: 审核任务列表（可选，如果不提供则获取所有相关任务）
            
        Returns:
            Dict: 汇总结果
        """
        try:
            # 获取审核任务
            if review_tasks is None:
                review_tasks = ReviewTask.objects.filter(
                    contract=contract,
                    status='completed'
                ).order_by('created_at')
            
            # 按层级分组意见
            opinions_by_level = {
                'level1': [],
                'level2': [],
                'level3': []
            }
            
            all_opinions = []
            for task in review_tasks:
                # 通过review_result获取opinions
                try:
                    review_result = task.result
                    opinions = ReviewOpinion.objects.filter(
                        review_result=review_result,
                        contract=contract
                    )
                except ReviewResult.DoesNotExist:
                    continue
                
                for opinion in opinions:
                    level = task.reviewer_level or 'unknown'
                    if level in opinions_by_level:
                        opinions_by_level[level].append(opinion)
                    all_opinions.append(opinion)
                    # 设置opinion的review_task引用（用于后续查询）
                    if not hasattr(opinion, '_review_task'):
                        opinion._review_task = task
            
            # 生成汇总表
            summary_table = self._generate_summary_table(
                contract=contract,
                opinions_by_level=opinions_by_level,
                all_opinions=all_opinions
            )
            
            return {
                'success': True,
                'contract_id': contract.id,
                'total_opinions': len(all_opinions),
                'opinions_by_level': {
                    level: len(opinions)
                    for level, opinions in opinions_by_level.items()
                },
                'summary_table': summary_table
            }
            
        except Exception as e:
            logger.error(f'意见汇总失败: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary_table(
        self,
        contract: Contract,
        opinions_by_level: Dict,
        all_opinions: List[ReviewOpinion]
    ) -> Dict:
        """生成审核意见汇总表"""
        
        summary = {
            'contract_info': {
                'title': contract.title,
                'contract_no': contract.contract_no,
                'contract_type': contract.get_contract_type_display()
            },
            'level1_opinions': [
                {
                    'id': op.id,
                    'type': op.get_opinion_type_display(),
                    'risk_level': op.get_risk_level_display() if op.risk_level else '未设置',
                    'content': op.content,
                    'clause': op.clause_content,
                    'suggestion': op.suggestion,
                    'legal_basis': op.legal_basis,
                    'created_at': op.created_at.isoformat() if op.created_at else None
                }
                for op in opinions_by_level.get('level1', [])
            ],
            'level2_opinions': [
                {
                    'id': op.id,
                    'type': op.get_opinion_type_display(),
                    'risk_level': op.get_risk_level_display() if op.risk_level else '未设置',
                    'content': op.content,
                    'clause': op.clause_content,
                    'suggestion': op.suggestion,
                    'legal_basis': op.legal_basis,
                    'created_at': op.created_at.isoformat() if op.created_at else None
                }
                for op in opinions_by_level.get('level2', [])
            ],
            'level3_opinions': [
                {
                    'id': op.id,
                    'type': op.get_opinion_type_display(),
                    'risk_level': op.get_risk_level_display() if op.risk_level else '未设置',
                    'content': op.content,
                    'clause': op.clause_content,
                    'suggestion': op.suggestion,
                    'legal_basis': op.legal_basis,
                    'created_at': op.created_at.isoformat() if op.created_at else None
                }
                for op in opinions_by_level.get('level3', [])
            ],
            'all_opinions': [
                {
                    'id': op.id,
                    'reviewer_level': getattr(op, '_review_task', None).reviewer_level if hasattr(op, '_review_task') and op._review_task else None,
                    'type': op.get_opinion_type_display(),
                    'risk_level': op.get_risk_level_display() if op.risk_level else '未设置',
                    'content': op.opinion_content,
                    'clause': op.clause_content,
                    'suggestion': op.suggestion,
                    'legal_basis': op.legal_basis,
                    'status': op.get_status_display(),
                    'created_at': op.created_at.isoformat() if op.created_at else None
                }
                for op in all_opinions
            ],
            'statistics': {
                'total_opinions': len(all_opinions),
                'high_risk_count': sum(1 for op in all_opinions if op.risk_level == 'high'),
                'medium_risk_count': sum(1 for op in all_opinions if op.risk_level == 'medium'),
                'low_risk_count': sum(1 for op in all_opinions if op.risk_level == 'low'),
                'pending_count': sum(1 for op in all_opinions if op.status == 'pending'),
                'processed_count': sum(1 for op in all_opinions if op.status == 'processed')
            }
        }
        
        return summary
    
    def feedback_to_drafter(
        self,
        contract: Contract,
        summary_table: Dict,
        feedback_message: Optional[str] = None
    ) -> Dict:
        """
        反馈审核意见给起草人
        
        Args:
            contract: 合同对象
            summary_table: 意见汇总表
            feedback_message: 反馈消息（可选）
            
        Returns:
            Dict: 反馈结果
        """
        try:
            # 更新合同状态为"待修改"
            contract.status = 'reviewing'  # 或者可以添加新的状态如 'needs_revision'
            contract.save()
            
            # 这里可以发送通知给起草人
            # TODO: 实现通知功能（邮件、站内消息等）
            
            return {
                'success': True,
                'contract_id': contract.id,
                'contract_status': contract.status,
                'summary_table': summary_table,
                'feedback_message': feedback_message or '请根据审核意见修改合同'
            }
            
        except Exception as e:
            logger.error(f'反馈给起草人失败: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def resubmit_for_review(
        self,
        contract: Contract,
        modified_by: User,
        change_summary: Optional[str] = None
    ) -> Dict:
        """
        重新提交审核
        
        Args:
            contract: 合同对象
            modified_by: 修改人
            change_summary: 修改摘要（可选）
            
        Returns:
            Dict: 提交结果
        """
        try:
            # 创建新版本
            new_version = contract.current_version + 1
            version = ContractVersion.objects.create(
                contract=contract,
                version=new_version,
                content=contract.content,
                file_path=contract.file_path,
                change_summary=change_summary or '根据审核意见修改后重新提交',
                changed_by=modified_by
            )
            
            contract.current_version = new_version
            contract.status = 'reviewing'
            contract.save()
            
            # 创建新的审核任务
            review_task = ReviewTask.objects.create(
                contract=contract,
                contract_version=new_version,
                task_type='auto',  # 或根据配置决定
                status='pending',
                created_by=modified_by
            )
            
            return {
                'success': True,
                'contract_id': contract.id,
                'new_version': new_version,
                'review_task_id': review_task.id,
                'message': '合同已重新提交审核'
            }
            
        except Exception as e:
            logger.error(f'重新提交审核失败: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }

