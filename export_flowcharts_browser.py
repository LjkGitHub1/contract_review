"""
使用浏览器自动化导出流程图（最简单的方法）
如果playwright不可用，会提示手动方法
"""
import os
import sys

def check_and_install_playwright():
    """检查并提示安装playwright"""
    try:
        import playwright
        return True
    except ImportError:
        print("=" * 60)
        print("需要安装playwright库")
        print("=" * 60)
        print("请运行以下命令安装：")
        print("  pip install playwright")
        print("  playwright install chromium")
        print("=" * 60)
        return False

def export_with_playwright():
    """使用playwright导出"""
    import asyncio
    from playwright.async_api import async_playwright
    
    async def export():
        html_file = '合同流程图.html'
        
        if not os.path.exists(html_file):
            print(f'错误: 找不到文件 {html_file}')
            return
        
        print('正在导出流程图...')
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            html_path = os.path.abspath(html_file).replace('\\', '/')
            file_url = f'file:///{html_path}'
            
            await page.goto(file_url)
            await page.wait_for_timeout(3000)
            
            # 读取HTML内容并分割
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建合同起草流程图HTML
            draft_content = content.split('<h2>二、合同审核流程图</h2>')[0]
            draft_content = draft_content.replace(
                '<h1>AI智能合同审核系统 - 流程图</h1>',
                '<h1>合同起草流程图</h1>'
            )
            if not draft_content.strip().endswith('</body></html>'):
                draft_content += '</body></html>'
            
            draft_file = 'temp_draft.html'
            with open(draft_file, 'w', encoding='utf-8') as f:
                f.write(draft_content)
            
            # 创建合同审核流程图HTML
            review_parts = content.split('<h2>二、合同审核流程图</h2>')
            if len(review_parts) > 1:
                review_content = content.split('</head>')[0] + '</head><body>' + review_parts[1]
                review_content = review_content.replace(
                    '<h1>AI智能合同审核系统 - 流程图</h1>',
                    '<h1>合同审核流程图</h1>'
                )
                
                review_file = 'temp_review.html'
                with open(review_file, 'w', encoding='utf-8') as f:
                    f.write(review_content)
                
                # 导出两个流程图
                draft_path = os.path.abspath(draft_file).replace('\\', '/')
                review_path = os.path.abspath(review_file).replace('\\', '/')
                
                await page.goto(f'file:///{draft_path}')
                await page.wait_for_timeout(2000)
                await page.screenshot(path='合同流程图_合同起草流程图.png', full_page=True)
                print('✓ 已导出: 合同流程图_合同起草流程图.png')
                
                await page.goto(f'file:///{review_path}')
                await page.wait_for_timeout(2000)
                await page.screenshot(path='合同流程图_合同审核流程图.png', full_page=True)
                print('✓ 已导出: 合同流程图_合同审核流程图.png')
                
                # 清理临时文件
                os.remove(draft_file)
                os.remove(review_file)
            
            await browser.close()
            print('\n✓ 所有流程图导出成功！')
    
    asyncio.run(export())

def main():
    print("=" * 60)
    print("合同流程图导出工具")
    print("=" * 60)
    
    if not check_and_install_playwright():
        print("\n或者，您可以使用以下手动方法：")
        print("1. 在浏览器中打开 合同流程图.html")
        print("2. 使用截图工具（如Windows的Snipping Tool）截图")
        print("3. 分别截图两个流程图部分")
        print("4. 保存为PNG格式")
        return
    
    try:
        export_with_playwright()
    except Exception as e:
        print(f'\n导出失败: {str(e)}')
        print('\n请使用手动方法：')
        print('1. 在浏览器中打开 合同流程图.html')
        print('2. 使用截图工具截图两个流程图')
        print('3. 保存为PNG格式')

if __name__ == '__main__':
    main()

