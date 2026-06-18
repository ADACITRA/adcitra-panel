#coding: utf-8
"""部署管理模块 — 集成到面板 /deploy 路由"""
import os, json, subprocess, threading, shlex, re
from pathlib import Path

CONFIG_DIR = Path.home() / ".adcitra"
DEPLOYS_FILE = CONFIG_DIR / "deployments.json"

def load_deploys():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DEPLOYS_FILE.exists():
        DEPLOYS_FILE.write_text("[]")
    return json.loads(DEPLOYS_FILE.read_text())

def save_deploys(d):
    DEPLOYS_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False))

def _sanitize_name(s):
    return re.sub(r'[^a-zA-Z0-9_\-]', '', s)

def deploy_git(repo_url, branch="main", name=""):
    name = _sanitize_name(name or repo_url.rstrip("/").split("/")[-1].replace(".git",""))
    preview = branch not in ("main","master") and len(branch) < 100
    dn = f"{name}-{branch}" if preview else name
    dd = f"/www/wwwroot/{dn}"
    
    if os.path.exists(dd):
        subprocess.run(f"cd {dd} && git pull origin {branch}", shell=True, capture_output=True, timeout=60)
    else:
        r = subprocess.run(f"git clone --branch {branch} {repo_url} {dd}", shell=True, capture_output=True, timeout=120)
        if r.returncode != 0:
            return {"status":"failed","error":r.stderr.decode()[:200]}
    
    domain = f"{dn}.test"
    port = sum(ord(c) for c in dn) % 1000 + 8000
    os.makedirs("/www/server/panel/vhost/nginx", exist_ok=True)
    dn = _sanitize_name(dn)
    nc = f"""server {{
    listen 80;
    server_name {domain};
    root {dd};
    index index.html index.htm index.php;
    access_log /www/wwwlogs/{dn}.log;
    error_log /www/wwwlogs/{dn}.error.log;
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }}
}}
"""
    Path(f"/www/server/panel/vhost/nginx/{dn}.conf").write_text(nc)
    r = {"name":name,"deploy_name":dn,"branch":branch,"domain":domain,
         "preview":preview,"status":"live","framework":"auto",
         "deployed_at":__import__("datetime").datetime.now().isoformat()}
    d = load_deploys(); d.append(r); save_deploys(d)
    return {"status":"live","url":f"http://{domain}","name":dn}

def register_deploy_routes(app):
    import public
    from flask import request, render_template
    
    @app.route("/deploy", methods=["GET","POST"])
    @app.route("/deploy/<action>", methods=["GET","POST"])
    def deploy_route(action=None):
        if request.method == "POST":
            if action == "webhook":
                data = request.get_json()
                if data and "repository" in data:
                    repo = data["repository"]["clone_url"]
                    branch = data.get("ref","refs/heads/main").replace("refs/heads/","")
                    name = data["repository"]["name"]
                    t = threading.Thread(target=deploy_git, args=(repo,branch,name))
                    t.start()
                    return public.returnMsg(True, {"status":"accepted","msg":"部署已开始"})
            elif action == "manual":
                repo = request.form.get("repo","")
                branch = request.form.get("branch","main")
                name = request.form.get("name","")
                result = deploy_git(repo, branch, name)
                return public.returnMsg(True, result)
            return public.returnMsg(False, "未知操作")
        deploys = load_deploys()
        stats = {"total":len(deploys),"live":0,"preview":0}
        for d in deploys:
            if d.get("status") == "live": stats["live"] += 1
            if d.get("preview"): stats["preview"] += 1
        return render_template("deploy.html", data={"deploys":deploys[-50:],"stats":stats})
    
    @app.route("/deploy/api/list", methods=["GET"])
    def deploy_api_list():
        return public.returnMsg(True, {"deploys":load_deploys()[-50:]})
