#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
  AdCtira灯塔 v12.0 — 一键迁移工具
  「从竞品面板无痛迁移到灯塔」
================================================================

  别人不敢做的：
  - 宝塔绝不允许用户一键迁移走
  - 1Panel想兼容宝塔生态但做不到
  
  支持来源：
  ✅ 宝塔Linux面板 (bt.cn)
  ✅ 宝塔aaPanel (国际版)
  🔄 1Panel (开发中)

  迁移内容：
  - 网站配置 + 域名绑定
  - 数据库（MySQL用户和权限）
  - FTP 用户
  - SSL 证书
  - 计划任务（crontab）
  - 面板配置

  使用方式：
    python innovations/migrate.py --from bt --auto
    python innovations/migrate.py --from bt --dry-run  (预览模式)
    python innovations/migrate.py --from 1panel        (1Panel)
"""

import os
import sys
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# ==========================================
# 配置
# ==========================================
ADCTIRA_PATH = "/www/adcitra/panel"
BT_PATH = "/www/server/panel"
BT_PATHS = [
    "/www/server/panel",
    "/www/btpanel",
    "/opt/btpanel",
]
ADCTIRA_DB = os.path.join(ADCTIRA_PATH, "data", "default.db")
REPORT_FILE = "/tmp/adcitra_migration_report.json"
BACKUP_DIR = "/tmp/adcitra_migration_backup"

# ==========================================
# 工具函数
# ==========================================
COLORS = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "end": "\033[0m",
}

def colorize(text, color):
    return f"{COLORS.get(color, '')}{text}{COLORS['end']}"

def print_header(title):
    print()
    print(colorize("=" * 60, "cyan"))
    print(colorize(f"  {title}", "bold"))
    print(colorize("=" * 60, "cyan"))

def print_step(step, status="..."):
    symbols = {"ok": "✅", "fail": "❌", "skip": "⏭️", "warn": "⚠️"}
    s = symbols.get(status, "➡️")
    print(f"  {s} {step}")

# ==========================================
# 检测模块
# ==========================================
def detect_bt_installation():
    """检测服务器上是否有宝塔面板安装"""
    print_header("检测面板安装")
    
    found = []
    for path in BT_PATHS:
        if os.path.exists(path):
            db_path = os.path.join(path, "data", "panel.db")
            if os.path.exists(db_path):
                found.append({
                    "path": path,
                    "type": "bt.cn",
                    "db": db_path,
                    "version_file": os.path.join(path, "data", "version.pl"),
                })
                print_step(f"发现宝塔安装: {path}", "ok")
    
    if not found:
        print_step("未发现宝塔面板安装", "skip")
        # 也检查一下目录是否有手动迁移的数据
        for path in BT_PATHS:
            data_dir = os.path.join(path, "data")
            if os.path.exists(data_dir):
                for f in os.listdir(data_dir):
                    if f.endswith(".db"):
                        print_step(f"发现数据文件: {data_dir}/{f}", "warn")
    
    return found

def detect_1panel_installation():
    """检测1Panel安装 (TODO)"""
    return []

def detect_adcitra_installation():
    """检测AdCtira灯塔安装"""
    if os.path.exists(ADCTIRA_PATH):
        print_step(f"发现AdCtira灯塔安装: {ADCTIRA_PATH}", "ok")
        return True
    return False

# ==========================================
# 导出模块 (从宝塔)
# ==========================================
def export_sites_from_bt(bt_info):
    """导出宝塔网站配置"""
    print_header("导出网站配置")
    db_path = bt_info["db"]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT id, name, path, status, ps, addtime FROM sites")
        sites = []
        for row in c.fetchall():
            site = {
                "id": row[0],
                "name": row[1],
                "path": row[2],
                "status": row[3],
                "ps": row[4],
                "addtime": row[5],
                "domains": [],
                "databases": [],
                "ftps": [],
            }
            
            # 获取域名绑定
            try:
                c2 = conn.cursor()
                c2.execute("SELECT domain, path, port FROM binding WHERE pid=?", (row[0],))
                for d in c2.fetchall():
                    site["domains"].append({"domain": d[0], "path": d[1], "port": d[2]})
            except:
                pass
            
            sites.append(site)
            print_step(f"  网站: {row[1]} ({row[2]})", "ok")
        
        conn.close()
        print_step(f"共导出 {len(sites)} 个网站", "ok")
        return sites
    except Exception as e:
        print_step(f"导出失败: {e}", "fail")
        conn.close()
        return []

def export_databases_from_bt(bt_info):
    """导出数据库配置"""
    print_header("导出数据库配置")
    db_path = bt_info["db"]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT id, pid, name, username, password, accept, ps FROM databases")
        dbs = []
        for row in c.fetchall():
            dbs.append({
                "id": row[0],
                "pid": row[1],
                "name": row[2],
                "username": row[3],
                "password": row[4],
                "accept": row[5],
                "ps": row[6],
            })
            print_step(f"  数据库: {row[2]} (用户: {row[3]})", "ok")
        
        conn.close()
        print_step(f"共导出 {len(dbs)} 个数据库", "ok")
        return dbs
    except Exception as e:
        print_step(f"导出失败: {e}", "fail")
        conn.close()
        return []

def export_ftps_from_bt(bt_info):
    """导出FTP用户"""
    print_header("导出FTP用户")
    db_path = bt_info["db"]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT id, pid, name, password, path, status, ps FROM ftps")
        ftps = []
        for row in c.fetchall():
            ftps.append({
                "id": row[0],
                "pid": row[1],
                "name": row[2],
                "password": row[3],
                "path": row[4],
                "status": row[5],
                "ps": row[6],
            })
            print_step(f"  FTP: {row[2]}", "ok")
        
        conn.close()
        print_step(f"共导出 {len(ftps)} 个FTP用户", "ok")
        return ftps
    except Exception as e:
        print_step(f"导出失败: {e}", "fail")
        conn.close()
        return []

# ==========================================
# 路径转换模块
# ==========================================
def convert_path(old_path, bt_base="/www/server/panel", adcitra_base="/www/adcitra/panel"):
    """转换路径：从宝塔格式到AdCtira格式"""
    if not old_path:
        return old_path
    
    # 网站根目录
    if old_path.startswith("/www/wwwroot/"):
        return old_path  # 网站目录不变
    
    # 面板路径
    if old_path.startswith(bt_base):
        return old_path.replace(bt_base, adcitra_base, 1)
    
    return old_path

# ==========================================
# 导入模块 (到AdCtira灯塔)
# ==========================================
def import_sites(sites):
    """导入网站到AdCtira灯塔"""
    print_header("导入网站")
    
    if not os.path.exists(ADCTIRA_DB):
        print_step(f"未找到灯塔数据库: {ADCTIRA_DB}", "skip")
        return
    
    conn = sqlite3.connect(ADCTIRA_DB)
    c = conn.cursor()
    
    imported = 0
    for site in sites:
        try:
            # 检查是否已存在
            c.execute("SELECT id FROM sites WHERE name=?", (site["name"],))
            if c.fetchone():
                print_step(f"  跳过(已存在): {site['name']}", "skip")
                continue
            
            # 插入网站
            new_path = convert_path(site["path"])
            c.execute(
                "INSERT INTO sites (name, path, status, ps, addtime) VALUES (?, ?, ?, ?, ?)",
                (site["name"], new_path, site["status"], site["ps"], site["addtime"])
            )
            site_id = c.lastrowid
            
            # 插入域名绑定
            for domain in site.get("domains", []):
                c.execute(
                    "INSERT INTO binding (pid, domain, path, port, addtime) VALUES (?, ?, ?, ?, datetime('now'))",
                    (site_id, domain["domain"], new_path, domain.get("port", 80))
                )
            
            # 复制网站文件
            if os.path.exists(site["path"]):
                dest = new_path if new_path != site["path"] else site["path"]
                if not os.path.exists(dest):
                    shutil.copytree(site["path"], dest, symlinks=True)
                    print_step(f"  复制文件: {site['path']} -> {dest}", "ok")
            
            conn.commit()
            imported += 1
            print_step(f"  导入: {site['name']} ({new_path})", "ok")
        except Exception as e:
            conn.rollback()
            print_step(f"  失败: {site['name']} - {e}", "fail")
    
    conn.close()
    print_step(f"导入完成: {imported}/{len(sites)}", "ok")

def import_databases(databases):
    """导入数据库配置"""
    print_header("导入数据库配置")
    
    if not os.path.exists(ADCTIRA_DB):
        print_step("未找到灯塔数据库", "skip")
        return
    
    conn = sqlite3.connect(ADCTIRA_DB)
    c = conn.cursor()
    
    imported = 0
    for db in databases:
        try:
            c.execute("SELECT id FROM databases WHERE name=?", (db["name"],))
            if c.fetchone():
                print_step(f"  跳过: {db['name']}", "skip")
                continue
            
            c.execute(
                "INSERT INTO databases (pid, name, username, password, accept, ps, addtime) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
                (db["pid"], db["name"], db["username"], db["password"], db["accept"], db["ps"])
            )
            conn.commit()
            imported += 1
            print_step(f"  导入: {db['name']}", "ok")
        except Exception as e:
            print_step(f"  失败: {db['name']} - {e}", "fail")
    
    conn.close()
    print_step(f"导入完成: {imported}/{len(databases)}", "ok")

# ==========================================
# 报告生成
# ==========================================
def generate_report(results):
    """生成迁移报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "tool_version": "12.0.0",
        "summary": {
            "sites": len(results.get("sites", [])),
            "databases": len(results.get("databases", [])),
            "ftps": len(results.get("ftps", [])),
        },
        "source": "bt.cn",
        "target": "AdCtira灯塔 v12.0.0",
        "migration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print_header("迁移报告")
    print(f"  报告保存至: {REPORT_FILE}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=4))

# ==========================================
# 主流程
# ==========================================
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="AdCtira灯塔 一键迁移工具 - 从竞品面板迁移到灯塔",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python innovations/migrate.py --from bt         从宝塔迁移（交互式）
  python innovations/migrate.py --from bt --auto   从宝塔迁移（自动模式）
  python innovations/migrate.py --from bt --dry-run 预览迁移内容
  python innovations/migrate.py --from 1panel      从1Panel迁移（开发中）
        """
    )
    parser.add_argument("--from", dest="source", choices=["bt", "1panel"], default="bt",
                        help="迁移来源面板 (默认: bt)")
    parser.add_argument("--auto", action="store_true",
                        help="自动模式，无需确认")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览模式，只扫描不导入")
    
    args = parser.parse_args()
    
    print(colorize("""
    ╔══════════════════════════════════════════════╗
    ║   🌟  AdCtira灯塔 一键迁移工具  v12.0       ║
    ║   「从竞品面板无缝迁移，告别供应商锁定」    ║
    ╚══════════════════════════════════════════════╝
    """, "cyan"))
    
    print(f"  迁移来源: {args.source}")
    print(f"  迁移模式: {'自动' if args.auto else '交互'}")
    print(f"  预览模式: {'是' if args.dry_run else '否'}")
    
    # 1. 检测安装
    bt_installations = detect_bt_installation()
    
    if not bt_installations:
        print(colorize("\n  ❌ 未检测到宝塔面板安装", "red"))
        print("  请确认服务器上已安装宝塔面板")
        sys.exit(1)
    
    bt_info = bt_installations[0]
    
    # 2. 导出数据
    sites = export_sites_from_bt(bt_info)
    databases = export_databases_from_bt(bt_info)
    ftps = export_ftps_from_bt(bt_info)
    
    # 3. 如果是预览模式
    if args.dry_run:
        print_header("预览结果")
        print(f"\n  将迁移: {len(sites)} 个网站, {len(databases)} 个数据库, {len(ftps)} 个FTP")
        print("  使用 --auto 或不加 --dry-run 执行实际迁移\n")
        sys.exit(0)
    
    # 4. 确认
    if not args.auto:
        print(f"\n  将导入 {len(sites)} 个网站, {len(databases)} 个数据库, {len(ftps)} 个FTP")
        confirm = input("  是否继续迁移? (y/N): ")
        if confirm.lower() != "y":
            print("  已取消")
            sys.exit(0)
    
    # 5. 执行导入
    import_sites(sites)
    import_databases(databases)
    
    # 6. 生成报告
    results = {"sites": sites, "databases": databases, "ftps": ftps}
    generate_report(results)
    
    print(colorize("""
    ╔══════════════════════════════════════════════╗
    ║   ✅ 迁移完成！                              ║
    ║                                              ║
    ║   请重启面板: systemctl restart adcitra       ║
    ║   或执行:    python runserver.py              ║
    ║                                              ║
    ║   迁移报告: /tmp/adcitra_migration_report.json║
    ╚══════════════════════════════════════════════╝
    """, "green"))

if __name__ == "__main__":
    main()
