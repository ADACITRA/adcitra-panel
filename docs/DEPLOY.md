# AdCtira灯塔 部署指南

## 系统要求

- **操作系统**: Linux (CentOS 7+, Ubuntu 20.04+, Debian 11+, Deepin 20+)
- **Python**: 3.7 - 3.11
- **内存**: 最低 512MB，推荐 1GB+
- **磁盘**: 最低 10GB
- **网络**: 需公网 IP 或内网可访问

## 快速部署

### 方法一：一键安装（推荐）

`ash
# Debian/Ubuntu/Docker
curl -sSO https://download.adcitra.cn/install/install_panel.sh && bash install_panel.sh
`

### 方法二：Docker 部署

`ash
# 1. 拉取镜像（构建）
docker compose build

# 2. 启动服务
docker compose up -d

# 3. 访问面板
open http://localhost:8888
`

### 方法三：源码部署

`ash
# 1. 克隆仓库
git clone https://github.com/adcitra/panel.git
cd panel

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动面板
python runserver.py
`

## Docker 部署详解

### 基础部署

`ash
# 构建并启动
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f adcitra-panel
`

### 使用外部数据库

`ash
# 使用 MySQL 数据库启动
docker compose --profile full up -d
`

### 自定义配置

创建 docker-compose.override.yml：

`yaml
version: '3.8'
services:
  adcitra-panel:
    ports:
      - "8888:8888"
    environment:
      - PANEL_PORT=8888
`

## 安全加固

### 部署后操作

1. **修改默认密码**: 安装后立即修改管理员密码
2. **配置防火墙**: 仅开放必要端口
3. **启用 HTTPS**: 安装 SSL 证书
4. **定期备份**: 配置自动备份到云存储

## 端口说明

| 端口 | 说明 | 建议 |
|------|------|------|
| 8888 | 面板管理端口 | 修改为非默认端口 |
| 80 | HTTP | 开放 |
| 443 | HTTPS | 开放 |
| 21 | FTP | 按需开放 |
| 22 | SSH | 修改为非常用端口 |

## 常见问题

### 1. 面板无法启动

`ash
# 检查日志
tail -f /www/adcitra/panel/logs/error.log

# 检查端口占用
lsof -i:8888

# 手动启动
python /www/adcitra/panel/runserver.py
`

### 2. 忘记密码

`ash
# 使用 CLI 重置
cd /www/adcitra/panel && python tools.py admin admin123
`

### 3. 数据库连接失败

检查 MySQL 服务状态和配置文件中的连接信息。
