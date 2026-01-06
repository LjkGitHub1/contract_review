from celery import shared_task
import logging
from django.utils import timezone
from .models import ReviewTask, ReviewResult, ReviewOpinion
from apps.contracts.models import Contract
from .services_auto import AutoReviewService
from .services_report import ReportGeneratorService

logger = logging.getLogger(__name__)


@shared_task
def process_review_task(task_id):
    """处理审核任务 - 统一流程：先AI审核，后人工审核"""
    try:
        task = ReviewTask.objects.get(id=task_id)
        contract = task.contract
        
        # 步骤1: AI自动审核
        logger.info(f'[开始] 开始AI自动审核 - 任务ID: {task_id}')
        task.status = 'ai_processing'
        task.started_at = timezone.now()
        # 初始化进度
        task.progress = {
            'current_step': '初始化',
            'progress': 0,
            'message': '正在初始化审核任务...',
            'steps': []
        }
        task.save()
        
        auto_review_service = AutoReviewService()
        ai_result = auto_review_service.process_auto_review(contract, task)
        
        # 检查AI审核结果
        if not ai_result or not ai_result.get('success', False):
            error_msg = ai_result.get('error', 'AI审核失败') if ai_result else 'AI审核返回空结果'
            logger.error(f'AI审核失败 - 任务ID: {task_id}, 错误: {error_msg}')
            task.status = 'failed'
            task.error_message = error_msg
            task.completed_at = timezone.now()
            task.save()
            return ai_result
        
        # 获取AI审核结果
        try:
            review_result = ReviewResult.objects.get(review_task=task)
        except ReviewResult.DoesNotExist:
            logger.warning(f'审核任务{task_id}未找到审核结果')
            task.status = 'failed'
            task.error_message = 'AI审核完成但未找到审核结果'
            task.completed_at = timezone.now()
            task.save()
            return ai_result
        
        # 步骤2: 如果配置了审核层级，生成针对每个层级的AI建议
        if task.review_levels and isinstance(task.review_levels, list) and len(task.review_levels) > 0:
            logger.info(f'开始为各层级生成AI审核建议 - 任务ID: {task_id}')
            from .services import ReviewService
            from apps.users.models import User
            from apps.reviews.models import ReviewFocusConfig
            
            review_service = ReviewService()
            
            # 为每个配置的层级生成AI建议
            level_suggestions = {}
            for level in task.review_levels:
                try:
                    # 获取该层级的审核重点配置
                    focus_config = ReviewFocusConfig.objects.get(level=level, is_active=True)
                    
                    # 获取该层级分配的审核员（如果有）
                    reviewer_id = task.reviewer_assignments.get(level) if task.reviewer_assignments else None
                    reviewer = None
                    if reviewer_id:
                        try:
                            reviewer = User.objects.get(id=reviewer_id)
                        except User.DoesNotExist:
                            pass
                    
                    # 如果没有分配审核员，创建一个临时用户对象用于生成建议
                    if not reviewer:
                        # 创建一个临时用户对象，只设置reviewer_level
                        class TempUser:
                            def __init__(self, level):
                                self.reviewer_level = level
                            def get_reviewer_level_display(self):
                                level_map = {'level1': '一级审核员', 'level2': '二级审核员', 'level3': '三级审核员（高级）'}
                                return level_map.get(self.reviewer_level, self.reviewer_level)
                        
                        reviewer = TempUser(level)
                    
                    # 生成针对该层级的AI建议
                    suggestions = review_service.generate_ai_suggestions_for_reviewer(
                        contract=contract,
                        reviewer=reviewer,
                        review_task=task
                    )
                    
                    level_suggestions[level] = suggestions
                    logger.info(f'已为{level}层级生成AI审核建议 - 任务ID: {task_id}')
                    
                except ReviewFocusConfig.DoesNotExist:
                    logger.warning(f'未找到{level}层级的审核重点配置 - 任务ID: {task_id}')
                    level_suggestions[level] = {
                        'error': f'未找到{level}层级的审核重点配置',
                        'suggestions': None
                    }
                except Exception as e:
                    logger.error(f'为{level}层级生成AI建议失败: {str(e)} - 任务ID: {task_id}')
                    level_suggestions[level] = {
                        'error': f'生成AI建议失败: {str(e)}',
                        'suggestions': None
                    }
            
            # 保存层级建议到审核结果
            if not review_result.review_data:
                review_result.review_data = {}
            review_result.review_data['level_suggestions'] = level_suggestions
            review_result.save()
        
        # 步骤3: AI审核完成，更新状态为ai_completed
        task.status = 'ai_completed'
        task.save()
        logger.info(f'AI审核完成 - 任务ID: {task_id}')
        
        # 步骤4: 如果配置了审核层级，更新状态为manual_reviewing，等待人工审核
        if task.review_levels and isinstance(task.review_levels, list) and len(task.review_levels) > 0:
            task.status = 'manual_reviewing'
            task.save()
            logger.info(f'任务进入人工审核阶段 - 任务ID: {task_id}')
        else:
            # 如果没有配置审核层级，直接标记为已完成
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            logger.info(f'任务完成（无人工审核） - 任务ID: {task_id}')
        
        # 生成Word格式报告
        try:
            report_service = ReportGeneratorService()
            report_path = report_service.generate_word_report(review_result, contract)
            review_result.report_path = report_path
            review_result.save()
            logger.info(f'审核任务{task_id}自动生成报告成功: {report_path}')
        except Exception as e:
            logger.error(f'审核任务{task_id}自动生成报告失败: {str(e)}')
            # 报告生成失败不影响审核任务完成
        
        return {
            'success': True,
            'review_result_id': review_result.id,
            'status': task.status,
            'ai_result': ai_result,
            'level_suggestions': level_suggestions if task.review_levels else {}
        }
        
    except Exception as e:
        logger.error(f'处理审核任务失败: {str(e)} - 任务ID: {task_id}')
        task = ReviewTask.objects.get(id=task_id)
        task.status = 'failed'
        task.error_message = str(e)
        task.completed_at = timezone.now()
        task.save()
        raise

