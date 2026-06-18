#!/usr/bin/env python3
"""AdCtira Webhook — Git 自动部署接收器 + 部署仪表盘"""
import os, sys, json, hmac, hashlib, subprocess, threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

CONFIG_DIR = Path.home() / ".adcitra"
DEPLOYS_FILE = CONFIG_DIR / "deployments.json"

def load_deploys():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not DEPLOYS_FILE.exists():
        DEPLOYS_FILE.write_text("[]")
    return json.loads(DEPLOYS_FILE.read_text())

def save_deploys(d):
    DEPLOYS_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False))

def deploy_git(repo_url, branch="main", name=""):
    name = name or repo_url.rstrip("/").split("/")[-1].replace(".git","")
    preview = branch not in ("main","master")
    dn = f"{name}-{branch}" if preview else name
    dd = f"/www/wwwroot/{dn}"
    print(f"  deploy: {name} ({branch})")

    if os.path.exists(dd):
        subprocess.run(f"cd {dd} && git pull origin {branch}", shell=True, capture_output=True, timeout=60)
    else:
        r = subprocess.run(f"git clone --branch {branch} {repo_url} {dd}", shell=True, capture_output=True, timeout=120)
        if r.returncode != 0: return {"status":"failed"}

    domain = f"{dn}.test"
    port = sum(ord(c) for c in dn) % 1000 + 8000
    os.makedirs("/www/server/panel/vhost/nginx", exist_ok=True)
    nc = f"""server {{
    listen 80; server_name {domain};
    root {dd}; index index.html index.htm index.php;
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
         "preview":preview,"status":"live",
         "deployed_at":datetime.now().isoformat()}
    d = load_deploys(); d.append(r); save_deploys(d)
    print(f"  OK: http://{domain}")
    return {"status":"live","url":f"http://{domain}"}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/deployments":
            self.send_response(200)
            self.send_header("Content-type","application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(load_deploys()[-50:], ensure_ascii=False, indent=2).encode("utf-8"))
            return
        
        # Dashboard HTML
        html = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AdCtira 部署仪表盘</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,system-ui,sans-serif;background:#0f172a;color:#e2e8f0;padding:20px}
h1{font-size:1.5rem;margin-bottom:20px;display:flex;align-items:center;gap:10px}
h1 span{background:#f59e0b;color:#0f172a;padding:2px 10px;border-radius:999px;font-size:.75rem;font-weight:700}
.stats{display:flex;gap:20px;margin-bottom:24px;flex-wrap:wrap}
.stat{padding:16px 24px;background:#1e293b;border-radius:12px;border:1px solid #334155}
.stat .num{font-size:1.8rem;font-weight:700;color:#f59e0b}
.stat .label{font-size:.8rem;color:#64748b;margin-top:4px}
table{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid #334155;font-size:.85rem}
th{background:#0f172a;color:#94a3b8;font-weight:600;text-transform:uppercase;font-size:.75rem}
.live{color:#22c55e;font-weight:600}
.preview{color:#3b82f6;font-weight:600}
.failed{color:#ef4444;font-weight:600}
a{color:#f59e0b;text-decoration:none}
a:hover{text-decoration:underline}
.time{color:#64748b;font-size:.8rem}
.empty{text-align:center;padding:60px;color:#64748b}
.empty code{background:#1e293b;padding:4px 12px;border-radius:6px;display:inline-block;margin-top:12px}
@media(max-width:640px){th,td{padding:8px 10px;font-size:.75rem}}
</style></head>
<body>
<h1>AdCtira <span>Deploy Dashboard</span></h1>
<div class="stats" id="stats">
  <div class="stat"><div class="num" id="total">-</div><div class="label">总部署</div></div>
  <div class="stat"><div class="num" id="live">-</div><div class="label">运行中</div></div>
  <div class="stat"><div class="num" id="preview">-</div><div class="label">预览中</div></div>
</div>
<table><thead><tr>
  <th>应用</th><th>分支</th><th>框架</th><th>域名</th><th>状态</th><th>时间</th>
</tr></thead><tbody id="deploys"></tbody></table>
<script>
async function load(){try{
  const r=await fetch('/deployments');const d=await r.json();
  const tbody=document.getElementById('deploys');tbody.innerHTML='';
  if(!d.length){tbody.innerHTML='<tr><td colspan="6" class="empty">暂无部署<code>adcitra deploy</code></td></tr>';return}
  let live=0,preview=0;
  d.slice().reverse().forEach(a=>{
    if(a.status=='live')live++;if(a.preview)preview++;
    const tr=document.createElement('tr');
    tr.innerHTML='<td><strong>'+a.name+'</strong></td>'+
      '<td>'+(a.branch||'main')+'</td>'+
      '<td>'+a.framework+'</td>'+
      '<td><a href="http://'+a.domain+'" target="_blank">'+a.domain+'</a></td>'+
      '<td class="'+(a.status||'live')+'">'+(a.preview?'preview':'live')+'</td>'+
      '<td class="time">'+(a.deployed_at||'').slice(0,19).replace('T',' ')+'</td>';
    tbody.appendChild(tr);
  });
  document.getElementById('total').textContent=d.length;
  document.getElementById('live').textContent=live;
  document.getElementById('preview').textContent=preview;
}catch(e){document.getElementById('deploys').innerHTML='<tr><td colspan="6" class="empty">无法加载部署数据</td></tr>'}
load();setInterval(load,10000);
</script></body></html>"""
        self.send_response(200)
        self.send_header("Content-type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    
    def do_POST(self):
        if self.path != "/webhook":
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length)
        try:
            p = json.loads(body)
            repo = p.get("repository",{}).get("clone_url","")
            ref = p.get("ref","refs/heads/main")
            branch = ref.replace("refs/heads/","")
            name = p.get("repository",{}).get("name","")
            print(f"  push: {name} ({branch})")
            t = threading.Thread(target=lambda: deploy_git(repo, branch, name))
            t.start()
            self.send_response(202)
            self.send_header("Content-type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"accepted"}).encode())
        except Exception as e:
            self.send_response(500); self.end_headers()
            self.wfile.write(json.dumps({"error":str(e)}).encode())
    def log_message(self,*a): pass

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=9999)
    a = p.parse_args()
    s = HTTPServer(("0.0.0.0",a.port), Handler)
    print(f"\n  AdCtira Webhook + Dashboard")
    print(f"  端口: {a.port}")
    print(f"  Webhook: POST /webhook")
    print(f"  Dashboard: http://localhost:{a.port}/\n")
    try: s.serve_forever()
    except KeyboardInterrupt: print("  stopped")
