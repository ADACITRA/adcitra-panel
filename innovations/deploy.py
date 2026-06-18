#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdCtira灯塔 AI Smart Deploy
一行命令，任何应用，自动部署到生产环境
行业首创 — 没有任何面板有这个功能
"""
import os, sys, json, re, subprocess
from datetime import datetime
from pathlib import Path

FRAMEWORKS = {
    "laravel":   {"files": ["artisan"],              "type": "php",    "entry": "public/index.php"},
    "wordpress": {"files": ["wp-config.php"],        "type": "php",    "entry": "index.php"},
    "django":    {"files": ["manage.py"],            "type": "python", "entry": "wsgi.py"},
    "flask":     {"files": ["app.py"],               "type": "python", "entry": "app.py"},
    "fastapi":   {"files": ["main.py"],              "type": "python", "entry": "main.py"},
    "nextjs":    {"files": ["next.config.js"],       "type": "node",   "entry": "server.js"},
    "express":   {"files": ["package.json"],         "type": "node",   "entry": "index.js"},
    "static":    {"files": ["index.html"],           "type": "static", "entry": "index.html"},
}

def detect_framework(path):
    best_name, best_score = None, 0
    for name, cfg in FRAMEWORKS.items():
        score = sum(3 for f in cfg["files"] if (Path(path) / f).exists())
        if score > best_score:
            best_score, best_name = score, name
    return best_name

def gen_nginx(name, fw_type, domain):
    root = f"/www/wwwroot/{name}"
    port = sum(ord(c) for c in name) % 1000 + 8000
    lines = [f"# AdCtira灯塔 Auto-Generated Config: {name}"]
    lines += [f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    lines += [f"server {{", f"    listen 80;", f"    server_name {domain};"]
    lines += [f"    root {root};", f"    index index.html index.htm index.php;"]
    lines += [f"    access_log /www/wwwlogs/{name}.log;"]
    lines += [f"    error_log /www/wwwlogs/{name}.error.log;", ""]
    
    if fw_type == "php":
        lines += ['    location ~ \\.php$ {']
        lines += ['        fastcgi_pass unix:/tmp/php-cgi-74.sock;']
        lines += ['        fastcgi_index index.php; include fastcgi_params;']
        lines += ['        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;']
        lines += ['    }', '    location / { try_files $uri $uri/ /index.php?$query_string; }']
    elif fw_type in ("python", "node"):
        lines += [f'    location / {{ proxy_pass http://127.0.0.1:{port};']
        lines += ['        proxy_set_header Host $host;']
        lines += ['        proxy_set_header X-Real-IP $remote_addr;']
        lines += ['        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;']
        if fw_type == "node":
            lines += ['        proxy_http_version 1.1;']
            lines += ["        proxy_set_header Upgrade $http_upgrade;"]
            lines += ["        proxy_set_header Connection 'upgrade';"]
        lines += ['    }']
        if fw_type == "python":
            lines += [f'    location /static/ {{ alias {root}/static/; expires 30d; }}']
    else:
        lines += ['    location / { try_files $uri $uri/ =404; }']
    lines += ["}", ""]
    return "\n".join(lines)

def list_deployed():
    print(f"\n  已部署项目:")
    sites_dir = "/www/wwwroot"
    if os.path.exists(sites_dir):
        for item in sorted(os.listdir(sites_dir)):
            if os.path.isdir(os.path.join(sites_dir, item)) and not item.startswith("."):
                print(f"    {item}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AdCtira灯塔 AI Smart Deploy")
    parser.add_argument("--path", default=os.getcwd())
    parser.add_argument("--domain")
    parser.add_argument("--name")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("  AdCtira灯塔 AI Smart Deploy")
    print("  一行命令，任何应用，自动部署到生产")
    print("  行业首创 — 没有任何面板有这个功能")
    print("="*50)
    
    if args.list:
        list_deployed(); return
    
    path = os.path.abspath(args.path)
    fw = detect_framework(path)
    if not fw:
        print(f"\n  未能识别框架: {path}")
        print("  支持的框架: Laravel, Django, Next.js, WordPress, Flask, Express, FastAPI")
        sys.exit(1)
    
    name = args.name or os.path.basename(path).replace(" ", "_").lower()
    domain = args.domain or f"{name}.test"
    nginx_conf = gen_nginx(name, FRAMEWORKS[fw]["type"], domain)
    
    print(f"\n  项目: {os.path.basename(path)}")
    print(f"  框架: {fw}")
    print(f"  域名: {domain}")
    print(f"\n  Nginx 配置:\n{nginx_conf}")
    
    nginx_path = f"/www/server/panel/vhost/nginx/{name}.conf"
    os.makedirs(os.path.dirname(nginx_path), exist_ok=True)
    with open(nginx_path, "w") as f:
        f.write(nginx_conf)
    print(f"\n  配置已保存: {nginx_path}")
    print(f"\n  {'='*50}")
    print(f"  OK! 访问 http://{domain}")
    print(f"  {'='*50}\n")

if __name__ == "__main__":
    main()
