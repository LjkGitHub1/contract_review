"""
将合同流程图导出为PNG格式
需要安装: pip install selenium pillow
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import io

def export_flowchart_to_png(html_file, output_file, element_id=None):
    """将HTML中的流程图导出为PNG"""
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        # 创建Chrome驱动
        driver = webdriver.Chrome(options=chrome_options)
        
        # 获取HTML文件的绝对路径
        html_path = os.path.abspath(html_file)
        file_url = f'file:///{html_path}'
        
        # 打开HTML文件
        driver.get(file_url)
        
        # 等待页面加载
        time.sleep(2)
        
        # 如果指定了元素ID，只截取该元素
        if element_id:
            element = driver.find_element('id', element_id)
            screenshot = element.screenshot_as_png
        else:
            # 截取整个页面
            screenshot = driver.get_screenshot_as_png()
        
        # 保存为PNG
        with open(output_file, 'wb') as f:
            f.write(screenshot)
        
        print(f'✓ 成功导出: {output_file}')
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f'✗ 导出失败: {str(e)}')
        print('提示: 请确保已安装Chrome浏览器和ChromeDriver')
        return False

def export_svg_directly(html_file, output_prefix):
    """直接从HTML中提取SVG并转换为PNG（备用方案）"""
    try:
        from cairosvg import svg2png
        import re
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取第一个SVG（合同起草流程图）
        svg_pattern = r'<svg[^>]*>.*?</svg>'
        svg_matches = re.findall(svg_pattern, content, re.DOTALL)
        
        if len(svg_matches) >= 1:
            # 导出合同起草流程图
            svg1 = svg_matches[0]
            output1 = f'{output_prefix}_合同起草流程图.png'
            svg2png(bytestring=svg1.encode('utf-8'), write_to=output1, output_width=2000)
            print(f'✓ 成功导出: {output1}')
        
        if len(svg_matches) >= 2:
            # 导出合同审核流程图
            svg2 = svg_matches[1]
            output2 = f'{output_prefix}_合同审核流程图.png'
            svg2png(bytestring=svg2.encode('utf-8'), write_to=output2, output_width=2000)
            print(f'✓ 成功导出: {output2}')
        
        return True
        
    except ImportError:
        print('cairosvg未安装，尝试使用selenium方法')
        return False
    except Exception as e:
        print(f'SVG直接转换失败: {str(e)}')
        return False

def main():
    html_file = '合同流程图.html'
    output_prefix = '合同流程图'
    
    if not os.path.exists(html_file):
        print(f'错误: 找不到文件 {html_file}')
        return
    
    print('开始导出流程图...')
    print('=' * 50)
    
    # 方法1: 尝试使用selenium截图（推荐）
    print('\n方法1: 使用Selenium截图...')
    
    # 创建两个单独的HTML文件用于截图
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建合同起草流程图的HTML
    draft_html = content.replace(
        '<h2>二、合同审核流程图</h2>',
        '<!-- 合同审核流程图已移除 -->'
    )
    draft_html = draft_html.replace(
        '<h1>AI智能合同审核系统 - 流程图</h1>',
        '<h1>合同起草流程图</h1>'
    )
    
    draft_file = 'temp_draft.html'
    with open(draft_file, 'w', encoding='utf-8') as f:
        f.write(draft_html)
    
    # 创建合同审核流程图的HTML
    review_html = content.replace(
        '<h2>一、合同起草流程图</h2>',
        '<!-- 合同起草流程图已移除 -->'
    )
    review_html = review_html.replace(
        '<h1>AI智能合同审核系统 - 流程图</h1>',
        '<h1>合同审核流程图</h1>'
    )
    
    review_file = 'temp_review.html'
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write(review_html)
    
    # 导出两个流程图
    success1 = export_flowchart_to_png(draft_file, f'{output_prefix}_合同起草流程图.png')
    success2 = export_flowchart_to_png(review_file, f'{output_prefix}_合同审核流程图.png')
    
    # 清理临时文件
    if os.path.exists(draft_file):
        os.remove(draft_file)
    if os.path.exists(review_file):
        os.remove(review_file)
    
    if success1 and success2:
        print('\n' + '=' * 50)
        print('✓ 所有流程图导出成功！')
        print(f'  - {output_prefix}_合同起草流程图.png')
        print(f'  - {output_prefix}_合同审核流程图.png')
    else:
        print('\n尝试备用方案...')
        # 方法2: 使用cairosvg直接转换
        export_svg_directly(html_file, output_prefix)

if __name__ == '__main__':
    main()

