"""
审核模块单元测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.contracts.models import Contract
from apps.reviews.models import ReviewTask, ReviewResult, ReviewOpinion

User = get_user_model()


class ReviewTaskModelTest(TestCase):
    """审核任务模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
    
    def test_create_review_task(self):
        """测试创建审核任务"""
        task = ReviewTask.objects.create(
            contract=self.contract,
            task_type='auto',
            priority='high',
            created_by=self.user
        )
        self.assertEqual(task.contract, self.contract)
        self.assertEqual(task.task_type, 'auto')
        self.assertEqual(task.status, 'pending')
    
    def test_task_status_transition(self):
        """测试任务状态转换"""
        task = ReviewTask.objects.create(
            contract=self.contract,
            task_type='auto',
            priority='high',
            created_by=self.user
        )
        self.assertEqual(task.status, 'pending')
        
        task.status = 'processing'
        task.save()
        self.assertEqual(task.status, 'processing')
        
        task.status = 'completed'
        task.save()
        self.assertEqual(task.status, 'completed')


class ReviewAPITest(TestCase):
    """审核API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_review_task(self):
        """测试创建审核任务API"""
        data = {
            'contract': self.contract.id,
            'task_type': 'auto',
            'priority': 'high'
        }
        response = self.client.post('/api/reviews/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReviewTask.objects.count(), 1)
    
    def test_list_review_tasks(self):
        """测试获取审核任务列表API"""
        ReviewTask.objects.create(
            contract=self.contract,
            task_type='auto',
            priority='high',
            created_by=self.user
        )
        
        response = self.client.get('/api/reviews/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_start_review_task(self):
        """测试启动审核任务API"""
        task = ReviewTask.objects.create(
            contract=self.contract,
            task_type='auto',
            priority='high',
            created_by=self.user
        )
        
        response = self.client.post(f'/api/reviews/tasks/{task.id}/start/')
        # 注意：实际启动可能需要Celery，这里只测试API调用
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])

