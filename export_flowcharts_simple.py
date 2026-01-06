"""
简化版：使用playwright将流程图导出为PNG
安装: pip install playwright
然后运行: playwright install chromium
"""
import os
import asyncio
from playwright.async_api import async_playwright

async def export_flowchart(html_file, output_file):
    """使用Playwright导出流程图"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 获取HTML文件的绝对路径
        html_path = os.path.abspath(html_file)
        file_url = f'file:///{html_path}'
        
        await page.goto(file_url)
        await page.wait_for_timeout(2000)  # 等待页面加载
        
        # 截图
        await page.screenshot(path=output_file, full_page=True)
        
        await browser.close()
        print(f'✓ 成功导出: {output_file}')

async def main():
    html_file = '合同流程图.html'
    
    if not os.path.exists(html_file):
        print(f'错误: 找不到文件 {html_file}')
        return
    
    print('开始导出流程图...')
    
    # 读取HTML内容
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建合同起草流程图的HTML
    draft_html = content.split('<h2>二、合同审核流程图</h2>')[0]
    draft_html = draft_html.replace(
        '<h1>AI智能合同审核系统 - 流程图</h1>',
        '<h1>合同起草流程图</h1>'
    )
    draft_html += '</body></html>'
    
    draft_file = 'temp_draft.html'
    with open(draft_file, 'w', encoding='utf-8') as f:
        f.write(draft_html)
    
    # 创建合同审核流程图的HTML
    review_html = '<!DOCTYPE html><html lang="zh-CN"><head>' + content.split('</head>')[1]
    review_html = review_html.split('<h2>一、合同起草流程图</h2>')[0] + '<h2>合同审核流程图</h2>' + review_html.split('<h2>二、合同审核流程图</h2>')[1]
    review_html = review_html.replace(
        '<h1>AI智能合同审核系统 - 流程图</h1>',
        '<h1>合同审核流程图</h1>'
    )
    
    review_file = 'temp_review.html'
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write(review_html)
    
    # 导出两个流程图
    await export_flowchart(draft_file, '合同流程图_合同起草流程图.png')
    await export_flowchart(review_file, '合同流程图_合同审核流程图.png')
    
    # 清理临时文件
    if os.path.exists(draft_file):
        os.remove(draft_file)
    if os.path.exists(review_file):
        os.remove(review_file)
    
    print('\n✓ 所有流程图导出成功！')

if __name__ == '__main__':
    asyncio.run(main())

