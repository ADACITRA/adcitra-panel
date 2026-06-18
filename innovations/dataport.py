#!/usr/bin/env python3
"""
AdCtira DataPort — 数据随身带
一键导出/导入全部数据，服务器到期不丢任何东西

用法:
  python innovations/dataport.py export             导出全部数据
  python innovations/dataport.py export --dest /mnt/backup 导出到指定目录
  python innovations/dataport.py import backup.tar.gz  导入恢复
  python innovations/dataport.py list                查看备份列表
"""

import os, sys, json, tarfile, gzip, shutil, subprocess
from datetime import datetime
from pathlib import Path

BACKUP_DIR = "/www/backup/adcitra"
PANEL_PATH = "/www/adcitra/panel"
SITES_DIR = "/www/wwwroot"
VHOST_DIR = "/www/server/panel/vhost"
NGINX_DIR = "/www/server/panel/vhost/nginx"
CERT_DIR = "/www/server/panel/vhost/cert"

C = {"g":"\033[92m","y":"\033[93m","r":"\033[91m","c":"\033[96m","b":"\033[1m","e":"\033[0m"}
def cl(text,c): return f"{C.get(c,'')}{text}{C['e']}"

def header(t):
    print(f"\n  {cl('==>','c')} {cl(t,'b')}")

def ok(m):
    print(f"  {cl('OK','g')}  {m}")

def warn(m):
    print(f"  {cl('WARN','y')} {m}")

def fail(m):
    print(f"  {cl('ERR','r')} {m}")

# ==========================================
# 导出引擎
# ==========================================
def do_export(dest_dir=None):
    """导出全部数据"""
    dest = dest_dir or BACKUP_DIR
    os.makedirs(dest,exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_name = f"adcitra-backup-{ts}.tar.gz"
    archive_path = os.path.join(dest,archive_name)

    manifest = {
        "tool":"AdCtira DataPort",
        "version":"1.0",
        "created_at":datetime.now().isoformat(),
        "content":{},
        "file_count":0,
        "total_size":0,
    }

    print(f"\n  {cl('DataPort','c')} — 导出全部数据")
    print(f"  备份文件: {archive_path}\n")

    # 创建临时目录
    tmp = f"/tmp/adcitra-export-{ts}"
    os.makedirs(tmp,exist_ok=True)

    # 1. 导出面板配置 (SQLite)
    header("导出面板配置")
    db_path = os.path.join(PANEL_PATH,"data","default.db")
    system_db = os.path.join(PANEL_PATH,"data","system.db")
    config_dir = os.path.join(PANEL_PATH,"config")

    db_tmp = os.path.join(tmp,"panel")
    os.makedirs(db_tmp,exist_ok=True)

    if os.path.exists(db_path):
        shutil.copy2(db_path,os.path.join(db_tmp,"default.db"))
        manifest["content"]["panel_db"] = True
        ok("面板数据库")

    if os.path.exists(system_db):
        shutil.copy2(system_db,os.path.join(db_tmp,"system.db"))
        manifest["content"]["system_db"] = True
        ok("系统数据库")

    if os.path.exists(config_dir):
        shutil.copytree(config_dir,os.path.join(tmp,"config"),dirs_exist_ok=True)
        manifest["content"]["config"] = True
        ok("配置文件")

    # 2. 导出网站文件
    header("导出网站文件")
    if os.path.exists(SITES_DIR):
        sites_tmp = os.path.join(tmp,"sites")
        count = 0
        for item in os.listdir(SITES_DIR):
            item_path = os.path.join(SITES_DIR,item)
            if os.path.isdir(item_path) and not item.startswith("."):
                shutil.copytree(item_path,os.path.join(sites_tmp,item),dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("node_modules",".git","__pycache__","cache"))
                count += 1
                print(f"    {item}")
        manifest["content"]["sites_count"] = count
        ok(f"网站文件 ({count}个)")

    # 3. 导出 Nginx vhost 配置
    header("导出服务器配置")
    if os.path.exists(NGINX_DIR):
        shutil.copytree(NGINX_DIR,os.path.join(tmp,"nginx"),dirs_exist_ok=True)
        manifest["content"]["nginx_configs"] = True
        ok("Nginx 配置")

    # 4. 导出 SSL 证书
    if os.path.exists(CERT_DIR):
        cert_tmp = os.path.join(tmp,"ssl")
        count = 0
        for item in os.listdir(CERT_DIR):
            item_path = os.path.join(CERT_DIR,item)
            if os.path.isdir(item_path):
                shutil.copytree(item_path,os.path.join(cert_tmp,item),dirs_exist_ok=True)
                count += 1
        manifest["content"]["ssl_certs"] = count
        ok(f"SSL 证书 ({count}个)")

    # 5. 导出 MySQL 数据库
    header("导出数据库")
    try:
        result = subprocess.run(
            "mysql -e 'SHOW DATABASES' 2>/dev/null | grep -v 'Database\\|information_schema\\|performance_schema\\|mysql\\|sys'",
            shell=True,capture_output=True,text=True,timeout=10
        )
        if result.stdout.strip():
            dbs = result.stdout.strip().split("\n")
            db_tmp_dir = os.path.join(tmp,"databases")
            os.makedirs(db_tmp_dir,exist_ok=True)
            for db in dbs:
                db = db.strip()
                if db:
                    dump_file = os.path.join(db_tmp_dir,f"{db}.sql")
                    subprocess.run(
                        f"mysqldump --skip-lock-tables {db} > {dump_file}",
                        shell=True,capture_output=True,timeout=120
                    )
                    if os.path.exists(dump_file) and os.path.getsize(dump_file) > 0:
                        print(f"    {db}")
            manifest["content"]["databases"] = len(dbs)
            ok(f"数据库 ({len(dbs)}个)")
        else:
            manifest["content"]["databases"] = 0
            warn("未发现 MySQL 数据库（或未安装 MySQL）")
    except Exception as e:
        manifest["content"]["databases"] = 0
        warn(f"数据库导出跳过: {e}")

    # 6. 保存 manifest
    with open(os.path.join(tmp,"manifest.json"),"w",encoding="utf-8") as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)

    # 7. 打包
    header("打包压缩")
    with tarfile.open(archive_path,"w:gz") as tar:
        tar.add(tmp,arcname="")
    
    # 统计
    total_size = os.path.getsize(archive_path)
    manifest["total_size"] = total_size
    with open(os.path.join(tmp,"manifest.json"),"w",encoding="utf-8") as f:
        json.dump(manifest,f,ensure_ascii=False,indent=2)

    # 清理临时目录
    shutil.rmtree(tmp,ignore_errors=True)

    print(f"\n  {cl('='*50,'g')}")
    print(f"  {cl('导出完成!','b')}")  
    print(f"  文件: {archive_path}")
    print(f"  大小: {total_size/1024/1024:.1f} MB")
    print(f"  命令: python innovations/dataport.py import {archive_path}")
    print(f"  {cl('='*50,'g')}\n")
    
    return archive_path


# ==========================================
# 导入引擎
# ==========================================
def do_import(archive_path):
    """从备份文件导入恢复"""
    if not os.path.exists(archive_path):
        fail(f"备份文件不存在: {archive_path}")
        sys.exit(1)

    print(f"\n  {cl('DataPort','c')} — 导入恢复")
    print(f"  文件: {archive_path}\n")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    tmp = f"/tmp/adcitra-restore-{ts}"
    os.makedirs(tmp,exist_ok=True)

    # 解压
    header("解压备份文件")
    with tarfile.open(archive_path,"r:gz") as tar:
        tar.extractall(tmp)
    ok("解压完成")

    # 读取 manifest
    manifest_path = os.path.join(tmp,"manifest.json")
    if not os.path.exists(manifest_path):
        fail("无效的备份文件（缺少 manifest.json）")
        sys.exit(1)
    with open(manifest_path,"r",encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"  备份时间: {manifest.get('created_at','unknown')}")

    # 1. 恢复面板配置
    header("恢复面板配置")
    panel_backup = os.path.join(tmp,"panel")
    if os.path.exists(panel_backup):
        for f in ["default.db","system.db"]:
            src = os.path.join(panel_backup,f)
            dst = os.path.join(PANEL_PATH,"data",f)
            if os.path.exists(src):
                shutil.copy2(src,dst)
                print(f"    {f}")
        ok("面板配置已恢复")

    config_backup = os.path.join(tmp,"config")
    if os.path.exists(config_backup):
        dst = os.path.join(PANEL_PATH,"config")
        for item in os.listdir(config_backup):
            shutil.copy2(os.path.join(config_backup,item),os.path.join(dst,item))
        ok("配置文件已恢复")

    # 2. 恢复网站文件
    sites_backup = os.path.join(tmp,"sites")
    if os.path.exists(sites_backup):
        header("恢复网站文件")
        count = 0
        for item in os.listdir(sites_backup):
            src = os.path.join(sites_backup,item)
            dst = os.path.join(SITES_DIR,item)
            if os.path.exists(dst):
                warn(f"  跳过（已存在）: {item}")
            else:
                shutil.copytree(src,dst)
                count += 1
                print(f"    {item}")
        ok(f"已恢复 {count} 个网站")

    # 3. 恢复 Nginx 配置
    nginx_backup = os.path.join(tmp,"nginx")
    if os.path.exists(nginx_backup):
        header("恢复 Nginx 配置")
        os.makedirs(NGINX_DIR,exist_ok=True)
        count = 0
        for item in os.listdir(nginx_backup):
            shutil.copy2(os.path.join(nginx_backup,item),os.path.join(NGINX_DIR,item))
            count += 1
        ok(f"已恢复 {count} 个配置")

    # 4. 恢复 SSL 证书
    ssl_backup = os.path.join(tmp,"ssl")
    if os.path.exists(ssl_backup):
        header("恢复 SSL 证书")
        os.makedirs(CERT_DIR,exist_ok=True)
        count = 0
        for item in os.listdir(ssl_backup):
            src = os.path.join(ssl_backup,item)
            dst = os.path.join(CERT_DIR,item)
            if os.path.isdir(src):
                shutil.copytree(src,dst,dirs_exist_ok=True)
                count += 1
        ok(f"已恢复 {count} 个证书")

    # 5. 恢复数据库
    db_backup = os.path.join(tmp,"databases")
    if os.path.exists(db_backup):
        header("恢复数据库")
        count = 0
        for item in os.listdir(db_backup):
            if item.endswith(".sql"):
                db_name = item.replace(".sql","")
                try:
                    subprocess.run(f"mysql -e 'CREATE DATABASE IF NOT EXISTS {db_name}'",shell=True,capture_output=True,timeout=10)
                    subprocess.run(f"mysql {db_name} < {os.path.join(db_backup,item)}",shell=True,capture_output=True,timeout=300)
                    count += 1
                    print(f"    {db_name}")
                except Exception as e:
                    warn(f"  {db_name}: {e}")
        ok(f"已恢复 {count} 个数据库")

    # 清理
    shutil.rmtree(tmp,ignore_errors=True)

    print(f"\n  {cl('='*50,'g')}")
    print(f"  {cl('恢复完成!','b')}")
    print(f"  建议重启面板: systemctl restart adcitra")
    print(f"  {cl('='*50,'g')}\n")


# ==========================================
# 备份列表
# ==========================================
def list_backups():
    """列出所有备份"""
    if not os.path.exists(BACKUP_DIR):
        print(f"\n  暂无备份 ({BACKUP_DIR})")
        return
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")],reverse=True)
    if not backups:
        print(f"\n  暂无备份 ({BACKUP_DIR})")
        return
    
    print(f"\n  {cl('备份列表','b')}")
    print(f"  目录: {BACKUP_DIR}\n")
    total_size = 0
    for b in backups:
        path = os.path.join(BACKUP_DIR,b)
        size = os.path.getsize(path)
        total_size += size
        # Try to read manifest
        try:
            with tarfile.open(path,"r:gz") as tar:
                mf = tar.extractfile("manifest.json")
                if mf:
                    m = json.loads(mf.read())
                    created = m.get("created_at","")[:19].replace("T"," ")
                else:
                    created = "unknown"
        except:
            created = "unknown"
        print(f"  {b}")
        print(f"     大小: {size/1024/1024:.1f} MB | 时间: {created}")
    
    print(f"\n  共 {len(backups)} 个备份, 总计 {total_size/1024/1024:.1f} MB")


# ==========================================
# 主入口
# ==========================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="AdCtira DataPort — 数据随身带")
    sub = parser.add_subparsers(dest="cmd")

    p_e = sub.add_parser("export",help="导出全部数据")
    p_e.add_argument("--dest","-d",default=BACKUP_DIR,help="保存目录")

    p_i = sub.add_parser("import",help="从备份恢复")
    p_i.add_argument("file",help="备份文件路径")

    _ = sub.add_parser("list",help="查看备份列表")

    args = parser.parse_args()

    if args.cmd == "export":
        do_export(args.dest)
    elif args.cmd == "import":
        do_import(args.file)
    elif args.cmd == "list":
        list_backups()
    else:
        parser.print_help()

if __name__ == "__main__":
    print(f"""
  {cl('╔══════════════════════════════════════╗','c')}
  {cl('║','c')}  AdCtira DataPort — 数据随身带  {cl('║','c')}
  {cl('║','c')}  服务器到期？不丢任何数据       {cl('║','c')}
  {cl('╚══════════════════════════════════════╝','c')}  
""")
    main()
