# AdCtira灯塔 API 文档

## 概述

AdCtira灯塔面板提供 RESTful API 接口，方便开发者进行自动化运维管理。
所有 API 需要认证后使用。

## 基础信息

- **Base URL**: http://<your-panel>:8888/api/v1
- **Content-Type**: pplication/json
- **认证方式**: Cookie Session（登录后自动获取）
- **编码**: UTF-8

## API 端点

### 1. 系统管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/system/info | 获取系统信息 |
| GET | /api/v1/system/status | 获取系统运行状态 |
| POST | /api/v1/system/restart | 重启面板 |

### 2. 网站管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/site/list | 获取网站列表 |
| POST | /api/v1/site/create | 创建网站 |
| POST | /api/v1/site/delete | 删除网站 |
| POST | /api/v1/site/update | 更新网站配置 |
| GET | /api/v1/site/detail | 获取网站详情 |

### 3. 数据库管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/database/list | 获取数据库列表 |
| POST | /api/v1/database/create | 创建数据库 |
| POST | /api/v1/database/delete | 删除数据库 |
| POST | /api/v1/database/backup | 备份数据库 |

### 4. FTP 管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ftp/list | 获取 FTP 用户列表 |
| POST | /api/v1/ftp/create | 创建 FTP 用户 |
| POST | /api/v1/ftp/delete | 删除 FTP 用户 |

### 5. SSL 证书

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ssl/list | 获取证书列表 |
| POST | /api/v1/ssl/apply | 申请 Let's Encrypt 证书 |
| POST | /api/v1/ssl/renew | 续期证书 |

### 6. 文件管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/files/list | 获取文件列表 |
| POST | /api/v1/files/upload | 上传文件 |
| POST | /api/v1/files/delete | 删除文件 |
| POST | /api/v1/files/edit | 编辑文件 |

### 7. 计划任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/cron/list | 获取任务列表 |
| POST | /api/v1/cron/create | 创建计划任务 |
| POST | /api/v1/cron/delete | 删除计划任务 |

### 8. 安全

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/firewall/rules | 获取防火墙规则 |
| POST | /api/v1/firewall/add | 添加防火墙规则 |
| POST | /api/v1/firewall/delete | 删除防火墙规则 |

## 认证示例

`python
import requests

# 登录获取 session
session = requests.Session()
login_data = {
    'username': 'admin',
    'password': 'your_password'
}
session.post('http://localhost:8888/login', data=login_data)

# 调用 API
response = session.get('http://localhost:8888/api/v1/system/info')
print(response.json())
`

## 返回格式

`json
{
    "status": true,
    "msg": "操作成功",
    "data": {}
}
`

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
