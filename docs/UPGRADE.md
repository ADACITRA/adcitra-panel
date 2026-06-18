# AdCtira灯塔 升级指南

## 从宝塔面板升级到 AdCtira灯塔

### 方法一：全新安装（推荐）

`ash
# Debian/Ubuntu
wget -O install_panel.sh https://download.adcitra.cn/install/install_panel.sh && bash install_panel.sh

# CentOS
yum install -y wget && wget -O install_panel.sh https://download.adcitra.cn/install/install_panel.sh && bash install_panel.sh
`

### 方法二：Docker 部署

`ash
# 克隆仓库
git clone https://github.com/adcitra/panel.git
cd panel

# 启动面板
docker compose up -d

# 查看日志
docker compose logs -f

# 停止面板
docker compose down
`

### 方法三：从宝塔迁移

1. 备份宝塔面板数据
2. 安装 AdCtira灯塔
3. 导入备份数据
4. 验证服务运行

## 版本升级日志

### v12.0.0 (2026-06-18)
- 基于宝塔 11.7.1 复刻
- 全品牌重命名: 宝塔 -> AdCtira灯塔
- Docker 容器化部署支持
- 安全策略配置文件
- API 文档门户
- 环境变量配置文件
- 全新 README 文档

## 配置迁移

从宝塔迁移配置时，请注意以下路径变化：

| 宝塔路径 | AdCtira灯塔路径 |
|----------|----------------|
| /www/server/panel | /www/adcitra/panel |
| bt命令 | adcitra命令 |
| BT-Panel | AdCtira-Panel |
| BT-Task | AdCtira-Task |
| BTPanel | AdCtiraPanel |
