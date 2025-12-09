from celery import shared_task
from django.utils import timezone
from .models import ReviewTask, ReviewResult, ReviewOpinion
from apps.contracts.models import Contract


@shared_task
def process_review_task(task_id):
    """处理审核任务"""
    try:
        task = ReviewTask.objects.get(id=task_id)
        contract = task.contract
        
        # 模拟审核过程
        # 实际应该调用AI模型进行审核
        review_data = {
            'contract_id': contract.id,
            'reviewed_at': timezone.now().isoformat(),
            'clauses_reviewed': [],
            'risks_found': []
        }
        
        # 创建审核结果
        result = ReviewResult.objects.create(
            review_task=task,
            contract=contract,
            overall_score=85.5,
            risk_level='medium',
            risk_count=3,
            summary='合同审核完成，发现3个中等风险点',
            review_data=review_data
        )
        
        # 创建示例审核意见
        ReviewOpinion.objects.create(
            review_result=result,
            clause_id='clause_1',
            clause_content='合同主体条款',
            opinion_type='risk',
            risk_level='medium',
            opinion_content='建议明确合同主体信息',
            legal_basis='《合同法》相关规定',
            suggestion='补充完整的合同主体信息'
        )
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        return {'status': 'success', 'result_id': result.id}
    except Exception as e:
        task = ReviewTask.objects.get(id=task_id)
        task.status = 'failed'
        task.error_message = str(e)
        task.completed_at = timezone.now()
        task.save()
        raise

