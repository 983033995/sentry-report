# API数据导出工具

一个简单易用的Web应用，用于从API接口获取数据并导出为Excel文件。支持接口配置、Excel表头自定义和模板管理功能。

## 功能特性

- 🔧 **接口配置**: 支持GET/POST请求，自定义请求头和参数
- 📊 **Excel配置**: 自定义列映射、数据路径和导出列
- 📝 **模板管理**: 保存和管理常用的配置模板
- 🎨 **友好界面**: 现代化的Web界面，操作简单直观
- ⚡ **实时测试**: 在线测试API接口，预览返回数据

## 安装说明

### 1. 环境要求

- Python 3.7+
- pip

### 2. 安装依赖

```bash
# 克隆或下载项目到本地
cd sentry-report

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:8080` 启动。

## Docker部署

### 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/983033995/sentry-report.git
cd sentry-report

# 使用docker-compose启动
docker-compose up -d

# 带nginx反向代理启动
docker-compose --profile with-nginx up -d
```

### 使用Docker直接运行

```bash
# 构建镜像
docker build -t sentry-report .

# 运行容器
docker run -d \
  --name sentry-report \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/templates_config:/app/templates_config \
  -v $(pwd)/output:/app/output \
  sentry-report
```

### 使用GitHub Container Registry

```bash
# 拉取最新镜像
docker pull ghcr.io/983033995/sentry-report:latest

# 运行容器
docker run -d \
  --name sentry-report \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/templates_config:/app/templates_config \
  -v $(pwd)/output:/app/output \
  ghcr.io/983033995/sentry-report:latest
```

## 使用指南

### 1. 接口配置

1. 在「接口配置」标签页中填写API信息：
   - **接口地址**: 完整的API URL
   - **请求方法**: GET或POST
   - **请求头**: JSON格式的请求头信息
   - **请求参数**: URL参数（GET）或查询参数
   - **请求体数据**: POST请求的body数据

2. 点击「测试接口」验证配置是否正确

### 2. Excel配置

1. 在「Excel配置」标签页中设置导出选项：
   - **数据路径**: 如果API返回嵌套数据，指定数据位置（如：`data.items`）
   - **列映射**: 将API字段名映射为Excel列名
   - **选择导出列**: 指定要导出的字段（逗号分隔）

2. 点击「导出Excel」生成并下载文件

### 3. 模板管理

1. 在「模板管理」标签页中：
   - 输入模板名称，点击「保存当前配置为模板」
   - 从模板列表中选择已保存的模板进行加载
   - 删除不需要的模板

## 配置示例

### API配置示例

```json
{
  "url": "https://jsonplaceholder.typicode.com/users",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer your-token",
    "Content-Type": "application/json"
  },
  "params": {
    "page": 1,
    "limit": 10
  }
}
```

### Excel配置示例

- **数据路径**: `data.users`（如果API返回 `{"data": {"users": [...]}}`）
- **列映射**: 
  - `id` → `用户ID`
  - `name` → `姓名`
  - `email` → `邮箱`
- **选择导出列**: `id,name,email,phone`

## 项目结构

```
sentry-report/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── templates/
│   └── index.html        # 前端界面
├── config/               # 配置文件目录
├── templates_config/     # 模板存储目录
├── output/              # Excel输出目录
└── README.md            # 说明文档
```

## API接口说明

- `GET /` - 主页面
- `GET /api/templates` - 获取模板列表
- `GET /api/templates/<name>` - 获取指定模板
- `POST /api/templates/<name>` - 保存模板
- `DELETE /api/templates/<name>` - 删除模板
- `POST /api/test-api` - 测试API接口
- `POST /api/export` - 导出Excel文件

## 注意事项

1. 请确保API接口支持CORS或在同域下使用
2. 大量数据导出时请耐心等待
3. 模板文件保存在 `templates_config/` 目录下
4. 导出的Excel文件保存在 `output/` 目录下

## 故障排除

### 常见问题

1. **API测试失败**
   - 检查网络连接
   - 验证API地址和认证信息
   - 确认请求头格式正确

2. **Excel导出失败**
   - 检查数据路径是否正确
   - 确认API返回的数据格式
   - 验证列映射配置

3. **模板加载失败**
   - 检查模板文件是否存在
   - 验证JSON格式是否正确

## 部署选项

### 1. 本地开发部署
```bash
python app.py
```

### 2. Docker容器部署
```bash
docker-compose up -d
```

### 3. 云平台部署

#### GitHub Container Registry
项目配置了GitHub Actions自动构建，每次推送到main分支都会自动构建Docker镜像并推送到GitHub Container Registry。

#### 其他云平台
- **Heroku**: 支持直接从GitHub部署
- **Railway**: 支持Docker部署
- **Render**: 支持Docker部署
- **DigitalOcean App Platform**: 支持Docker部署
- **AWS ECS/Fargate**: 支持容器部署
- **Google Cloud Run**: 支持容器部署
- **Azure Container Instances**: 支持容器部署

## 技术栈

- **后端**: Flask, Pandas, OpenPyXL, Requests
- **前端**: HTML5, CSS3, JavaScript
- **数据处理**: Pandas
- **Excel生成**: OpenPyXL
- **容器化**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **反向代理**: Nginx（可选）

## 许可证

MIT License
