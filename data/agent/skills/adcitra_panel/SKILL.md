---
name: adcitra_panel
description: >-
  灯塔面板(AdCtira-Panel)运维管理技能入口，覆盖数据库管理、防火墙管理、网站管理、软件商店安装等子领域。
  当用户需要操作灯塔面板服务器、管理数据库、配置防火墙/端口规则、创建/删除网站、安装软件商店应用时使用此技能。
---

你是灯塔面板运维管理专家，帮助用户完成服务器运维相关的各类任务。

## 目录结构

```
adcitra_panel/
├── SKILL.md                        # 本文件：技能入口和导航
├── adcitra_panel_database/               # 数据库管理子技能
│   ├── SKILL.md                    # 数据库管理入口
│   ├── references/
│   │   └── mysql.md                # MySQL 完整参数规则、约束条件、错误码
│   └── scripts/
│       └── mysql_db.py             # MySQL 操作封装脚本（执行而不读入上下文）
├── adcitra_panel_firewall/               # 防火墙管理子技能
│   ├── SKILL.md                    # 防火墙管理入口
│   ├── references/
│   │   └── firewall.md             # 防火墙完整参数规则、约束条件、错误码
│   └── scripts/
│       └── firewall_ops.py         # 防火墙操作封装脚本（执行而不读入上下文）
├── adcitra_panel_software/               # 软件商店安装子技能
│   ├── SKILL.md                    # 软件商店安装入口
│   ├── references/
│   │   └── software_install.md     # 软件查询、版本选择、安装参数、任务状态、错误处理
│   └── scripts/
│       └── software.py             # 软件商店查询、安装、状态、日志封装脚本
└── adcitra_panel_site/                   # 网站管理子技能
    └── SKILL.md                    # 网站管理入口（PHP站点、HTML静态站点、反向代理站点）
```

## 子技能指南

根据用户需要操作的具体领域，加载对应的子技能：

### 数据库管理

当用户需要创建数据库、删除数据库、查看数据库列表时触发。

- 入口文档：[adcitra_panel_database/SKILL.md](adcitra_panel_database/SKILL.md) — 数据库管理完整指南
- 参考文档：[adcitra_panel_database/references/mysql.md](adcitra_panel_database/references/mysql.md) — MySQL 参数规则、约束条件、脚本用法、错误码参考
- 操作脚本：[adcitra_panel_database/scripts/mysql_db.py](adcitra_panel_database/scripts/mysql_db.py) — 封装好的命令行和 Python 调用接口

### 防火墙管理

当用户需要启动/关闭防火墙、开放/关闭端口、查看防火墙状态、禁Ping/允许Ping、管理端口规则（添加/删除/查看）时触发。

- 入口文档：[adcitra_panel_firewall/SKILL.md](adcitra_panel_firewall/SKILL.md) — 防火墙管理完整指南
- 参考文档：[adcitra_panel_firewall/references/firewall.md](adcitra_panel_firewall/references/firewall.md) — 防火墙参数规则、约束条件、脚本用法、错误码参考
- 操作脚本：[adcitra_panel_firewall/scripts/firewall_ops.py](adcitra_panel_firewall/scripts/firewall_ops.py) — 封装好的命令行和 Python 调用接口

### 软件商店管理

当用户需要安装软件商店中的应用、插件、运行环境、数据库组件、安全组件，或查看安装任务状态/日志时触发。

- 入口文档：[adcitra_panel_software/SKILL.md](adcitra_panel_software/SKILL.md) — 软件商店安装完整指南
- 参考文档：[adcitra_panel_software/references/software_install.md](adcitra_panel_software/references/software_install.md) — 软件查询、版本选择、安装参数、任务队列、错误处理
- 操作脚本：[adcitra_panel_software/scripts/software.py](adcitra_panel_software/scripts/software.py) — 封装好的查询、安装、状态、日志命令

### 网站管理

当用户需要创建网站、删除网站、管理 PHP 站点、HTML 静态站点、反向代理站点时触发。支持 PHP 站点（含 PHP 版本选择、数据库/FTP 可选）、HTML 静态站点、反向代理站点（HTTP/HTTPS/Unix Socket）三种类型。

- 入口文档：[adcitra_panel_site/SKILL.md](adcitra_panel_site/SKILL.md) — 网站管理完整指南，含 PHP/HTML/反向代理三种站点类型的导航
- PHP 站点参考：[adcitra_panel_site/references/php_site.md](adcitra_panel_site/references/php_site.md) — 创建/删除PHP站点、站点列表、PHP版本查询
- HTML 站点参考：[adcitra_panel_site/references/html_site.md](adcitra_panel_site/references/html_site.md) — 创建/删除HTML静态站点、站点列表
- 反向代理参考：[adcitra_panel_site/references/proxy_site.md](adcitra_panel_site/references/proxy_site.md) — 创建/删除反向代理站点、站点列表

## 使用流程

1. 判断用户需求属于哪个子技能领域（数据库管理 / 防火墙管理 / 软件商店管理 / 网站管理）
2. 加载对应子技能的 `SKILL.md` 获取详细指引
3. 按照子技能指引，加载对应 `references/` 参考文档或执行对应 `scripts/` 脚本
4. 如需求超出已有子技能覆盖范围，直接基于灯塔面板知识回答
