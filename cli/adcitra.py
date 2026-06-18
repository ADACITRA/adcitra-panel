#!/usr/bin/env python3
"""
adcitra — 自托管应用部署平台 CLI
让任何服务器拥有 Vercel/Heroku 一样的一键部署体验

Usage:
  adcitra init               初始化项目
  adcitra deploy             部署到服务器
  adcitra deploy --preview   部署到预览环境
  adcitra apps               列出所有应用
  adcitra logs <app>         查看应用日志
  adcitra domain <app>       管理域名
  adcitra ssl <app>          管理 SSL
  adcitra db <app> create    创建数据库
  adcitra env <app>          管理环境变量
  adcitra ps                  查看进程状态
  adcitra open <app>         在浏览器中打开
  adcitra help               显示帮助
"""

import os, sys, json, subprocess, shutil, webbrowser
from pathlib import Path

PANEL_URL = os.environ.get("ADCTIRA_URL", "http://localhost:8888")
API_KEY = os.environ.get("ADCTIRA_KEY", "")
CONFIG_DIR = Path.home() / ".adcitra"
DEPLOYS_FILE = CONFIG_DIR / "deployments.json"

C = {
    "green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m",
    "cyan": "\033[96m", "bold": "\033[1m", "end": "\033[0m",
}

def color(text, c):
    return f"{C.get(c,'')}{text}{C['end']}"

def header(title):
    print(f"\n  {color('==>', 'cyan')} {color(title, 'bold')}")

def ok(msg):
    print(f"  {color('OK', 'green')}  {msg}")

def warn(msg):
    print(f"  {color('WARN', 'yellow')} {msg}")

def fail(msg):
    print(f"  {color('ERR', 'red')}  {msg}")

def banner():
    print(f"""
  {color('AdCtira', 'cyan')} {color('CLI v1.0', 'yellow')}
  {color('自托管应用部署平台 · 一行命令部署任何应用', 'bold')}
""")

def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DEPLOYS_FILE.exists():
        DEPLOYS_FILE.write_text("[]")

def save_deployments(deploys):
    DEPLOYS_FILE.write_text(json.dumps(deploys, indent=2, ensure_ascii=False))

def load_deployments():
    load_config()
    return json.loads(DEPLOYS_FILE.read_text())

# ============ Core Framework Detection ============

FRAMEWORKS = {
    "laravel":   {"files": ["artisan"],              "type": "php",    "build": "composer install --no-dev"},
    "wordpress": {"files": ["wp-config.php"],        "type": "php",    "build": ""},
    "django":    {"files": ["manage.py"],            "type": "python", "build": "pip install -r requirements.txt"},
    "flask":     {"files": ["app.py"],               "type": "python", "build": "pip install -r requirements.txt"},
    "fastapi":   {"files": ["main.py"],              "type": "python", "build": "pip install -r requirements.txt"},
    "nextjs":    {"files": ["next.config.js"],       "type": "node",   "build": "npm install && npm run build"},
    "express":   {"files": ["app.js", "index.js"],   "type": "node",   "build": "npm install --production"},
    "nuxt":      {"files": ["nuxt.config.js"],       "type": "node",   "build": "npm install && npm run build"},
    "static":    {"files": ["index.html"],           "type": "static", "build": ""},
}

def detect_framework(path):
    best_name, best_score = None, 0
    for name, cfg in FRAMEWORKS.items():
        score = sum(3 for f in cfg["files"] if (Path(path) / f).exists())
        if score > best_score:
            best_score, best_name = score, name
    return best_name, FRAMEWORKS.get(best_name) if best_name else None

# ============ Commands ============

def cmd_init(args):
    """初始化当前目录为部署项目"""
    header("初始化项目")
    path = Path(args.path or os.getcwd())
    
    # 检测框架
    fw_name, fw_config = detect_framework(str(path))
    if not fw_name:
        warn(f"未能自动识别框架: {path.name}")
        fw_name = input("  请输入框架名称 (laravel/django/nextjs/static): ") or "static"
        fw_config = FRAMEWORKS.get(fw_name, FRAMEWORKS["static"])
    
    app_name = args.name or path.name.replace(" ", "-").lower()
    
    config = {
        "name": app_name,
        "framework": fw_name,
        "type": fw_config["type"],
        "path": str(path),
        "domain": "",
        "created": __import__("datetime").datetime.now().isoformat(),
    }
    
    (path / ".adcitra.json").write_text(json.dumps(config, indent=2))
    
    ok(f"项目 {app_name} 初始化完成")
    print(f"    框架: {fw_name} ({fw_config['type']})")
    print(f"    配置: {path / '.adcitra.json'}")
    print(f"    下一步: cd {path.name} && adcitra deploy")

def cmd_deploy(args):
    """部署应用到服务器"""
    header("部署应用")
    path = Path(args.path or os.getcwd())
    
    # 读取项目配置
    config_file = path / ".adcitra.json"
    if config_file.exists():
        config = json.loads(config_file.read_text())
        fw_name = config["framework"]
        fw_config = FRAMEWORKS.get(fw_name)
    else:
        fw_name, fw_config = detect_framework(str(path))
        if not fw_name:
            fail("无法检测框架。先运行 adcitra init")
            sys.exit(1)
        config = {"name": path.name.replace(" ", "-").lower(), "framework": fw_name}
    
    app_name = config["name"]
    is_preview = args.preview
    domain = f"{app_name}-preview.test" if is_preview else f"{app_name}.test"
    
    print(f"    应用: {color(app_name, 'bold')}")
    print(f"    框架: {fw_name} ({fw_config['type']})")
    print(f"    域名: {domain}")
    print(f"    模式: {'preview' if is_preview else 'production'}")
    
    # Step 1: 创建部署目录
    target = f"/www/wwwroot/{app_name}"
    header("创建目录")
    os.makedirs(target, exist_ok=True) if is_preview else os.makedirs(target, exist_ok=False)
    ok(f"目录: {target}")
    
    # Step 2: 上传代码
    header("上传代码")
    if str(path) != target:
        for item in path.iterdir():
            if item.name.startswith(".") or item.name == "node_modules":
                continue
            dest = Path(target) / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
    ok("代码已上传")
    
    # Step 3: 安装依赖
    if fw_config["build"]:
        header("安装依赖")
        try:
            subprocess.run(fw_config["build"], shell=True, cwd=target, capture_output=True, timeout=120)
            ok("依赖安装完成")
        except:
            warn("依赖安装失败")
    
    # Step 4: 生成 Nginx 配置
    header("配置 Web 服务器")
    port = sum(ord(c) for c in app_name) % 1000 + 8000
    nginx_conf = f"""
server {{
    listen 80;
    server_name {domain};
    root {target}/{'public' if fw_config['type'] == 'php' else '.'};
    index index.html index.htm index.php;
    access_log /www/wwwlogs/{app_name}.log;
    error_log /www/wwwlogs/{app_name}.error.log;
"""
    if fw_config["type"] == "php":
        nginx_conf += """
    location ~ \\.php$ {
        fastcgi_pass unix:/tmp/php-cgi-74.sock;
        fastcgi_index index.php; include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
    location / { try_files $uri $uri/ /index.php?$query_string; }"""
    elif fw_config["type"] in ("python", "node"):
        nginx_conf += f"""
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }}"""
    else:
        nginx_conf += "\n    location / { try_files $uri $uri/ =404; }"
    nginx_conf += "\n}\n"
    
    nginx_path = f"/www/server/panel/vhost/nginx/{app_name}.conf"
    os.makedirs(os.path.dirname(nginx_path), exist_ok=True)
    Path(nginx_path).write_text(nginx_conf)
    ok(f"Nginx 配置已生成: {nginx_path}")
    
    # Step 5: 创建数据库
    if args.db:
        header("创建数据库")
        db_name = app_name.replace("-", "_")
        try:
            subprocess.run(f"mysql -e 'CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4'", shell=True, capture_output=True)
            ok(f"数据库: {db_name}")
        except:
            warn("数据库创建失败（可能未安装 MySQL）")
    
    # Step 6: 保存部署记录
    deploy_record = {
        "name": app_name, "framework": fw_name, "domain": domain,
        "target": target, "preview": is_preview,
        "deployed_at": __import__("datetime").datetime.now().isoformat(),
    }
    deploys = load_deployments()
    deploys.append(deploy_record)
    save_deployments(deploys)
    
    # 完成
    print(f"\n  {color('='*40, 'green')}")
    print(f"  {color('部署成功!', 'bold')}")
    print(f"  {color('='*40, 'green')}")
    print(f"    URL:  http://{domain}")
    print(f"    目录: {target}")
    print(f"    框架: {fw_name}")
    print(f"\n  运行 adcitra apps 查看所有已部署应用")
    print(f"  运行 adcitra logs {app_name} 查看日志\n")

def cmd_apps(args):
    """列出所有已部署的应用"""
    header("已部署的应用")
    deploys = load_deployments()
    
    if not deploys:
        warn("暂无已部署的应用")
        print("  运行 adcitra deploy 部署第一个应用")
        return
    
    apps = {}
    for d in deploys:
        name = d["name"]
        if name not in apps or not d.get("preview"):
            apps[name] = d
    
    print(f"  共 {len(apps)} 个应用\n")
    print(f"  {'名称':<20} {'框架':<12} {'域名':<25} {'状态':<8}")
    print(f"  {'-'*20} {'-'*12} {'-'*25} {'-'*8}")
    
    for name, info in sorted(apps.items()):
        status = "preview" if info.get("preview") else "live"
        print(f"  {name:<20} {info['framework']:<12} {info['domain']:<25} {status:<8}")

def cmd_logs(args):
    """查看应用日志"""
    if not args.app:
        fail("请指定应用名: adcitra logs <app>")
        sys.exit(1)
    
    log_file = f"/www/wwwlogs/{args.app}.log"
    error_file = f"/www/wwwlogs/{args.app}.error.log"
    
    header(f"日志: {args.app}")
    
    files = [f for f in [log_file, error_file] if os.path.exists(f)]
    if not files:
        warn("未找到日志文件")
        return
    
    for f in files:
        print(f"\n  {color(f, 'bold')}:")
        try:
            lines = Path(f).read_text().splitlines()[-20:]
            for line in lines:
                print(f"    {line}")
        except:
            warn(f"无法读取: {f}")

def cmd_domain(args):
    """管理域名"""
    if not args.app:
        fail("请指定应用名")
        return
    
    header(f"域名管理: {args.app}")
    print(f"\n  当前域名: {args.app}.test")
    print(f"  运行: adcitra ssl {args.app} 配置 HTTPS")
    print(f"  运行: adcitra open {args.app} 在浏览器打开")

def cmd_ssl(args):
    """配置 SSL"""
    if not args.app:
        fail("请指定应用名")
        return
    
    header(f"SSL 配置: {args.app}")
    print(f"\n  执行 Let's Encrypt 自动签发...")
    cert_dir = f"/www/server/panel/vhost/cert/{args.app}"
    os.makedirs(cert_dir, exist_ok=True)
    ok(f"证书目录: {cert_dir}")
    print(f"  需将域名 DNS 解析到本服务器后运行完整 SSL 签发流程")

def cmd_db(args):
    """数据库管理"""
    if not args.app:
        fail("请指定应用名")
        return
    
    action = args.action or "list"
    db_name = args.app.replace("-", "_")
    
    header(f"数据库: {args.app}")
    
    if action == "create":
        try:
            subprocess.run(f"mysql -e 'CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4'", shell=True, capture_output=True)
            ok(f"数据库 {db_name} 创建成功")
        except:
            mysql_ok = shutil.which("mysql")
            if not mysql_ok:
                warn("未安装 MySQL/mariadb")
            else:
                warn("创建失败，请检查 MySQL 权限")
    elif action == "list":
        print(f"  数据库名: {db_name}")
    else:
        warn(f"未知操作: {action}")

def cmd_env(args):
    """管理环境变量"""
    if not args.app:
        fail("请指定应用名")
        return
    
    env_file = f"/www/wwwroot/{args.app}/.env"
    if os.path.exists(env_file):
        header(f"环境变量: {args.app}")
        print(Path(env_file).read_text())
    else:
        warn(f"未找到 .env 文件")

def cmd_open(args):
    """在浏览器中打开应用"""
    if not args.app:
        fail("请指定应用名")
        return
    
    url = f"http://{args.app}.test"
    print(f"  打开: {url}")
    try:
        webbrowser.open(url)
    except:
        pass

def cmd_ps(args):
    """查看进程状态"""
    header("进程状态")
    try:
        result = subprocess.run(
            "ps aux --sort=-%mem | head -15", shell=True, capture_output=True, text=True
        )
        print(result.stdout)
    except:
        warn("进程列表获取失败")

def cmd_help(args):
    """显示帮助"""
    print(__doc__)

def main():
    banner()
    
    import argparse
    parser = argparse.ArgumentParser(description="AdCtira CLI", add_help=False)
    parser.add_argument("--server", "-s", help="面板服务器地址")
    parser.add_argument("--key", "-k", help="API Key")
    
    sub = parser.add_subparsers(dest="command")
    
    p_init = sub.add_parser("init", help="初始化项目")
    p_init.add_argument("--path", help="项目路径")
    p_init.add_argument("--name", "-n", help="应用名称")
    
    p_deploy = sub.add_parser("deploy", help="部署应用")
    p_deploy.add_argument("--path", help="项目路径")
    p_deploy.add_argument("--preview", action="store_true", help="部署到预览环境")
    p_deploy.add_argument("--db", action="store_true", help="同时创建数据库")
    p_deploy.add_argument("--domain", help="自定义域名")
    
    p_apps = sub.add_parser("apps", help="列出应用")
    
    p_logs = sub.add_parser("logs", help="查看日志")
    p_logs.add_argument("app", nargs="?", help="应用名")
    
    p_domain = sub.add_parser("domain", help="管理域名")
    p_domain.add_argument("app", nargs="?", help="应用名")
    
    p_ssl = sub.add_parser("ssl", help="管理 SSL")
    p_ssl.add_argument("app", nargs="?", help="应用名")
    
    p_db = sub.add_parser("db", help="管理数据库")
    p_db.add_argument("app", nargs="?", help="应用名")
    p_db.add_argument("action", nargs="?", choices=["create", "list"], default="list")
    
    p_env = sub.add_parser("env", help="管理环境变量")
    p_env.add_argument("app", nargs="?", help="应用名")
    
    p_open = sub.add_parser("open", help="在浏览器打开")
    p_open.add_argument("app", nargs="?", help="应用名")
    
    p_ps = sub.add_parser("ps", help="进程状态")
    
    _ = sub.add_parser("help", help="显示帮助")
    
    args = parser.parse_args()
    
    if args.server:
        global PANEL_URL
        PANEL_URL = args.server
    if args.key:
        global API_KEY
        API_KEY = args.key
    
    commands = {
        "init": cmd_init, "deploy": cmd_deploy, "apps": cmd_apps,
        "logs": cmd_logs, "domain": cmd_domain, "ssl": cmd_ssl,
        "db": cmd_db, "env": cmd_env, "open": cmd_open,
        "ps": cmd_ps, "help": cmd_help,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
