"""
合同服务模块 - 包含AI合同生成等功能
"""
import json
import logging
from typing import Dict, Optional
from django.conf import settings
from apps.contracts.models import Contract, Template
from apps.reviews.services import AIService

logger = logging.getLogger(__name__)


class ContractService:
    """合同服务类 - 处理合同相关业务逻辑"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def generate_contract_content(
        self,
        contract_type: str,
        industry: str = '',
        template: Optional[Template] = None,
        basic_info: Optional[Dict] = None
    ) -> Dict:
        """
        使用AI生成合同初步内容
        
        Args:
            contract_type: 合同类型
            industry: 所属行业
            template: 合同模板（可选）
            basic_info: 基本信息字典，包含合同的关键信息
            
        Returns:
            Dict: 包含生成的合同内容的字典
        """
        try:
            # 构建AI提示词
            prompt = self._build_generation_prompt(
                contract_type=contract_type,
                industry=industry,
                template=template,
                basic_info=basic_info or {}
            )
            
            # 调用AI接口生成合同内容
            if not self.ai_service.enabled or not self.ai_service.model:
                error_msg = 'AI服务未启用或未配置模型，无法生成合同内容。请管理员在AI模型配置中启用AI服务并配置正确的模型。'
                logger.error(error_msg)
                raise Exception(error_msg)
            
            try:
                # 直接调用AI API，不使用_call_ai_api（因为那是审核建议的格式）
                ai_response = self._call_ai_api_for_generation(prompt)
                
                # 验证AI返回的内容
                if not ai_response or not ai_response.strip():
                    error_msg = 'AI返回内容为空，无法生成合同内容。请检查AI模型配置或重试。'
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                generated_content = {'text': ai_response.strip()}
                
            except Exception as e:
                logger.error(f'AI调用失败: {str(e)}')
                raise Exception(f'AI合同生成失败: {str(e)}。请检查AI模型配置和网络连接。')
            
            return {
                'success': True,
                'content': generated_content,
                'message': '合同内容生成成功'
            }
            
        except Exception as e:
            logger.error(f'AI合同生成失败: {str(e)}')
            # 失败时抛出异常，不再使用模拟内容
            raise Exception(f'AI合同生成失败: {str(e)}。请检查AI模型配置和网络连接。')
    
    def _build_generation_prompt(
        self,
        contract_type: str,
        industry: str = '',
        template: Optional[Template] = None,
        basic_info: Optional[Dict] = None
    ) -> str:
        """构建AI生成合同的提示词"""
        
        prompt_parts = []
        
        # 系统角色
        prompt_parts.append("你是一位资深的合同起草专家，具有丰富的法律知识和合同起草经验，擅长根据提供的信息生成详细、规范、完整的合同内容。")
        
        # 合同类型和行业信息
        contract_type_map = {
            'procurement': '采购合同',
            'sales': '销售合同',
            'labor': '劳动合同',
            'service': '服务合同',
        }
        contract_type_name = contract_type_map.get(contract_type, contract_type)
        prompt_parts.append(f"\n【合同类型】{contract_type_name}")
        
        if industry:
            prompt_parts.append(f"【所属行业】{industry}")
        
        # 如果有模板，提供模板内容作为参考
        if template:
            prompt_parts.append(f"\n【参考模板】{template.name}")
            # 提供完整的模板内容作为参考
            prompt_parts.append(f"模板内容结构参考：\n{template.content}")
        
        # 基本信息
        if basic_info:
            prompt_parts.append("\n【合同基本信息】")
            info_mapping = {
                'party_a': '甲方（采购方/销售方/委托方/用人单位）',
                'party_b': '乙方（供应方/购买方/服务方/劳动者）',
                'subject': '标的物/服务内容/工作内容',
                'amount': '合同金额/工资标准',
                'delivery_location': '交付地点',
                'delivery_time': '交付时间',
                'payment_method': '付款方式',
                'payment_time': '付款时间',
            }
            for key, value in basic_info.items():
                if value:
                    label = info_mapping.get(key, key)
                    prompt_parts.append(f"- {label}：{value}")
        
        # 详细的生成要求
        prompt_parts.append("\n【生成要求】")
        prompt_parts.append("请根据以上信息生成一份详细、完整、规范、专业的合同内容，具体要求如下：")
        prompt_parts.append("\n1. 合同结构要求（必须严格遵守）：")
        prompt_parts.append("   - 合同标题：必须明确标注合同类型，格式为'[合同类型]合同'，如'采购合同'、'销售合同'等")
        prompt_parts.append("   - 合同编号：必须包含合同编号占位符，格式为'合同编号：___________'")
        prompt_parts.append("   - 合同双方信息：必须包含完整的双方信息，格式如下：")
        prompt_parts.append("     * 甲方信息：名称、地址（详细地址）、法定代表人、联系电话、开户银行、银行账号")
        prompt_parts.append("     * 乙方信息：名称、地址（详细地址）、法定代表人、联系电话、开户银行、银行账号")
        prompt_parts.append("   - 合同前言：必须包含标准的合同前言，格式为：")
        prompt_parts.append("     '根据《中华人民共和国合同法》、《中华人民共和国民法典》等相关法律法规的规定，")
        prompt_parts.append("     甲乙双方在平等、自愿、公平、诚实信用的基础上，就[合同事项]事宜，经友好协商，达成如下协议：'")
        prompt_parts.append("   - 合同条款：必须使用'第一条'、'第二条'等标准编号格式")
        prompt_parts.append("   - 合同结尾：必须包含双方签字盖章部分和签订日期")
        
        # 根据合同类型提供具体的条款要求
        if contract_type == 'procurement':
            prompt_parts.append("\n2. 必须包含以下详细条款：")
            prompt_parts.append("   - 第一条：合同标的（货物名称、规格、数量、单价、总金额、质量标准等，要详细具体）")
            prompt_parts.append("   - 第二条：交货方式（交货地点、交货时间、交货方式、运输方式、包装要求等）")
            prompt_parts.append("   - 第三条：验收标准及方法（验收标准、验收方法、验收期限、验收异议处理等）")
            prompt_parts.append("   - 第四条：付款方式（付款方式、付款时间、付款条件、发票要求等，要具体到百分比和时间）")
            prompt_parts.append("   - 第五条：质量保证（质保期限、质保范围、质保责任等）")
            prompt_parts.append("   - 第六条：违约责任（甲方违约责任、乙方违约责任，要具体到违约金比例）")
            prompt_parts.append("   - 第七条：知识产权条款")
            prompt_parts.append("   - 第八条：保密条款（保密期限、保密范围等）")
            prompt_parts.append("   - 第九条：争议解决（协商、诉讼等）")
            prompt_parts.append("   - 第十条：其他约定（补充协议、合同生效、合同份数等）")
        elif contract_type == 'sales':
            prompt_parts.append("\n2. 必须包含以下详细条款：")
            prompt_parts.append("   - 第一条：合同标的（货物名称、规格型号、数量、单价、总金额、质量标准、产地等）")
            prompt_parts.append("   - 第二条：交货方式（交货地点、交货时间、交货方式、运输方式、费用承担、包装标准等）")
            prompt_parts.append("   - 第三条：验收标准及方法（验收标准、验收方法、验收期限、验收合格确认等）")
            prompt_parts.append("   - 第四条：付款方式（付款方式、付款时间、付款条件、发票要求等）")
            prompt_parts.append("   - 第五条：质量保证（质保期限、质保内容、质保责任等）")
            prompt_parts.append("   - 第六条：违约责任（甲方违约责任、乙方违约责任，要具体到违约金比例）")
            prompt_parts.append("   - 第七条：知识产权条款")
            prompt_parts.append("   - 第八条：争议解决")
            prompt_parts.append("   - 第九条：其他约定")
        elif contract_type == 'service':
            prompt_parts.append("\n2. 必须包含以下详细条款：")
            prompt_parts.append("   - 第一条：服务内容（服务项目、服务范围、服务标准、服务期限、服务地点等）")
            prompt_parts.append("   - 第二条：服务要求（服务标准、人员要求、质量管理、进度报告等）")
            prompt_parts.append("   - 第三条：服务费用（费用总额、费用构成、付款方式、付款时间、发票要求等）")
            prompt_parts.append("   - 第四条：验收标准（验收标准、验收方法、验收期限、验收合格确认等）")
            prompt_parts.append("   - 第五条：知识产权（知识产权归属、侵权责任等）")
            prompt_parts.append("   - 第六条：保密条款（保密义务、保密期限、保密范围等）")
            prompt_parts.append("   - 第七条：违约责任（甲方违约责任、乙方违约责任，要具体到违约金比例）")
            prompt_parts.append("   - 第八条：合同变更和解除")
            prompt_parts.append("   - 第九条：争议解决")
            prompt_parts.append("   - 第十条：其他约定")
        elif contract_type == 'labor':
            prompt_parts.append("\n2. 必须包含以下详细条款：")
            prompt_parts.append("   - 第一条：合同期限（合同期限类型、固定期限、试用期等）")
            prompt_parts.append("   - 第二条：工作内容和工作地点（工作岗位、工作内容、工作地点、岗位调整等）")
            prompt_parts.append("   - 第三条：工作时间和休息休假（工时制、工作时间、休息休假、带薪年休假等）")
            prompt_parts.append("   - 第四条：劳动报酬（工资标准、工资构成、工资支付方式、试用期工资等）")
            prompt_parts.append("   - 第五条：社会保险和福利待遇（五险一金、其他福利等）")
            prompt_parts.append("   - 第六条：劳动保护和劳动条件")
            prompt_parts.append("   - 第七条：保密和竞业限制（保密义务、竞业限制、补偿金等）")
            prompt_parts.append("   - 第八条：合同的变更、解除和终止")
            prompt_parts.append("   - 第九条：违约责任")
            prompt_parts.append("   - 第十条：争议解决（协商、仲裁、诉讼等）")
            prompt_parts.append("   - 第十一条：其他约定")
        
        prompt_parts.append("\n3. 内容详细程度要求（非常重要）：")
        prompt_parts.append("   - 每个条款都必须详细具体，不能只是简单的一句话或概括性描述")
        prompt_parts.append("   - 必须包含具体的数字、时间、比例、金额等可执行的内容")
        prompt_parts.append("   - 必须包含多种选择项（用□标记），让用户可以根据实际情况选择，例如：")
        prompt_parts.append("     '□ 一次性付款  □ 分期付款  □ 其他：___________'")
        prompt_parts.append("   - 必须包含占位符（用下划线___________标记），让用户填写具体信息")
        prompt_parts.append("   - 违约责任必须具体到违约金的比例和计算方式，例如：")
        prompt_parts.append("     '每逾期一日，应向对方支付逾期金额的0.5‰（千分之零点五）作为违约金'")
        prompt_parts.append("   - 付款方式必须具体到付款比例和时间节点，例如：")
        prompt_parts.append("     '合同签订后3个工作日内支付合同总金额的30%作为预付款；")
        prompt_parts.append("     货物验收合格后5个工作日内支付合同总金额的65%；")
        prompt_parts.append("     质保期满后10个工作日内支付合同总金额的5%作为质保金'")
        prompt_parts.append("   - 时间要求必须具体到'工作日'或'自然日'，例如：'3个工作日内'、'5个自然日内'")
        prompt_parts.append("   - 金额必须同时标注数字和大写，例如：'人民币100,000元（大写：拾万元整）'")
        prompt_parts.append("   - 每个条款的子条款必须使用'1.1'、'1.2'、'2.1'等格式编号")
        
        prompt_parts.append("\n4. 语言和格式要求（必须严格遵守）：")
        prompt_parts.append("   - 使用规范的合同法律语言，表述清晰、准确、严谨、无歧义")
        prompt_parts.append("   - 必须符合《中华人民共和国合同法》、《中华人民共和国民法典》等相关法律法规的规定")
        prompt_parts.append("   - 根据行业特点，使用相应的专业术语和行业规范")
        prompt_parts.append("   - 格式规范，层次清晰，使用标准的合同格式和排版")
        prompt_parts.append("   - 避免使用口语化、模糊性、歧义性的表述")
        prompt_parts.append("   - 使用'应'、'必须'、'不得'等法律规范用语，不使用'可以'、'建议'等非强制性用语")
        prompt_parts.append("   - 金额、时间、数量等关键信息必须明确，不得使用'约'、'左右'、'大概'等模糊词汇")
        
        if template:
            prompt_parts.append("\n5. 参考模板要求：")
            prompt_parts.append("   - 参考提供的模板格式和结构")
            prompt_parts.append("   - 根据提供的基本信息，将模板中的占位符替换为具体信息")
            prompt_parts.append("   - 保持模板的详细程度和完整性")
        
        prompt_parts.append("\n【输出要求】")
        prompt_parts.append("1. 请直接返回完整的合同正文内容，不需要额外的说明文字、注释或解释")
        prompt_parts.append("2. 合同内容必须详细、完整、专业、可直接使用")
        prompt_parts.append("3. 合同内容必须包含所有必要的条款，不得遗漏关键条款")
        prompt_parts.append("4. 合同内容必须符合实际业务需求，具有可操作性")
        prompt_parts.append("5. 如果提供了模板，必须参考模板的结构和详细程度，但要根据提供的基本信息进行个性化定制")
        prompt_parts.append("6. 合同内容长度应该足够详细，一般不少于2000字，确保每个条款都有充分的说明")
        prompt_parts.append("7. 输出格式：纯文本格式，使用换行符分隔段落，保持清晰的层次结构")
        
        return "\n".join(prompt_parts)
    
    def _call_ai_api_for_generation(self, prompt: str) -> str:
        """调用AI API生成合同内容（返回纯文本）"""
        try:
            import requests
        except ImportError:
            logger.error('requests模块未安装，无法调用AI API')
            return None
        
        if not self.ai_service.enabled or not self.ai_service.api_key:
            error_msg = 'AI服务未启用或未配置API密钥，无法生成合同内容'
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # 构建请求数据
            messages = [
                {"role": "system", "content": "你是一位专业的合同起草专家，擅长根据提供的信息生成规范的合同内容。"},
                {"role": "user", "content": prompt}
            ]
            
            headers = {
                'Authorization': f'Bearer {self.ai_service.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.ai_service.model,
                'messages': messages,
                'temperature': self.ai_service.temperature,
                'max_tokens': self.ai_service.max_tokens
            }
            
            # 发送请求
            # AI生成合同需要更长时间，临时增加超时时间到240秒（4分钟）
            original_timeout = self.ai_service.timeout
            generation_timeout = max(self.ai_service.timeout, 240)  # 至少240秒（4分钟）
            
            response = requests.post(
                self.ai_service.api_url,
                headers=headers,
                json=data,
                timeout=generation_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析响应（兼容不同API格式）
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return content.strip() if content else None
                else:
                    logger.error('API响应格式错误')
                    return None
            else:
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
    
    def _generate_mock_content(
        self,
        contract_type: str,
        industry: str = '',
        template: Optional[Template] = None,
        basic_info: Optional[Dict] = None
    ) -> Dict:
        """生成模拟合同内容（当AI不可用时）"""
        
        # 如果有模板，使用模板内容
        if template:
            return {
                'text': template.content,
                'html': template.content.replace('\n', '<br>'),
                'source': 'template'
            }
        
        # 否则生成详细的基础模板
        contract_type_map = {
            'procurement': '采购合同',
            'sales': '销售合同',
            'labor': '劳动合同',
            'service': '服务合同',
        }
        contract_type_name = contract_type_map.get(contract_type, '合同')
        
        # 提取基本信息
        party_a = basic_info.get('party_a', '_________________________') if basic_info else '_________________________'
        party_b = basic_info.get('party_b', '_________________________') if basic_info else '_________________________'
        subject = basic_info.get('subject', '_________________________') if basic_info else '_________________________'
        amount = basic_info.get('amount', '_________________________') if basic_info else '_________________________'
        delivery_location = basic_info.get('delivery_location', '_________________________') if basic_info else '_________________________'
        delivery_time = basic_info.get('delivery_time', '_________________________') if basic_info else '_________________________'
        payment_method = basic_info.get('payment_method', '_________________________') if basic_info else '_________________________'
        payment_time = basic_info.get('payment_time', '_________________________') if basic_info else '_________________________'
        
        if contract_type == 'procurement':
            mock_content = f'''采购合同

合同编号：___________

甲方（采购方）：{party_a}
地址：___________________________________
法定代表人：_____________________________
联系电话：_____________________________
开户银行：_____________________________
银行账号：_____________________________

乙方（供应方）：{party_b}
地址：___________________________________
法定代表人：_____________________________
联系电话：_____________________________
开户银行：_____________________________
银行账号：_____________________________

根据《中华人民共和国合同法》及相关法律法规的规定，甲乙双方在平等、自愿、公平、诚实信用的基础上，就甲方向乙方采购货物事宜，经友好协商，达成如下协议：

第一条 合同标的
1.1 货物名称：{subject}
1.2 货物规格：_________________________
1.3 货物数量：_________________________
1.4 货物单价：人民币___________元/单位
1.5 合同总金额：人民币{amount}元（大写：_________________________）
1.6 货物质量标准：符合国家相关标准及行业标准，具体标准为：_________________________

第二条 交货方式
2.1 交货地点：{delivery_location}
2.2 交货时间：{delivery_time}
2.3 交货方式：□ 乙方送货上门  □ 甲方自提  □ 第三方物流
2.4 运输方式及费用：_________________________
2.5 包装要求：_________________________

第三条 验收标准及方法
3.1 验收标准：按照本合同第一条约定的质量标准进行验收
3.2 验收方法：_________________________
3.3 验收期限：货物到达交货地点后___________个工作日内完成验收
3.4 验收异议：如甲方对货物质量有异议，应在验收期限内书面通知乙方，乙方应在收到通知后___________个工作日内予以处理

第四条 付款方式
4.1 付款方式：□ 一次性付款  □ 分期付款  □ 其他：_________________________
4.2 付款时间：
    □ 合同签订后___________个工作日内支付合同总金额的___________%
    □ 货物验收合格后___________个工作日内支付合同总金额的___________%
    □ 质保期满后___________个工作日内支付合同总金额的___________%
4.3 付款方式：□ 银行转账  □ 支票  □ 其他：_________________________
4.4 发票要求：乙方应在收到款项后___________个工作日内向甲方开具合法有效的增值税专用发票

第五条 质量保证
5.1 质保期限：自货物验收合格之日起___________个月
5.2 质保范围：在质保期内，如货物出现质量问题，乙方应负责免费维修、更换或退货
5.3 质保责任：因乙方原因导致货物质量问题，给甲方造成损失的，乙方应承担相应的赔偿责任

第六条 违约责任
6.1 甲方违约责任：
    （1）如甲方未按合同约定支付款项，每逾期一日，应向乙方支付逾期付款金额的___________‰作为违约金
    （2）如甲方无正当理由拒绝接收货物，应向乙方支付合同总金额的___________%作为违约金
6.2 乙方违约责任：
    （1）如乙方未按合同约定时间交货，每逾期一日，应向甲方支付合同总金额的___________‰作为违约金
    （2）如乙方交付的货物不符合合同约定的质量标准，甲方有权要求乙方免费更换、退货或减少价款
    （3）如乙方交付的货物存在严重质量问题，甲方有权解除合同，并要求乙方支付合同总金额的___________%作为违约金
6.3 因不可抗力导致合同无法履行的，双方互不承担违约责任

第七条 知识产权
7.1 乙方保证所供货物不侵犯任何第三方的知识产权
7.2 如因乙方提供的货物侵犯第三方知识产权，给甲方造成损失的，乙方应承担全部责任

第八条 保密条款
8.1 双方应对在合同履行过程中知悉的对方商业秘密和技术秘密承担保密义务
8.2 保密期限：自合同签订之日起至合同终止后___________年

第九条 争议解决
9.1 因本合同引起的争议，双方应友好协商解决
9.2 协商不成的，任何一方均可向合同签订地人民法院提起诉讼
9.3 合同签订地：_________________________

第十条 其他约定
10.1 本合同未尽事宜，双方可另行签订补充协议，补充协议与本合同具有同等法律效力
10.2 本合同自双方签字盖章之日起生效
10.3 本合同一式___________份，甲乙双方各执___________份，具有同等法律效力

甲方（盖章）：                   乙方（盖章）：
法定代表人（签字）：             法定代表人（签字）：
委托代理人（签字）：             委托代理人（签字）：
签订日期：________年____月____日  签订日期：________年____月____日'''
        else:
            # 其他类型的简化版本
            mock_content = f'''{contract_type_name}

合同编号：___________

甲方：{party_a}
地址：___________________________________
法定代表人：_____________________________
联系电话：_____________________________

乙方：{party_b}
地址：___________________________________
法定代表人：_____________________________
联系电话：_____________________________

根据《中华人民共和国合同法》及相关法律法规的规定，甲乙双方在平等、自愿、公平、诚实信用的基础上，经友好协商，达成如下协议：

第一条 合同标的
1.1 标的物/服务内容：{subject}
1.2 数量/范围：_________________________
1.3 合同金额：{amount}

第二条 交付/履行方式
2.1 交付/履行地点：{delivery_location}
2.2 交付/履行时间：{delivery_time}
2.3 交付/履行方式：_________________________

第三条 付款方式
3.1 付款方式：{payment_method}
3.2 付款时间：{payment_time}
3.3 发票要求：_________________________

第四条 质量保证
4.1 质保期限：_________________________
4.2 质保范围：_________________________

第五条 违约责任
5.1 任何一方违反本合同约定，应承担相应的违约责任
5.2 具体违约责任按照相关法律法规执行

第六条 争议解决
6.1 因本合同引起的争议，双方应友好协商解决
6.2 协商不成的，提交有管辖权的人民法院解决

第七条 其他约定
7.1 本合同自双方签字盖章之日起生效
7.2 本合同一式___________份，甲乙双方各执___________份

甲方（盖章）：                   乙方（盖章）：
法定代表人（签字）：             法定代表人（签字）：
签订日期：________年____月____日  签订日期：________年____月____日'''
        
        return {
            'text': mock_content.strip(),
            'html': mock_content.strip().replace('\n', '<br>'),
            'source': 'generated'
        }

