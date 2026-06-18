# AdCtira灯塔 v12.0.0 服务器运维面板

**AdCtira灯塔 v12.0.0** 是一款现代化开源服务器运维面板，基于宝塔Linux面板复刻并全面升级。
提供网站管理、数据库、FTP、SSL证书、Docker、安全防护、文件管理等一站式运维能力。

> 在保留宝塔强大生态兼容性的同时，增加了 Docker 容器化部署、企业级安全策略配置、API 文档门户等特色功能。

---

## 与同类面板对比

| 特性 | AdCtira灯塔 12.0 | 宝塔官方 11.8 | 1Panel |
|------|:-:|:-:|:-:|
| 开源协议 | 专有许可 | 部分开源 | GPL v3 |
| 开发语言 | Python/Flask | Python/Flask | Go |
| GitHub Stars | - | 4.5K | 35.9K |
| Docker 部署 | 原生支持 | 不支持 | 原生支持 |
| 企业安全策略 | 内置 JSON 配置 | 需手动配置 | 基础配置 |
| 云存储备份 | S3/OSS/COS/七牛/又拍 | 付费功能 | 基础支持 |
| AI 助手 | 面板内置 AI | AI建站(AI点数) | AI Agent(Ollama) |
| API 文档门户 | 自带完整文档 | 论坛零散文档 | 基础文档 |
| 多机管理 | 节点管理 | 付费功能 | 集群管理 |
| CLI 工具 | AdCtira CLI | bt命令 | 1pctl命令 |

## 全新特性（v12.0.0）

- **Docker 容器化部署** — Docker Compose 一键启动，集成 Nginx + Supervisor
- **企业级安全策略** — 密码策略、登录保护、SSH 安全、审计日志 JSON 配置
- **API 文档门户** — 完整的 RESTful API 参考文档，方便二次开发
- **云存储备份配置** — 支持 S3/OSS/COS/七牛/又拍云 备份
- **环境变量配置** — .env 配置文件，灵活管理运行参数
- **升级指南** — 从宝塔平滑迁移到 AdCtira灯塔

## 功能特性

| 模块 | 功能 |
|------|------|
| **网站管理** | Nginx/Apache/OpenLiteSpeed 一键部署、SSL证书、反向代理、负载均衡 |
| **数据库** | MySQL/MariaDB/PostgreSQL 管理、备份、恢复、在线导入导出 |
| **FTP 管理** | Pure-FTPd 用户管理、权限控制、流量限制 |
| **SSL 证书** | Let's Encrypt 免费 SSL、DNS API 自动续签、SSL 部署监控 |
| **Docker 管理** | 容器编排、镜像管理、应用商店、Compose 可视化 |
| **安全防护** | 防火墙规则、WAF 防护、CC 攻击防护、木马查杀、SSH 安全 |
| **文件管理** | 在线文件浏览器、上传/下载/编辑/解压/权限管理 |
| **AI 助手** | 面板内置 AI 对话、智能运维建议、故障排查 |
| **节点管理** | 多机集群管理、负载均衡、文件同步、跨机 SSH |
| **计划任务** | 定时备份、日志切割、Shell/Python 脚本、邮件通知 |
| **软件商店** | 300+ 免费应用，一键部署 WordPress/Laravel/Discuz |
| **插件系统** | 丰富插件生态，WAF/防火墙/数据库/Docker 等扩展 |

## 技术栈

| 分层 | 技术选型 |
|------|----------|
| **后端框架** | Python Flask + Gevent |
| **前端** | HTML5 / JavaScript / CSS3 (CKEditor 4) |
| **数据存储** | SQLite / MySQL / MariaDB |
| **Web 服务器** | Nginx / Apache / OpenLiteSpeed |
| **任务调度** | Python 多线程 + Linux crontab |
| **部署方式** | 原生安装 / Docker 容器化 |
| **授权协议** | 专有许可 |

## 快速开始

### 一键安装

`ash
curl -sSO https://download.adcitra.cn/install/install_panel.sh && bash install_panel.sh
`

### Docker 部署

`ash
git clone https://github.com/adcitra/panel.git
cd panel
docker compose up -d
# 访问 http://localhost:8888
`

### 源码部署

`ash
git clone https://github.com/adcitra/panel.git
cd panel
pip install -r requirements.txt
python runserver.py
`

## 项目结构

`
AdCtira灯塔/
├── AdCtira-Panel          # 面板主程序入口
├── AdCtira-Task           # 后台任务调度入口
├── AdCtiraPanel/          # 前端静态资源和模板
├── class/                 # 核心业务逻辑（120+ 模块）
├── config/                # JSON 配置 / SQLite 数据库
├── data/                  # 运行时数据
├── install/               # 安装脚本
├── plugin/                # 插件目录
├── rewrite/               # 伪静态规则（Nginx/Apache）
├── script/                # 辅助脚本工具
├── vhost/                 # 虚拟主机配置模板
├── mod/                   # 扩展模块（Docker/Java/Node/PHP等）
├── docs/                  # API文档 + 升级指南 + 部署指南
├── Dockerfile             # Docker 构建文件
├── docker-compose.yml     # Docker Compose 编排
├── docker/                # Docker 配置文件
├── .env.example           # 环境配置模板
├── runserver.py           # 开发启动入口
├── task.py                # 后台任务调度
├── tools.py               # 工具函数
└── requirements.txt       # Python 依赖清单
`

## 系统要求

- **操作系统**: CentOS 7+ / Ubuntu 20.04+ / Debian 11+
- **Python**: 3.7 - 3.11
- **内存**: 最低 512MB，推荐 1GB+
- **磁盘**: 最低 10GB

## 文档

- [API 文档](/docs/API.md)
- [部署指南](/docs/DEPLOY.md)  
- [安全策略](/docs/SECURITY.md)
- [升级指南](/docs/UPGRADE.md)

## 开源许可

本项目采用 **MIT 许可证** 发布（详见 [LICENSE.md](LICENSE.md)）。
原创代码版权归 AdCtira灯塔 Team 所有。

如果您认为本项目的任何部分侵犯了您的合法权益，请提交 Issue 联系我们。

---

> **AdCtira灯塔 v12.0.0** — 让服务器管理像灯塔一样明亮。

