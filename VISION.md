# AdCtira 愿景文档

## 一句话定义

AdCtira = 自托管的 Vercel/Heroku + 你拥有服务器

---

## 市场定位

### 现有方案 vs AdCtira

| 维度 | Vercel/Heroku | 宝塔/1Panel | AdCtira（我们） |
|------|:------------:|:-----------:|:-----------------:|
| 一行命令部署 | ✅ | ❌ | ✅ |
| 自托管/拥有服务器 | ❌ | ✅ | ✅ |
| 服务器管理面板 | ❌ | ✅ | ✅ |
| 自动 SSL/域名 | ✅ | 手动 | ✅ |
| 数据库自动创建 | ❌ | 手动 | ✅ |
| 预览部署 (Preview) | ✅ | ❌ | ✅ 独创 |
| Git 自动部署 | ✅ | ❌ | ✅ 独创 |
| 自然语言运维 | ❌ | ❌ | ✅ 独创 |
| 极简模式 | ❌ | ❌ | ✅ 独创 |
| 一键从竞品迁移 | ❌ | ❌ | ✅ 独创 |

### 目标用户

1. 独立开发者 - 想要 Heroku 体验但不想被平台绑定
2. SaaS 创业团队 - 需要自托管降低成本
3. 外包/建站公司 - 批量部署客户项目
4. IDC/主机商 - 给客户提供一键部署增值服务

### 盈利能力

免费版: CLI + 面板核心（获客，打造生态）
    ↓
专业版 (19/月): 团队协作 + 高级功能
    ↓
企业版 (99/月): 白标 + SLA + 定制
    ↓
AdCtira Cloud: 托管版（不用自己管理服务器）

---

## 产品架构

```
adcitra CLI (init / deploy / apps / logs / domain / ssl / db / env)
        |
Deploy Engine（框架检测 / 代码上传 / 依赖安装 / 配置生成 / SSL）
        |
AdCtira 面板（网站 / 数据库 / Docker / SSL / 防火墙 / 文件 / 计划任务）
```

## 核心创新（别人没有的）

### 1. AI Smart Deploy - 一行命令部署任何应用
  cd my-app && adcitra deploy
  AI自动检测框架, 生成配置, 创建数据库, 上线

### 2. 预览部署 (Preview Deploy)
  adcitra deploy --preview
  每个 Git 分支自动一个预览环境

### 3. 一键从竞品迁移
  adcitra migrate --from bt
  迁移所有网站/数据库/SSL到灯塔

### 4. AI 自然语言运维
  adcitra ask "网站访问慢帮我看看"
  AI 自动诊断 CPU/内存/磁盘/网络/进程

### 5. Server Blueprint - 预设即代码
  保存当前配置为蓝图，新服务器上一键还原

---

## 项目结构

AdCtira灯塔 v12.0
  cli/adcitra.py         CLI 主程序（11个命令）
  innovations/deploy.py   AI Smart Deploy
  innovations/migrate.py  一键迁移工具
  innovations/ai_ops.py   自然语言运维
  innovations/blueprint.md 蓝图系统
  innovations/lightweight.json 极简模式
  AdCtiraPanel/           面板前端
  class/                  核心模块
  config/                 配置文件
  install/                安装脚本
  script/                 辅助工具
  docs/                   文档
  website/                产品官网
  Dockerfile              Docker 部署
  LICENSE.md              MIT 许可证
  NOTICE.md               项目声明
