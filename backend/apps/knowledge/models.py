from django.db import models


class KnowledgeEntity(models.Model):
    """知识实体表"""
    ENTITY_TYPE_CHOICES = [
        ('party', '合同主体'),
        ('clause', '条款'),
        ('regulation', '法规'),
        ('case', '案例'),
    ]
    
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES, verbose_name='实体类型')
    entity_name = models.CharField(max_length=500, verbose_name='实体名称')
    entity_code = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name='实体编码')
    description = models.TextField(blank=True, verbose_name='实体描述')
    properties = models.JSONField(null=True, blank=True, verbose_name='实体属性')
    source = models.CharField(max_length=200, blank=True, verbose_name='数据来源')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'knowledge_knowledge_entity'
        verbose_name = '知识实体'
        verbose_name_plural = '知识实体'
        ordering = ['entity_type', 'entity_name']

    def __str__(self):
        return f'{self.get_entity_type_display()} - {self.entity_name}'


class KnowledgeRelation(models.Model):
    """知识关系表"""
    RELATION_TYPE_CHOICES = [
        ('legal_basis', '法律依据'),
        ('related_to', '相关于'),
        ('similar_to', '类似于'),
    ]
    
    source_entity = models.ForeignKey(KnowledgeEntity, on_delete=models.CASCADE, related_name='outgoing_relations', verbose_name='源实体')
    target_entity = models.ForeignKey(KnowledgeEntity, on_delete=models.CASCADE, related_name='incoming_relations', verbose_name='目标实体')
    relation_type = models.CharField(max_length=50, choices=RELATION_TYPE_CHOICES, verbose_name='关系类型')
    relation_properties = models.JSONField(null=True, blank=True, verbose_name='关系属性')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='关系置信度')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'knowledge_knowledge_relation'
        verbose_name = '知识关系'
        verbose_name_plural = '知识关系'
        unique_together = [['source_entity', 'target_entity', 'relation_type']]

    def __str__(self):
        return f'{self.source_entity.entity_name} - {self.get_relation_type_display()} - {self.target_entity.entity_name}'


class Regulation(models.Model):
    """法律法规表"""
    REGULATION_TYPE_CHOICES = [
        ('law', '法律'),
        ('regulation', '法规'),
        ('standard', '标准'),
    ]
    
    title = models.CharField(max_length=500, verbose_name='法规标题')
    regulation_no = models.CharField(max_length=100, blank=True, verbose_name='法规编号')
    regulation_type = models.CharField(max_length=50, choices=REGULATION_TYPE_CHOICES, blank=True, verbose_name='法规类型')
    publish_date = models.DateField(null=True, blank=True, verbose_name='发布日期')
    effective_date = models.DateField(null=True, blank=True, verbose_name='生效日期')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='失效日期')
    content = models.TextField(blank=True, verbose_name='法规内容')
    source_url = models.URLField(max_length=500, blank=True, verbose_name='来源URL')
    entity = models.ForeignKey(KnowledgeEntity, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联实体')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'knowledge_regulation'
        verbose_name = '法律法规'
        verbose_name_plural = '法律法规'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title


class Case(models.Model):
    """案例库表"""
    case_no = models.CharField(max_length=100, blank=True, verbose_name='案例编号')
    case_title = models.CharField(max_length=500, verbose_name='案例标题')
    case_type = models.CharField(max_length=50, blank=True, verbose_name='案例类型')
    court = models.CharField(max_length=200, blank=True, verbose_name='审理法院')
    judge_date = models.DateField(null=True, blank=True, verbose_name='判决日期')
    case_summary = models.TextField(blank=True, verbose_name='案例摘要')
    case_content = models.TextField(blank=True, verbose_name='案例内容')
    related_clauses = models.JSONField(null=True, blank=True, verbose_name='相关条款')
    entity = models.ForeignKey(KnowledgeEntity, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联实体')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'knowledge_case'
        verbose_name = '案例'
        verbose_name_plural = '案例'
        ordering = ['-judge_date']

    def __str__(self):
        return self.case_title

