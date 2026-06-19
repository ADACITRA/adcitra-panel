#!/usr/bin/env python3
# AdCtira灯塔 面板 v1.0 — 纯净版
import os, sys, hashlib, secrets, subprocess
from datetime import datetime

app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)
sys.path.insert(0, os.path.join(app_dir, 'class'))

from flask import Flask, render_template, request, redirect, session, g

app = Flask(__name__, template_folder='panel/templates', static_folder='AdCtiraPanel/static')
app.secret_key = secrets.token_hex(32)

PWFILE = os.path.join(app_dir, 'data', 'admin.password')
def get_pw():
    if os.path.exists(PWFILE): return open(PWFILE).read().strip()
    pw = secrets.token_hex(6); open(PWFILE, 'w').write(pw); return pw
PW_HASH = hashlib.sha256(get_pw().encode()).hexdigest()

TEMPLATES = {
"login.html":"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AdCtira\u706f\u5854</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b1120;color:#e2e8f0;font-family:-apple-system,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}form{background:rgba(19,29,49,.95);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:40px;width:360px;text-align:center}h2{font-size:24px;font-weight:700;margin-bottom:24px}h2 .hl{background:linear-gradient(135deg,#00d4ff,#f59e0b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}input{width:100%;padding:12px;background:rgba(15,23,42,.8);border:1px solid rgba(255,255,255,.08);border-radius:8px;color:#e2e8f0;font-size:14px;outline:none}input:focus{border-color:rgba(0,212,255,.4)}button{width:100%;padding:12px;margin-top:16px;background:linear-gradient(135deg,#00d4ff,#0099cc);border:none;border-radius:8px;color:#fff;font-weight:600;cursor:pointer}.error{color:#ef4444;font-size:13px;margin-bottom:12px;padding:8px;background:rgba(239,68,68,.1);border-radius:6px}</style></head><body><form method="POST"><h2><span class="hl">AdCtira</span>\u706f\u5854</h2>{% if error %}<div class="error">{{error}}</div>{% endif %}<input type="password" name="password" placeholder="\u7ba1\u7406\u5458\u5bc6\u7801" required autofocus><button type="submit">\u767b\u5f55</button></form></body></html>""",

"layout.html":"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{g.title}} - {{"\u9762\u677f" if not title else title}}</title><link rel="stylesheet" href="/static/css/base.min.css"><link rel="stylesheet" href="/static/css/adcitra-theme.css"><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#0b1120;color:#e2e8f0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",sans-serif}.sidebar{position:fixed;top:0;left:0;width:220px;height:100vh;background:rgba(15,23,42,.95);border-right:1px solid rgba(255,255,255,.06);z-index:100;display:flex;flex-direction:column}.sidebar .logo{padding:20px;font-size:15px;font-weight:700;display:flex;align-items:center;gap:8px;border-bottom:1px solid rgba(255,255,255,.06)}.sidebar .logo .dot{width:8px;height:8px;border-radius:50%;background:#00d4ff;box-shadow:0 0 12px #00d4ff;animation:pulse 2s ease-in-out infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}.sidebar nav{padding:8px;flex:1;display:flex;flex-direction:column}.sidebar nav a{display:flex;align-items:center;gap:10px;padding:10px 14px;color:#94a3b8;text-decoration:none;border-radius:8px;font-size:14px;transition:all .15s;margin-bottom:2px}.sidebar nav a:hover,.sidebar nav a.active{background:rgba(0,212,255,.08);color:#00d4ff}.sidebar nav .spacer{flex:1}.sidebar nav .logout{border-top:1px solid rgba(255,255,255,.06);margin-top:8px;padding-top:12px}.main{margin-left:220px;padding:28px;min-height:100vh}h2{font-size:20px;font-weight:600;margin-bottom:20px;color:#e2e8f0;letter-spacing:-.3px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:28px}.card{background:rgba(19,29,49,.92);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:20px}.card .num{font-size:28px;font-weight:700;line-height:1}.card .label{color:#94a3b8;font-size:13px;margin-top:6px}.tbl{width:100%;border-collapse:collapse;font-size:13px}.tbl th,.tbl td{padding:10px 14px;text-align:left;border-bottom:1px solid rgba(255,255,255,.06)}.tbl th{color:#94a3b8;font-weight:600;font-size:11px;text-transform:uppercase;background:rgba(255,255,255,.02)}.table-wrap{background:rgba(19,29,49,.92);border:1px solid rgba(255,255,255,.06);border-radius:10px;overflow:hidden;margin-bottom:20px}.sec{margin-bottom:28px}.sec-title{font-size:15px;font-weight:600;margin-bottom:12px;color:#e2e8f0}code{background:rgba(0,0,0,.3);padding:2px 8px;border-radius:4px;font-size:13px;color:#00d4ff}pre{overflow-x:auto}</style></head><body><div class="sidebar"><div class="logo"><div class="dot"></div>AdCtira\u706f\u5854</div><nav><a href="/dashboard" class="{{'active' if request.path in ['/','/dashboard'] else ''}}">\u4eea\u8868\u76d8</a><a href="/sites" class="{{'active' if request.path=='/sites' else ''}}">\u7f51\u7ad9</a><a href="/backup" class="{{'active' if request.path=='/backup' else ''}}">\u5907\u4efd</a><div class="spacer"></div><a href="/logout" class="logout">\u9000\u51fa</a></nav></div><div class="main">{% block content %}{% endblock %}</div></body></html>""",

"dashboard.html":"""{% extends "layout.html" %}{% block content %}<h2>\u7cfb\u7edf\u6982\u89c8</h2><div class="cards"><div class="card"><div class="num" style="color:#00d4ff">{{info.cpu}}%</div><div class="label">CPU</div></div><div class="card"><div class="num" style="color:#f59e0b">{{info.memory}}%</div><div class="label">\u5185\u5b58</div></div><div class="card"><div class="num" style="color:#22c55e">{{info.disk}}%</div><div class="label">\u78c1\u76d8</div></div><div class="card"><div class="num" style="color:#a78bfa">{{"%.1f"|format(info.uptime/3600)}}h</div><div class="label">\u8fd0\u884c</div></div></div><div class="sec"><div class="sec-title">\u6302\u8f7d\u70b9</div><div class="table-wrap"><table class="tbl"><thead><tr><th>\u6302\u8f7d\u70b9</th><th>\u5927\u5c0f</th><th>\u4f7f\u7528</th><th>\u7387</th></tr></thead><tbody>{% for m in mounts %}<tr><td>{{m.mount}}</td><td>{{"%.1f"|format(m.total/1073741824)}}GB</td><td>{{"%.1f"|format(m.used/1073741824)}}GB</td><td>{{m.percent}}%</td></tr>{% endfor %}</tbody></table></div></div><div class="sec"><div class="sec-title">\u7ad9\u70b9 ({{sites|length}})</div><div class="table-wrap"><table class="tbl"><thead><tr><th>\u540d\u79f0</th><th>\u8def\u5f84</th></tr></thead><tbody>{% for s in sites %}<tr><td><strong>{{s.name}}</strong></td><td style="color:#94a3b8">{{s.path}}</td></tr>{% else %}<tr><td colspan="2" style="text-align:center;color:#64748b;padding:32px">\u6682\u65e0\u7ad9\u70b9</td></tr>{% endfor %}</tbody></table></div></div>{% endblock %}""",

"sites.html":"""{% extends "layout.html" %}{% block content %}<h2>\u7f51\u7ad9\u7ba1\u7406</h2><div class="table-wrap"><table class="tbl"><thead><tr><th>\u540d\u79f0</th><th>\u8def\u5f84</th><th>\u5927\u5c0f</th></tr></thead><tbody>{% for s in sites %}<tr><td><strong>{{s.name}}</strong></td><td style="color:#94a3b8">{{s.path}}</td><td>{{s.size}}</td></tr>{% else %}<tr><td colspan="3" style="text-align:center;color:#64748b;padding:32px">\u6682\u65e0\u7f51\u7ad9</td></tr>{% endfor %}</tbody></table></div>{% endblock %}""",

"backup.html":"""{% extends "layout.html" %}{% block content %}<h2>\u5907\u4efd\u670d\u52a1</h2><div class="card" style="max-width:600px"><p style="margin-bottom:12px;font-size:14px">\u670d\u52a1\u5730\u5740: <code>https://backup.adacitra.cloud</code></p><p style="margin-bottom:8px;font-size:14px">\u5907\u4efd\u547d\u4ee4:</p><pre style="background:#030712;border:1px solid rgba(0,212,255,.08);border-radius:8px;padding:16px;font-size:13px;line-height:1.9;overflow-x:auto"><span style="color:#f59e0b">$</span> <span style="color:#e2e8f0">python innovations/dataport.py backup</span>\n<span style="color:#22c55e">OK \u5907\u4efd\u5b8c\u6210</span>\n<span style="color:#f59e0b">$</span> <span style="color:#e2e8f0">python innovations/dataport.py remote list</span>\n<span style="color:#22c55e">... \u5217\u51fa\u6240\u6709\u5907\u4efd ...</span></pre></div>{% endblock %}""",
}

def _write_templates():
    td = os.path.join(app_dir, 'panel', 'templates')
    os.makedirs(td, exist_ok=True)
    for name, content in TEMPLATES.items():
        fp = os.path.join(td, name)
        if not os.path.exists(fp):
            with open(fp, 'w', encoding='utf-8') as f: f.write(content)

@app.before_request
def before():
    g.title = 'AdCtira\u706f\u5854'
    g.panel_theme = {'logo': {'favicon': '/static/favicon.ico'}}
    if request.path.startswith('/static/') or request.path == '/login': return
    if not session.get('login'): return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if hashlib.sha256(request.form['password'].encode()).hexdigest() == PW_HASH:
            session['login'] = True; return redirect('/dashboard')
        return render_template('login.html', error='\u5bc6\u7801\u9519\u8bef')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

@app.route('/')
@app.route('/dashboard')
def dashboard():
    import psutil
    info = {'cpu': psutil.cpu_percent(interval=0.3), 'memory': psutil.virtual_memory().percent, 'disk': psutil.disk_usage('/').percent, 'uptime': datetime.now().timestamp() - psutil.boot_time(), 'hostname': os.uname().nodename if hasattr(os,'uname') else 'localhost'}
    mounts = []
    for m in ['/','/www','/www/wwwroot','/data']:
        try: u=psutil.disk_usage(m); mounts.append({'mount':m,'total':u.total,'used':u.used,'percent':u.percent})
        except: pass
    sites = []
    if os.path.exists('/www/wwwroot'):
        for d in sorted(os.listdir('/www/wwwroot')):
            p=os.path.join('/www/wwwroot',d)
            if os.path.isdir(p) and not d.startswith('.'): sites.append({'name':d,'path':p})
    return render_template('dashboard.html', info=info, mounts=mounts, sites=sites, title='\u4eea\u8868\u76d8')

@app.route('/sites')
def sites():
    sl=[]
    if os.path.exists('/www/wwwroot'):
        for d in sorted(os.listdir('/www/wwwroot')):
            p=os.path.join('/www/wwwroot',d)
            if os.path.isdir(p) and not d.startswith('.'):
                try: r=subprocess.run(['du','-sh',p],capture_output=True,text=True,timeout=5); size=r.stdout.split()[0] if r.stdout else'?'
                except: size='?'
                sl.append({'name':d,'path':p,'size':size})
    return render_template('sites.html', sites=sl, title='\u7f51\u7ad9\u7ba1\u7406')

@app.route('/backup')
def backup():
    return render_template('backup.html', title='\u5907\u4efd')

@app.route('/static/<path:f>')
def st(f):
    return send_from_directory('AdCtiraPanel/static', f)

if __name__ == '__main__':
    _write_templates()
    pw = get_pw()
    print(f'\n  AdCtira\u706f\u5854 \u9762\u677f v1.0')
    print(f'  \u767b\u5f55: http://localhost:8888/login')
    print(f'  \u5bc6\u7801: {pw}')
    print(f'  \u9762\u677f\u5df2\u542f\u52a8, \u8bb0\u5f97\u653e\u884c\u9632\u706b\u5899 8888 \u7aef\u53e3\n')
    app.run(host='0.0.0.0', port=8888)
