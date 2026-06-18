




# AdCtira灯塔 服务器运维面板

**AdCtira灯塔** 是一款基于宝塔Linux面板（aaPanel/BaoTa）复刻的开源服务器运维面板。
简单好用、功能强大的服务器管理工具，让运维管理更高效。

---

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| **网站管理** | Nginx/Apache/OpenLiteSpeed 一键部署、SSL证书、反向代理 |
| **数据库** | MySQL/MariaDB/PostgreSQL 管理、备份、恢复 |
| **FTP 管理** | Pure-FTPd 用户管理、权限控制 |
| **SSL 证书** | Let's Encrypt 免费 SSL、DNS API 自动续签 |
| **文件管理** | 在线文件浏览器、上传/下载/编辑/解压 |
| **安全防护** | 防火墙规则、WAF 防护、SSH 安全、木马查杀 |
| **计划任务** | 定时备份、日志切割、脚本任务 |
| **Docker 管理** | 容器编排、镜像管理、应用商店 |
| **PHP 管理** | 多版本共存、扩展管理 |
| **插件系统** | 丰富的插件生态，扩展面板功能 |
| **集群管理** | 多节点管理、负载均衡、文件同步 |

## 🛠 技术栈

| 分层 | 技术选型 |
|------|----------|
| **后端框架** | Python Flask |
| **前端** | HTML5 / JavaScript / CSS3（CKEditor） |
| **数据存储** | SQLite / MySQL |
| **Web 服务器** | Nginx / Apache / OpenLiteSpeed |
| **任务调度** | Python 多线程 + crontab |
| **授权协议** | LGPL v3 |

## 📦 项目结构

```
AdCtira灯塔/
├── AdCtira-Panel          # 面板主程序入口
├── AdCtira-Task           # 后台任务调度入口
├── AdCtiraPanel/          # 前端静态资源和模板
│   ├── static/            # CSS / JS / 图片
│   ├── templates/         # HTML 模板
│   └── __init__.py        # Flask 应用初始化
├── class/                 # 核心业务逻辑（120+ 模块）
│   ├── panelSite.py       # 网站管理
│   ├── public.py          # 公共函数
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库管理
│   ├── files.py           # 文件管理
│   ├── ajax.py            # AJAX 接口
│   └── ...
├── config/                # JSON 配置 / SQLite 数据库
├── data/                  # 运行时数据
├── install/               # 安装脚本
├── plugin/                # 插件目录
├── rewrite/               # 伪静态规则（Nginx/Apache）
├── script/                # 辅助脚本工具
├── vhost/                 # 虚拟主机配置模板
├── mod/                   # 扩展模块（Docker/Java/Node/PHP等）
├── runserver.py           # 开发启动入口
├── runconfig.py           # 运行配置
├── task.py                # 后台任务调度
├── tools.py               # 工具函数
└── requirements.txt       # Python 依赖清单
```

## 🚀 快速启动（开发模式）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置运行参数
python runconfig.py

# 3. 启动面板
python runserver.py
```

## 📋 系统要求

- **操作系统**: CentOS / Ubuntu / Debian / Deepin / OpenCloud
- **Python**: 3.7+
- **Web 服务器**: Nginx 1.18+ / Apache 2.4+
- **数据库**: MySQL 5.7+ 或 MariaDB 10.3+

## 📄 开源许可

本项目基于 **LGPL v3** 开源协议发布。
原项目为 [aaPanel/BaoTa](https://github.com/aaPanel/BaoTa)（宝塔Linux面板）。

本复刻版本在保留原 LGPL 协议的基础上进行了品牌重命名和个性化定制。

---

> **AdCtira灯塔** — 让服务器管理像灯塔一样明亮。
