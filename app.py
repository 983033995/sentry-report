from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import requests
import pandas as pd
import json
import os
from datetime import datetime
import yaml

app = Flask(__name__)
CORS(app)

# 配置文件路径
CONFIG_DIR = 'config'
TEMPLATES_DIR = 'templates_config'
OUTPUT_DIR = 'output'

# 确保目录存在
for dir_path in [CONFIG_DIR, TEMPLATES_DIR, OUTPUT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取所有模板"""
    templates = []
    if os.path.exists(TEMPLATES_DIR):
        for file in os.listdir(TEMPLATES_DIR):
            if file.endswith('.json'):
                template_name = file[:-5]  # 移除.json后缀
                templates.append(template_name)
    return jsonify(templates)

@app.route('/api/templates/<template_name>', methods=['GET'])
def get_template(template_name):
    """获取指定模板"""
    template_path = os.path.join(TEMPLATES_DIR, f'{template_name}.json')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_data = json.load(f)
        return jsonify(template_data)
    return jsonify({'error': '模板不存在'}), 404

@app.route('/api/templates/<template_name>', methods=['POST'])
def save_template(template_name):
    """保存模板"""
    template_data = request.json
    template_path = os.path.join(TEMPLATES_DIR, f'{template_name}.json')
    
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, ensure_ascii=False, indent=2)
    
    return jsonify({'message': '模板保存成功'})

@app.route('/api/templates/<template_name>', methods=['DELETE'])
def delete_template(template_name):
    """删除模板"""
    template_path = os.path.join(TEMPLATES_DIR, f'{template_name}.json')
    if os.path.exists(template_path):
        os.remove(template_path)
        return jsonify({'message': '模板删除成功'})
    return jsonify({'error': '模板不存在'}), 404

@app.route('/api/test-api', methods=['POST'])
def test_api():
    """测试API接口"""
    config = request.json
    
    try:
        # 准备请求参数
        url = config.get('url')
        headers = config.get('headers', {})
        method = config.get('method', 'GET').upper()
        params = config.get('params', {})
        data = config.get('data', {})
        
        # 发送请求
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            return jsonify({'error': f'不支持的请求方法: {method}'}), 400
        
        # 检查响应状态
        response.raise_for_status()
        
        # 尝试解析JSON响应
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'data': response_data
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def fetch_all_pages(url, headers, params, method, pagination_config, data_path, data=None):
    """获取所有分页数据"""
    all_data = []
    page_count = 0
    max_pages = pagination_config.get('max_pages', 100)
    cursor_param = pagination_config.get('cursor_param', 'cursor')
    page_size_param = pagination_config.get('page_size_param', 'per_page')
    next_cursor_path = pagination_config.get('next_cursor_path', 'links.next.cursor')
    page_param = pagination_config.get('page_param', 'page')  # 支持基于页码的分页
    
    # 获取页大小，默认为25
    page_size = params.get(page_size_param, 25)
    if isinstance(page_size, str):
        try:
            page_size = int(page_size)
        except:
            page_size = 25
    
    print(f"开始分页获取数据，最大页数: {max_pages}，页大小: {page_size}")
    
    # 初始化cursor，第一页从0:0:1开始（Sentry格式：offset:limit:direction）
    current_offset = 0
    
    while page_count < max_pages:
        page_count += 1
        print(f"正在获取第 {page_count} 页数据...")
        
        # 设置当前页的参数
        current_params = params.copy()
        
        # 构造Sentry格式的cursor
        if page_count == 1:
            # 第一页：0:0:1（从头开始，方向向后）
            current_cursor = "0:0:1"
        else:
            # 后续页：offset:page_size:0（从当前偏移量开始，方向向前）
            current_cursor = f"0:{current_offset}:0"
        
        current_params[cursor_param] = current_cursor
        current_params[page_size_param] = page_size
        
        print(f"当前cursor: {current_cursor}，偏移量: {current_offset}")
        
        try:
            # 发送请求
            if method == 'GET':
                response = requests.get(url, headers=headers, params=current_params, timeout=30)
            elif method == 'POST':
                # POST请求时，分页参数应该添加到URL查询字符串中
                response = requests.post(url, headers=headers, params=current_params, json=data, timeout=30)
            
            response.raise_for_status()
            page_data = response.json()
            
            # 提取数据
            extracted_data = page_data
            if data_path:
                for key in data_path.split('.'):
                    if key and isinstance(extracted_data, dict) and key in extracted_data:
                        extracted_data = extracted_data[key]
            
            # 确保数据是列表格式
            if isinstance(extracted_data, list):
                if len(extracted_data) == 0:
                    print(f"第 {page_count} 页没有数据，停止分页")
                    break
                all_data.extend(extracted_data)
                print(f"第 {page_count} 页获取到 {len(extracted_data)} 条数据")
                
                # 更新偏移量，为下一页做准备
                current_offset += len(extracted_data)
                
                # 如果返回的数据少于页大小，说明已经是最后一页
                if len(extracted_data) < page_size:
                    print(f"返回数据量({len(extracted_data)})小于页大小({page_size})，已到最后一页")
                    break
            else:
                print(f"第 {page_count} 页数据格式不是列表，停止分页")
                break
            
        except Exception as e:
            print(f"获取第 {page_count} 页数据失败: {str(e)}")
            break
    
    print(f"分页完成，共获取 {len(all_data)} 条数据，总页数: {page_count}")
    return all_data

@app.route('/api/export', methods=['POST'])
def export_excel():
    """导出Excel文件"""
    config = request.json
    
    try:
        # 获取配置
        api_config = config.get('api_config', {})
        excel_config = config.get('excel_config', {})
        export_mode = config.get('export_mode', 'current')
        pagination_config = config.get('pagination_config', {})
        
        # 发送API请求
        url = api_config.get('url')
        headers = api_config.get('headers', {})
        method = api_config.get('method', 'GET').upper()
        params = api_config.get('params', {})
        data = api_config.get('data', {})
        
        # 解析JSON字符串格式的参数
        if isinstance(headers, str):
            try:
                headers = json.loads(headers) if headers.strip() else {}
            except:
                headers = {}
        
        if isinstance(params, str):
            try:
                params = json.loads(params) if params.strip() else {}
            except:
                params = {}
                
        if isinstance(data, str):
            try:
                data = json.loads(data) if data.strip() else {}
            except:
                data = {}
        
        print(f"导出模式: {export_mode}")
        print(f"分页配置: {pagination_config}")
        print(f"发送请求到: {url}")
        print(f"请求头: {headers}")
        print(f"请求参数: {params}")
        print(f"请求数据: {data}")
        
        # 获取数据路径
        data_path = excel_config.get('data_path', '').strip()
        
        if export_mode == 'all':
            # 分页获取所有数据
            api_data = fetch_all_pages(url, headers, params, method, pagination_config, data_path, data)
        else:
            # 获取当前页数据
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            api_data = response.json()
            
            print(f"API响应数据类型: {type(api_data)}")
            
            # 处理数据路径
            if data_path:
                print(f"数据路径: {data_path}")
                for key in data_path.split('.'):
                    if key and isinstance(api_data, dict) and key in api_data:
                        api_data = api_data[key]
                        print(f"提取路径 {key} 后的数据: {type(api_data)}")
            
            # 确保数据是列表格式
            if not isinstance(api_data, list):
                if isinstance(api_data, dict):
                    api_data = [api_data]
                else:
                    api_data = [{'value': api_data}]
        
        print(f"处理后的数据长度: {len(api_data)}")
        
        # 在转换为DataFrame之前处理transaction字段
        if len(api_data) > 0 and isinstance(api_data, list):
            for item in api_data:
                if isinstance(item, dict) and 'transaction' in item:
                    transaction_value = item['transaction']
                    if transaction_value and not str(transaction_value).startswith('/'):
                        item['transaction'] = '/' + str(transaction_value)
            print(f"已在数据层处理transaction字段，统一添加\"/\"前缀")
        
        # 转换为DataFrame
        if len(api_data) == 0:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(api_data)
        
        print(f"DataFrame形状: {df.shape}")
        if not df.empty:
            print(f"DataFrame列: {list(df.columns)}")
        
        # 应用列映射
        column_mapping = excel_config.get('column_mapping', {})
        if column_mapping and not df.empty:
            df = df.rename(columns=column_mapping)
            print(f"应用列映射后的列: {list(df.columns)}")
        
        # 选择指定列
        selected_columns = excel_config.get('selected_columns', [])
        if selected_columns and not df.empty:
            selected_columns = [col.strip() for col in selected_columns if col.strip()]
            if selected_columns:
                available_columns = [col for col in selected_columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
                    print(f"选择列后的DataFrame: {list(df.columns)}")
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mode_suffix = '_all' if export_mode == 'all' else '_current'
        filename = f"export{mode_suffix}_{timestamp}.xlsx"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # 导出Excel
        if df.empty:
            df = pd.DataFrame({'提示': ['没有找到数据，请检查API响应和数据路径配置']})
        
        df.to_excel(filepath, index=False, sheet_name='Data')
        print(f"Excel文件已保存: {filepath}")
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"导出错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("正在启动API数据导出工具...")
    print("服务器地址: http://localhost:8080")
    print("按 Ctrl+C 停止服务器")
    app.run(debug=True, host='0.0.0.0', port=8080)