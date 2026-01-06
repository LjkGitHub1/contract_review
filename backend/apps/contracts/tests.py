"""
合同管理模块单元测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.contracts.models import Contract, Template

User = get_user_model()


class ContractModelTest(TestCase):
    """合同模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_contract(self):
        """测试创建合同"""
        contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        self.assertEqual(contract.title, '测试合同')
        self.assertEqual(contract.contract_type, 'procurement')
        self.assertEqual(contract.drafter, self.user)
        self.assertFalse(contract.is_deleted)
    
    def test_soft_delete(self):
        """测试软删除"""
        contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        contract.is_deleted = True
        contract.save()
        
        # 软删除后，默认查询应该不包含
        self.assertNotIn(contract, Contract.objects.filter(is_deleted=False))
        self.assertIn(contract, Contract.objects.all())


class ContractAPITest(TestCase):
    """合同API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_contract(self):
        """测试创建合同API"""
        data = {
            'title': '测试合同',
            'contract_type': 'procurement',
            'industry': '制造业'
        }
        response = self.client.post('/api/contracts/contracts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contract.objects.count(), 1)
        self.assertEqual(Contract.objects.first().title, '测试合同')
    
    def test_list_contracts(self):
        """测试获取合同列表API"""
        Contract.objects.create(
            title='合同1',
            contract_type='procurement',
            drafter=self.user
        )
        Contract.objects.create(
            title='合同2',
            contract_type='sales',
            drafter=self.user
        )
        
        response = self.client.get('/api/contracts/contracts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_contract_detail(self):
        """测试获取合同详情API"""
        contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        
        response = self.client.get(f'/api/contracts/contracts/{contract.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '测试合同')
    
    def test_update_contract(self):
        """测试更新合同API"""
        contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        
        data = {'title': '更新后的合同'}
        response = self.client.patch(f'/api/contracts/contracts/{contract.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(contract.title, '更新后的合同')
    
    def test_delete_contract(self):
        """测试删除合同API（软删除）"""
        contract = Contract.objects.create(
            title='测试合同',
            contract_type='procurement',
            drafter=self.user
        )
        
        response = self.client.delete(f'/api/contracts/contracts/{contract.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        contract.refresh_from_db()
        self.assertTrue(contract.is_deleted)


class TemplateAPITest(TestCase):
    """模板API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_template(self):
        """测试创建模板API"""
        data = {
            'name': '测试模板',
            'contract_type': 'procurement',
            'content': '模板内容'
        }
        response = self.client.post('/api/contracts/templates/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 1)

