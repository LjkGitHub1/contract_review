"""
填充测试数据的管理命令
使用方法: python manage.py fill_test_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from apps.users.models import User, Department, Permission, Role, RolePermission, UserRole, AuditLog
from apps.contracts.models import Contract, ContractVersion, Template, UserHabit
from apps.reviews.models import ReviewTask, ReviewResult, ReviewOpinion, ReviewCycle
from apps.rules.models import ReviewRule, RuleMatch
from apps.clauses.models import ContractClause
from apps.risks.models import RiskIdentification
from apps.comparisons.models import ComparisonTask, ComparisonDiff
from apps.knowledge.models import KnowledgeEntity, KnowledgeRelation, Regulation, Case
from apps.recommendations.models import Recommendation


class Command(BaseCommand):
    help = '填充测试数据到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空现有数据后再填充',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('正在清空现有数据...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('开始填充测试数据...'))
        
        # 按顺序填充数据
        departments = self.create_departments()
        users = self.create_users(departments)
        templates = self.create_templates(users)
        contracts = self.create_contracts(users, templates)
        contract_versions = self.create_contract_versions(contracts, users)
        clauses = self.create_clauses(contracts, users)
        rules = self.create_rules(users)
        review_tasks = self.create_review_tasks(contracts, users)
        review_results = self.create_review_results(review_tasks, contracts)
        review_opinions = self.create_review_opinions(review_results, users)
        rule_matches = self.create_rule_matches(review_tasks, rules, contracts)
        risks = self.create_risks(review_results, contracts, clauses, users)
        comparison_tasks = self.create_comparison_tasks(contracts, templates, users)
        comparison_diffs = self.create_comparison_diffs(comparison_tasks)
        knowledge_entities = self.create_knowledge_entities()
        knowledge_relations = self.create_knowledge_relations(knowledge_entities)
        regulations = self.create_regulations(knowledge_entities)
        cases = self.create_cases(knowledge_entities)
        recommendations = self.create_recommendations(users, contracts)
        user_habits = self.create_user_habits(users)
        audit_logs = self.create_audit_logs(users)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ 测试数据填充完成！'))
        self.stdout.write(f'  - 部门: {len(departments)}')
        self.stdout.write(f'  - 用户: {len(users)}')
        self.stdout.write(f'  - 模板: {len(templates)}')
        self.stdout.write(f'  - 合同: {len(contracts)}')
        self.stdout.write(f'  - 合同版本: {len(contract_versions)}')
        self.stdout.write(f'  - 条款: {len(clauses)}')
        self.stdout.write(f'  - 规则: {len(rules)}')
        self.stdout.write(f'  - 审核任务: {len(review_tasks)}')
        self.stdout.write(f'  - 审核结果: {len(review_results)}')
        self.stdout.write(f'  - 审核意见: {len(review_opinions)}')
        self.stdout.write(f'  - 风险识别: {len(risks)}')
        self.stdout.write(f'  - 对比任务: {len(comparison_tasks)}')
        self.stdout.write(f'  - 知识实体: {len(knowledge_entities)}')
        self.stdout.write(f'  - 推荐记录: {len(recommendations)}')

    def clear_data(self):
        """清空所有测试数据"""
        Recommendation.objects.all().delete()
        Case.objects.all().delete()
        Regulation.objects.all().delete()
        KnowledgeRelation.objects.all().delete()
        KnowledgeEntity.objects.all().delete()
        ComparisonDiff.objects.all().delete()
        ComparisonTask.objects.all().delete()
        RiskIdentification.objects.all().delete()
        RuleMatch.objects.all().delete()
        ReviewOpinion.objects.all().delete()
        ReviewCycle.objects.all().delete()
        ReviewResult.objects.all().delete()
        ReviewTask.objects.all().delete()
        ReviewRule.objects.all().delete()
        ContractClause.objects.all().delete()
        ContractVersion.objects.all().delete()
        Contract.objects.all().delete()
        Template.objects.all().delete()
        UserHabit.objects.all().delete()
        AuditLog.objects.all().delete()
        UserRole.objects.all().delete()
        RolePermission.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()

    def create_departments(self):
        """创建部门"""
        self.stdout.write('创建部门...')
        departments = []
        
        # 一级部门
        dept1 = Department.objects.create(
            name='技术部',
            code='TECH',
            description='负责技术开发和维护'
        )
        departments.append(dept1)
        
        dept2 = Department.objects.create(
            name='法务部',
            code='LEGAL',
            description='负责法律事务和合同审核'
        )
        departments.append(dept2)
        
        dept3 = Department.objects.create(
            name='采购部',
            code='PROC',
            description='负责采购业务'
        )
        departments.append(dept3)
        
        dept4 = Department.objects.create(
            name='销售部',
            code='SALES',
            description='负责销售业务'
        )
        departments.append(dept4)
        
        # 二级部门
        dept1_1 = Department.objects.create(
            name='前端组',
            parent=dept1,
            code='TECH-FRONT',
            description='前端开发组'
        )
        departments.append(dept1_1)
        
        dept1_2 = Department.objects.create(
            name='后端组',
            parent=dept1,
            code='TECH-BACK',
            description='后端开发组'
        )
        departments.append(dept1_2)
        
        return departments

    def create_users(self, departments):
        """创建用户"""
        self.stdout.write('创建用户...')
        users = []
        
        # 管理员
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            real_name='系统管理员',
            phone='13800000001',
            role='admin',
            department=departments[0],
            is_staff=True,
            is_superuser=True
        )
        users.append(admin)
        
        # 审核员
        reviewer1 = User.objects.create_user(
            username='reviewer1',
            email='reviewer1@example.com',
            password='reviewer123',
            real_name='张审核',
            phone='13800000002',
            role='reviewer',
            department=departments[1]
        )
        users.append(reviewer1)
        
        reviewer2 = User.objects.create_user(
            username='reviewer2',
            email='reviewer2@example.com',
            password='reviewer123',
            real_name='李审核',
            phone='13800000003',
            role='reviewer',
            department=departments[1]
        )
        users.append(reviewer2)
        
        # 起草人
        drafter_names = ['王起草', '赵起草', '钱起草', '孙起草', '周起草']
        for i, name in enumerate(drafter_names):
            drafter = User.objects.create_user(
                username=f'drafter{i+1}',
                email=f'drafter{i+1}@example.com',
                password='drafter123',
                real_name=name,
                phone=f'13800000{10+i:02d}',
                role='drafter',
                department=departments[i % len(departments)]
            )
            users.append(drafter)
        
        return users

    def create_templates(self, users):
        """创建模板"""
        self.stdout.write('创建模板...')
        templates = []
        
        template_data = [
            {
                'name': '采购合同模板',
                'contract_type': 'procurement',
                'industry': '制造业',
                'category': '采购',
                'content': '<p>采购合同</p><p>甲方：{甲方名称}</p><p>乙方：{乙方名称}</p><p>标的物：{标的物}</p><p>金额：{金额}</p><p>交付日期：{交付日期}</p>',
                'description': '标准采购合同模板',
                'tags': ['采购', '标准', '常用'],
                'is_public': True,
                'is_enterprise': False,
            },
            {
                'name': '销售合同模板',
                'contract_type': 'sales',
                'industry': '贸易',
                'category': '销售',
                'content': '<p>销售合同</p><p>卖方：{卖方名称}</p><p>买方：{买方名称}</p><p>商品：{商品名称}</p><p>价格：{价格}</p><p>数量：{数量}</p>',
                'description': '标准销售合同模板',
                'tags': ['销售', '标准'],
                'is_public': True,
                'is_enterprise': False,
            },
            {
                'name': '服务合同模板',
                'contract_type': 'service',
                'industry': '服务业',
                'category': '服务',
                'content': '<p>服务合同</p><p>服务提供方：{服务提供方}</p><p>服务接受方：{服务接受方}</p><p>服务内容：{服务内容}</p><p>服务期限：{服务期限}</p>',
                'description': '标准服务合同模板',
                'tags': ['服务', '标准'],
                'is_public': True,
                'is_enterprise': False,
            },
            {
                'name': '劳动合同模板',
                'contract_type': 'labor',
                'industry': '通用',
                'category': '人事',
                'content': '<p>劳动合同</p><p>用人单位：{用人单位}</p><p>劳动者：{劳动者}</p><p>工作岗位：{工作岗位}</p><p>工作地点：{工作地点}</p><p>薪资：{薪资}</p>',
                'description': '标准劳动合同模板',
                'tags': ['劳动', '人事'],
                'is_public': True,
                'is_enterprise': False,
            },
        ]
        
        for data in template_data:
            template = Template.objects.create(
                created_by=random.choice(users),
                usage_count=random.randint(0, 50),
                **data
            )
            templates.append(template)
        
        return templates

    def create_contracts(self, users, templates):
        """创建合同"""
        self.stdout.write('创建合同...')
        contracts = []
        
        contract_types = ['procurement', 'sales', 'labor', 'service']
        statuses = ['draft', 'reviewing', 'reviewed', 'approved', 'rejected', 'signed']
        industries = ['制造业', '贸易', '服务业', 'IT', '金融', '房地产']
        
        # 为每个状态创建一些合同
        for status in statuses:
            for i in range(3):
                contract_no = f'HT{timezone.now().strftime("%Y%m%d")}{random.randint(1000, 9999)}'
                contract_type = random.choice(contract_types)
                industry = random.choice(industries)
                
                contract = Contract.objects.create(
                    contract_no=contract_no,
                    title=f'{industry}{contract_type}合同-{i+1}',
                    contract_type=contract_type,
                    industry=industry,
                    status=status,
                    content={
                        'html': f'<p>这是{contract_type}合同的内容</p><p>合同编号：{contract_no}</p>',
                        'text': f'这是{contract_type}合同的内容\n合同编号：{contract_no}'
                    },
                    template=random.choice(templates) if random.random() > 0.3 else None,
                    drafter=random.choice([u for u in users if u.role == 'drafter']),
                    current_version=random.randint(1, 3),
                )
                contracts.append(contract)
        
        return contracts

    def create_contract_versions(self, contracts, users):
        """创建合同版本"""
        self.stdout.write('创建合同版本...')
        versions = []
        
        for contract in contracts[:15]:  # 只为部分合同创建版本
            for version in range(1, contract.current_version + 1):
                version_obj = ContractVersion.objects.create(
                    contract=contract,
                    version=version,
                    content={
                        'html': f'<p>这是第{version}版合同内容</p>',
                        'text': f'这是第{version}版合同内容'
                    },
                    change_summary=f'第{version}版变更说明' if version > 1 else '初始版本',
                    changed_by=random.choice(users),
                )
                versions.append(version_obj)
        
        return versions

    def create_clauses(self, contracts, users):
        """创建条款"""
        self.stdout.write('创建条款...')
        clauses = []
        
        clause_types = ['party', 'subject', 'period', 'liability', 'payment', 'other']
        clause_templates = {
            'party': {
                'title': '合同主体',
                'content': '甲方：{甲方名称}，统一社会信用代码：{代码}。乙方：{乙方名称}，统一社会信用代码：{代码}。'
            },
            'subject': {
                'title': '标的物',
                'content': '本合同标的物为{标的物名称}，规格：{规格}，数量：{数量}。'
            },
            'period': {
                'title': '履行期限',
                'content': '合同履行期限自{开始日期}至{结束日期}，共计{天数}天。'
            },
            'liability': {
                'title': '违约责任',
                'content': '如一方违约，应承担违约责任，赔偿对方因此造成的损失。'
            },
            'payment': {
                'title': '付款方式',
                'content': '付款方式：{付款方式}，付款期限：{期限}，付款金额：{金额}元。'
            },
            'other': {
                'title': '其他条款',
                'content': '其他未尽事宜，双方协商解决。'
            },
        }
        
        for contract in contracts[:20]:  # 为部分合同创建条款
            clause_count = random.randint(3, 8)
            position = 0
            
            for i in range(clause_count):
                clause_type = random.choice(clause_types)
                template = clause_templates[clause_type]
                
                clause = ContractClause.objects.create(
                    contract=contract,
                    contract_version=contract.current_version,
                    clause_no=f'第{i+1}条',
                    clause_type=clause_type,
                    clause_title=template['title'],
                    clause_content=template['content'],
                    start_position=position,
                    end_position=position + len(template['content']),
                    extracted_data={'type': clause_type},
                    confidence=Decimal(str(random.uniform(0.7, 0.99))).quantize(Decimal('0.01')),
                    is_confirmed=random.choice([True, False]),
                    confirmed_by=random.choice(users) if random.random() > 0.5 else None,
                    confirmed_at=timezone.now() - timedelta(days=random.randint(0, 30)) if random.random() > 0.5 else None,
                )
                clauses.append(clause)
                position += len(template['content']) + 100
        
        return clauses

    def create_rules(self, users):
        """创建规则"""
        self.stdout.write('创建规则...')
        rules = []
        
        rule_data = [
            {
                'rule_code': 'RULE001',
                'rule_name': '合同主体必须明确',
                'rule_type': 'general',
                'priority': 90,
                'risk_level': 'high',
                'description': '合同必须明确双方主体信息',
                'legal_basis': '《合同法》第十条',
            },
            {
                'rule_code': 'RULE002',
                'rule_name': '标的物描述必须清晰',
                'rule_type': 'general',
                'priority': 85,
                'risk_level': 'high',
                'description': '标的物必须详细描述',
                'legal_basis': '《合同法》第十二条',
            },
            {
                'rule_code': 'RULE003',
                'rule_name': '付款方式必须明确',
                'rule_type': 'general',
                'priority': 80,
                'risk_level': 'medium',
                'description': '付款方式、期限、金额必须明确',
                'legal_basis': '《合同法》第一百五十九条',
            },
            {
                'rule_code': 'RULE004',
                'rule_name': '违约责任条款必须完整',
                'rule_type': 'general',
                'priority': 75,
                'risk_level': 'medium',
                'description': '违约责任条款必须明确',
                'legal_basis': '《合同法》第一百零七条',
            },
            {
                'rule_code': 'RULE005',
                'rule_name': '制造业特殊条款检查',
                'rule_type': 'industry',
                'industry': '制造业',
                'priority': 70,
                'risk_level': 'low',
                'description': '制造业合同特殊条款检查',
            },
        ]
        
        for data in rule_data:
            rule = ReviewRule.objects.create(
                rule_content={
                    'pattern': f'{data["rule_code"]}_pattern',
                    'conditions': ['condition1', 'condition2'],
                },
                created_by=random.choice(users),
                **{k: v for k, v in data.items() if k != 'rule_content'}
            )
            rules.append(rule)
        
        return rules

    def create_review_tasks(self, contracts, users):
        """创建审核任务"""
        self.stdout.write('创建审核任务...')
        tasks = []
        
        statuses = ['pending', 'processing', 'completed', 'failed']
        task_types = ['auto', 'manual']
        
        for contract in contracts[:15]:
            task = ReviewTask.objects.create(
                contract=contract,
                contract_version=contract.current_version,
                task_type=random.choice(task_types),
                status=random.choice(statuses),
                priority=random.randint(0, 100),
                started_at=timezone.now() - timedelta(days=random.randint(0, 10)) if random.random() > 0.3 else None,
                completed_at=timezone.now() - timedelta(days=random.randint(0, 5)) if random.random() > 0.5 else None,
                created_by=random.choice(users),
            )
            tasks.append(task)
        
        return tasks

    def create_review_results(self, review_tasks, contracts):
        """创建审核结果"""
        self.stdout.write('创建审核结果...')
        results = []
        
        risk_levels = ['high', 'medium', 'low']
        
        for task in review_tasks:
            if task.status == 'completed':
                result = ReviewResult.objects.create(
                    review_task=task,
                    contract=task.contract,
                    overall_score=Decimal(str(random.uniform(60, 100))).quantize(Decimal('0.01')),
                    risk_level=random.choice(risk_levels),
                    risk_count=random.randint(0, 10),
                    summary=f'合同审核完成，发现{random.randint(0, 10)}个风险点',
                    review_data={
                        'total_clauses': random.randint(5, 15),
                        'checked_clauses': random.randint(5, 15),
                        'risks': [],
                    },
                )
                results.append(result)
        
        return results

    def create_review_opinions(self, review_results, users):
        """创建审核意见"""
        self.stdout.write('创建审核意见...')
        opinions = []
        
        opinion_types = ['risk', 'suggestion', 'warning']
        risk_levels = ['high', 'medium', 'low']
        statuses = ['pending', 'accepted', 'rejected']
        
        for result in review_results:
            opinion_count = random.randint(2, 6)
            for i in range(opinion_count):
                opinion = ReviewOpinion.objects.create(
                    review_result=result,
                    reviewer=random.choice([u for u in users if u.role == 'reviewer']),
                    clause_id=f'clause_{i+1}',
                    clause_content=f'第{i+1}条条款内容',
                    opinion_type=random.choice(opinion_types),
                    risk_level=random.choice(risk_levels),
                    opinion_content=f'审核意见{i+1}：建议修改相关条款',
                    legal_basis='《合同法》相关条款',
                    suggestion=f'建议修改建议{i+1}',
                    status=random.choice(statuses),
                )
                opinions.append(opinion)
        
        return opinions

    def create_rule_matches(self, review_tasks, rules, contracts):
        """创建规则匹配记录"""
        self.stdout.write('创建规则匹配记录...')
        matches = []
        
        for task in review_tasks[:10]:
            matched_rules = random.sample(rules, random.randint(1, 3))
            for rule in matched_rules:
                match = RuleMatch.objects.create(
                    review_task=task,
                    rule=rule,
                    contract_id=task.contract.id,
                    matched_clause=f'匹配的条款内容',
                    match_score=Decimal(str(random.uniform(0.6, 1.0))).quantize(Decimal('0.01')),
                    match_result={
                        'matched': True,
                        'details': '匹配详情',
                    },
                )
                matches.append(match)
        
        return matches

    def create_risks(self, review_results, contracts, clauses, users):
        """创建风险识别记录"""
        self.stdout.write('创建风险识别记录...')
        risks = []
        
        risk_types = ['invalid', 'missing', 'illegal', 'non_compliant']
        risk_categories = ['legality', 'compliance', 'completeness', 'financial']
        risk_levels = ['high', 'medium', 'low']
        statuses = ['pending', 'handled', 'ignored']
        
        for result in review_results:
            risk_count = random.randint(1, 5)
            for i in range(risk_count):
                risk = RiskIdentification.objects.create(
                    review_result=result,
                    contract_id=result.contract.id,
                    clause=random.choice(clauses) if clauses and random.random() > 0.5 else None,
                    risk_type=random.choice(risk_types),
                    risk_category=random.choice(risk_categories),
                    risk_level=random.choice(risk_levels),
                    risk_description=f'风险描述{i+1}：发现潜在风险点',
                    risk_location=f'第{i+1}条',
                    legal_basis='相关法律法规依据',
                    suggestion=f'处理建议{i+1}',
                    status=random.choice(statuses),
                    handled_by=random.choice(users) if random.random() > 0.5 else None,
                    handled_at=timezone.now() - timedelta(days=random.randint(0, 5)) if random.random() > 0.5 else None,
                )
                risks.append(risk)
        
        return risks

    def create_comparison_tasks(self, contracts, templates, users):
        """创建对比任务"""
        self.stdout.write('创建对比任务...')
        tasks = []
        
        task_types = ['version', 'template', 'cross_industry']
        statuses = ['pending', 'processing', 'completed', 'failed']
        
        # 版本对比
        for i in range(3):
            contract = random.choice(contracts)
            if contract.current_version > 1:
                task = ComparisonTask.objects.create(
                    task_type='version',
                    source_contract=contract,
                    target_contract=contract,
                    source_version=1,
                    target_version=contract.current_version,
                    status=random.choice(statuses),
                    result_data={'differences': []},
                    created_by=random.choice(users),
                    completed_at=timezone.now() - timedelta(days=random.randint(0, 5)) if random.random() > 0.5 else None,
                )
                tasks.append(task)
        
        # 模板对比
        for i in range(2):
            contract = random.choice(contracts)
            if contract.template:
                task = ComparisonTask.objects.create(
                    task_type='template',
                    source_contract=contract,
                    template=contract.template,
                    status=random.choice(statuses),
                    result_data={'differences': []},
                    created_by=random.choice(users),
                )
                tasks.append(task)
        
        return tasks

    def create_comparison_diffs(self, comparison_tasks):
        """创建对比差异"""
        self.stdout.write('创建对比差异...')
        diffs = []
        
        diff_types = ['added', 'deleted', 'modified']
        diff_levels = ['clause', 'field', 'risk']
        risk_levels = ['high', 'medium', 'low']
        
        for task in comparison_tasks:
            if task.status == 'completed':
                diff_count = random.randint(2, 6)
                for i in range(diff_count):
                    diff = ComparisonDiff.objects.create(
                        comparison_task=task,
                        diff_type=random.choice(diff_types),
                        diff_level=random.choice(diff_levels),
                        source_content=f'源内容{i+1}',
                        target_content=f'目标内容{i+1}',
                        clause_id=f'clause_{i+1}',
                        risk_level=random.choice(risk_levels),
                    )
                    diffs.append(diff)
        
        return diffs

    def create_knowledge_entities(self):
        """创建知识实体"""
        self.stdout.write('创建知识实体...')
        entities = []
        
        entity_data = [
            {'type': 'party', 'name': '合同主体', 'code': 'ENTITY001', 'description': '合同双方主体'},
            {'type': 'clause', 'name': '违约责任条款', 'code': 'ENTITY002', 'description': '违约责任相关条款'},
            {'type': 'regulation', 'name': '合同法', 'code': 'ENTITY003', 'description': '中华人民共和国合同法'},
            {'type': 'case', 'name': '合同纠纷案例', 'code': 'ENTITY004', 'description': '典型合同纠纷案例'},
            {'type': 'party', 'name': '付款方式', 'code': 'ENTITY005', 'description': '合同付款方式'},
            {'type': 'clause', 'name': '履行期限', 'code': 'ENTITY006', 'description': '合同履行期限条款'},
        ]
        
        for data in entity_data:
            entity = KnowledgeEntity.objects.create(
                entity_type=data['type'],
                entity_name=data['name'],
                entity_code=data['code'],
                description=data['description'],
                properties={'key': 'value'},
                source='系统生成',
            )
            entities.append(entity)
        
        return entities

    def create_knowledge_relations(self, entities):
        """创建知识关系"""
        self.stdout.write('创建知识关系...')
        relations = []
        
        relation_types = ['legal_basis', 'related_to', 'similar_to']
        
        if len(entities) >= 2:
            for i in range(min(5, len(entities) - 1)):
                relation = KnowledgeRelation.objects.create(
                    source_entity=entities[i],
                    target_entity=entities[i+1],
                    relation_type=random.choice(relation_types),
                    relation_properties={'strength': random.uniform(0.5, 1.0)},
                    confidence=Decimal(str(random.uniform(0.7, 0.99))).quantize(Decimal('0.01')),
                )
                relations.append(relation)
        
        return relations

    def create_regulations(self, entities):
        """创建法律法规"""
        self.stdout.write('创建法律法规...')
        regulations = []
        
        regulation_data = [
            {
                'title': '中华人民共和国合同法',
                'regulation_no': '法律〔1999〕第15号',
                'regulation_type': 'law',
                'content': '合同法全文内容...',
            },
            {
                'title': '合同纠纷处理办法',
                'regulation_no': '法规〔2020〕第10号',
                'regulation_type': 'regulation',
                'content': '合同纠纷处理办法内容...',
            },
        ]
        
        for data in regulation_data:
            regulation = Regulation.objects.create(
                entity=random.choice([e for e in entities if e.entity_type == 'regulation']) if any(e.entity_type == 'regulation' for e in entities) else None,
                publish_date=timezone.now().date() - timedelta(days=random.randint(100, 1000)),
                effective_date=timezone.now().date() - timedelta(days=random.randint(50, 500)),
                **data
            )
            regulations.append(regulation)
        
        return regulations

    def create_cases(self, entities):
        """创建案例"""
        self.stdout.write('创建案例...')
        cases = []
        
        case_data = [
            {
                'case_no': 'CASE001',
                'case_title': '合同违约纠纷案例',
                'case_type': '违约纠纷',
                'court': '北京市第一中级人民法院',
                'case_summary': '典型合同违约纠纷案例',
                'case_content': '案例详细内容...',
            },
            {
                'case_no': 'CASE002',
                'case_title': '合同履行纠纷案例',
                'case_type': '履行纠纷',
                'court': '上海市第一中级人民法院',
                'case_summary': '典型合同履行纠纷案例',
                'case_content': '案例详细内容...',
            },
        ]
        
        for data in case_data:
            case = Case.objects.create(
                entity=random.choice([e for e in entities if e.entity_type == 'case']) if any(e.entity_type == 'case' for e in entities) else None,
                judge_date=timezone.now().date() - timedelta(days=random.randint(100, 1000)),
                related_clauses=['clause1', 'clause2'],
                **data
            )
            cases.append(case)
        
        return cases

    def create_recommendations(self, users, contracts):
        """创建推荐记录"""
        self.stdout.write('创建推荐记录...')
        recommendations = []
        
        recommendation_types = ['clause', 'template', 'risk_response']
        contexts = ['drafting', 'modifying', 'reviewing', 'negotiating']
        
        for user in users[:5]:
            for i in range(random.randint(2, 5)):
                recommendation = Recommendation.objects.create(
                    user=user,
                    contract=random.choice(contracts) if contracts and random.random() > 0.3 else None,
                    recommendation_type=random.choice(recommendation_types),
                    recommendation_context=random.choice(contexts),
                    item_type='clause',
                    item_id=random.randint(1, 100),
                    item_content=f'推荐内容{i+1}',
                    score=Decimal(str(random.uniform(0.6, 1.0))).quantize(Decimal('0.01')),
                    reason=f'推荐理由{i+1}',
                    is_accepted=random.choice([True, False, None]),
                )
                recommendations.append(recommendation)
        
        return recommendations

    def create_user_habits(self, users):
        """创建用户习惯"""
        self.stdout.write('创建用户习惯...')
        habits = []
        
        habit_types = ['clause_preference', 'template_preference']
        
        for user in users[:5]:
            for habit_type in habit_types:
                habit = UserHabit.objects.create(
                    user=user,
                    habit_type=habit_type,
                    habit_key=f'habit_key_{habit_type}',
                    habit_value={'preference': 'value'},
                    frequency=random.randint(1, 20),
                    last_used_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                )
                habits.append(habit)
        
        return habits

    def create_audit_logs(self, users):
        """创建审计日志"""
        self.stdout.write('创建审计日志...')
        logs = []
        
        actions = ['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'LOGIN', 'LOGOUT']
        resource_types = ['Contract', 'Template', 'Review', 'User']
        statuses = ['success', 'failed']
        
        for user in users:
            for i in range(random.randint(5, 15)):
                log = AuditLog.objects.create(
                    user=user,
                    action=random.choice(actions),
                    resource_type=random.choice(resource_types),
                    resource_id=random.randint(1, 100),
                    ip_address=f'192.168.1.{random.randint(1, 255)}',
                    user_agent='Mozilla/5.0',
                    request_data={'method': 'GET', 'path': '/api/test'},
                    response_data={'status': 200},
                    status=random.choice(statuses),
                    error_message='' if random.random() > 0.1 else '错误信息',
                )
                logs.append(log)
        
        return logs



