"""
规则引擎服务模块 - 处理规则匹配和扫描
"""
import json
import re
import logging
from typing import Dict, List, Optional
from django.db.models import Q
from apps.rules.models import ReviewRule, RuleMatch
from apps.contracts.models import Contract
from apps.reviews.models import ReviewTask

logger = logging.getLogger(__name__)


class RuleEngineService:
    """规则引擎服务类 - 处理规则匹配和扫描"""
    
    def scan_contract(
        self,
        contract: Contract,
        review_task: Optional[ReviewTask] = None,
        rule_types: Optional[List[str]] = None,
        industry: Optional[str] = None
    ) -> Dict:
        """
        扫描合同并匹配规则
        
        Args:
            contract: 合同对象
            review_task: 审核任务对象（可选）
            rule_types: 规则类型列表（可选，如['general', 'industry']）
            industry: 行业（可选，用于筛选行业规则）
            
        Returns:
            Dict: 包含匹配结果的字典
        """
        try:
            # 提取合同内容
            contract_content = self._extract_contract_content(contract)
            
            # 获取适用的规则
            rules = self._get_applicable_rules(
                rule_types=rule_types,
                industry=industry or contract.industry,
                contract_type=contract.contract_type
            )
            
            # 匹配规则
            matches = []
            for rule in rules:
                match_result = self._match_rule(rule, contract_content, contract)
                if match_result['matched']:
                    matches.append({
                        'rule': rule,
                        'match_result': match_result
                    })
                    
                    # 保存匹配记录
                    if review_task:
                        RuleMatch.objects.create(
                            review_task=review_task,
                            rule=rule,
                            contract_id=contract.id,
                            matched_clause=match_result.get('matched_clause', ''),
                            match_score=match_result.get('score', 0),
                            match_result=match_result
                        )
            
            # 计算总体评分和风险等级
            overall_score, risk_level, risk_count = self._calculate_overall_metrics(matches)
            
            return {
                'success': True,
                'total_rules_scanned': len(rules),
                'total_matches': len(matches),
                'overall_score': overall_score,
                'risk_level': risk_level,
                'risk_count': risk_count,
                'matches': [
                    {
                        'rule_code': match['rule'].rule_code,
                        'rule_name': match['rule'].rule_name,
                        'rule_type': match['rule'].get_rule_type_display(),
                        'risk_level': match['rule'].get_risk_level_display() if match['rule'].risk_level else '未设置',
                        'matched_clause': match['match_result'].get('matched_clause', ''),
                        'match_score': match['match_result'].get('score', 0),
                        'suggestion': match['match_result'].get('suggestion', ''),
                        'legal_basis': match['rule'].legal_basis
                    }
                    for match in matches
                ]
            }
            
        except Exception as e:
            logger.error(f'规则引擎扫描失败: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'matches': []
            }
    
    def _get_applicable_rules(
        self,
        rule_types: Optional[List[str]] = None,
        industry: Optional[str] = None,
        contract_type: Optional[str] = None
    ) -> List[ReviewRule]:
        """获取适用的规则"""
        query = Q(is_active=True, is_deleted=False)
        
        # 规则类型过滤
        if rule_types:
            query &= Q(rule_type__in=rule_types)
        
        # 获取所有规则
        rules = ReviewRule.objects.filter(query).order_by('-priority')
        
        # 过滤行业规则
        applicable_rules = []
        for rule in rules:
            if rule.rule_type == 'general':
                # 通用规则适用于所有合同
                applicable_rules.append(rule)
            elif rule.rule_type == 'industry':
                # 行业规则需要匹配行业
                if industry and (not rule.industry or rule.industry == industry):
                    applicable_rules.append(rule)
            elif rule.rule_type == 'enterprise':
                # 企业规则需要匹配企业（这里简化处理，实际可能需要企业ID）
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def _extract_contract_content(self, contract: Contract) -> str:
        """提取合同内容为文本"""
        if contract.content:
            if isinstance(contract.content, dict):
                # 如果是字典，转换为文本
                return json.dumps(contract.content, ensure_ascii=False, indent=2)
            elif isinstance(contract.content, str):
                return contract.content
        
        # 如果有文件路径，可以读取文件（这里简化处理）
        if contract.file_path:
            # TODO: 实现文件内容读取
            pass
        
        return contract.title or ""
    
    def _match_rule(self, rule: ReviewRule, contract_content: str, contract: Contract) -> Dict:
        """
        匹配单个规则
        
        Args:
            rule: 规则对象
            contract_content: 合同内容文本
            contract: 合同对象
            
        Returns:
            Dict: 匹配结果
        """
        try:
            rule_content = rule.rule_content
            if isinstance(rule_content, str):
                rule_content = json.loads(rule_content)
            
            # 规则内容结构示例：
            # {
            #   "type": "keyword",  # keyword/regex/pattern
            #   "patterns": ["关键词1", "关键词2"],
            #   "conditions": {...},
            #   "action": "warning"  # warning/error/suggestion
            # }
            
            rule_type = rule_content.get('type', 'keyword')
            patterns = rule_content.get('patterns', [])
            conditions = rule_content.get('conditions', {})
            action = rule_content.get('action', 'warning')
            
            matched = False
            matched_clause = ""
            score = 0.0
            suggestion = ""
            
            if rule_type == 'keyword':
                # 关键词匹配
                for pattern in patterns:
                    if pattern.lower() in contract_content.lower():
                        matched = True
                        # 查找匹配的条款
                        matched_clause = self._find_matched_clause(pattern, contract_content)
                        score = 0.8  # 关键词匹配默认分数
                        suggestion = rule.description or f"发现关键词：{pattern}"
                        break
            
            elif rule_type == 'regex':
                # 正则表达式匹配
                for pattern in patterns:
                    try:
                        matches = re.finditer(pattern, contract_content, re.IGNORECASE)
                        if matches:
                            matched = True
                            matched_clause = self._find_matched_clause(pattern, contract_content)
                            score = 0.9  # 正则匹配分数更高
                            suggestion = rule.description or f"匹配到模式：{pattern}"
                            break
                    except re.error:
                        logger.warning(f'无效的正则表达式: {pattern}')
                        continue
            
            elif rule_type == 'pattern':
                # 模式匹配（更复杂的匹配逻辑）
                matched, matched_clause, score = self._pattern_match(
                    rule_content, contract_content
                )
                if matched:
                    suggestion = rule.description or "发现匹配模式"
            
            # 应用条件过滤
            if matched and conditions:
                matched = self._check_conditions(conditions, contract, contract_content)
            
            return {
                'matched': matched,
                'matched_clause': matched_clause,
                'score': score,
                'suggestion': suggestion,
                'action': action
            }
            
        except Exception as e:
            logger.error(f'规则匹配失败: {str(e)}')
            return {
                'matched': False,
                'matched_clause': '',
                'score': 0.0,
                'suggestion': '',
                'action': 'warning'
            }
    
    def _find_matched_clause(self, pattern: str, content: str, context_lines: int = 3) -> str:
        """查找匹配的条款上下文"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if pattern.lower() in line.lower():
                # 返回匹配行及其上下文
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                return '\n'.join(lines[start:end])
        return ""
    
    def _pattern_match(self, rule_content: Dict, contract_content: str) -> tuple:
        """模式匹配（更复杂的匹配逻辑）"""
        # 这里可以实现更复杂的模式匹配逻辑
        # 例如：检查合同结构、条款完整性等
        return False, "", 0.0
    
    def _check_conditions(self, conditions: Dict, contract: Contract, content: str) -> bool:
        """检查条件是否满足"""
        # 这里可以实现条件检查逻辑
        # 例如：检查合同类型、金额范围等
        return True
    
    def _calculate_overall_metrics(self, matches: List[Dict]) -> tuple:
        """计算总体评分和风险等级"""
        if not matches:
            return 100.0, 'low', 0
        
        # 计算平均分数
        total_score = sum(match['match_result'].get('score', 0) for match in matches)
        avg_score = total_score / len(matches) if matches else 0
        
        # 计算风险等级
        high_risk_count = sum(
            1 for match in matches
            if match['rule'].risk_level == 'high'
        )
        medium_risk_count = sum(
            1 for match in matches
            if match['rule'].risk_level == 'medium'
        )
        
        if high_risk_count > 0:
            risk_level = 'high'
        elif medium_risk_count > 0:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # 总体评分（100 - 匹配分数 * 权重）
        overall_score = max(0, 100 - avg_score * 20)
        
        return overall_score, risk_level, len(matches)

