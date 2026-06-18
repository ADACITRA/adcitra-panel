#!/usr/bin/env python3
"""AdCtira Backup Server — 云备份服务端
python server/backup_server.py --port 7890 --token your-key
"""
import os, json, hashlib
from flask import Flask, request, jsonify, send_file
from datetime import datetime

app = Flask(__name__)
DATA_DIR = os.environ.get("AD_BACKUP_DIR", "/data/adcitra-backups")
TOKENS = os.environ.get("AD_TOKENS", "admin").split(",")

def auth():
    t = request.headers.get("X-Token", "")
    if t not in TOKENS:
        return jsonify({"error":"unauthorized"}), 401
    return None

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "X-Token,Content-Type"
    return r

@app.route("/api/backup", methods=["POST","OPTIONS"])
def upload():
    if request.method == "OPTIONS": return jsonify({})
    auth()
    cid = hashlib.sha256(request.headers["X-Token"].encode()).hexdigest()[:16]
    cd = os.path.join(DATA_DIR, cid)
    os.makedirs(cd, exist_ok=True)
    f = request.files.get("file")
    if not f: return jsonify({"error":"no file"}), 400
    name = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.enc"
    f.save(os.path.join(cd, name))
    mf = os.path.join(cd, "manifest.json")
    ml = json.load(open(mf)) if os.path.exists(mf) else []
    ml.append({"id":name.replace(".enc",""),"file":name,"size":os.path.getsize(os.path.join(cd,name)),"created_at":datetime.now().isoformat()})
    json.dump(ml, open(mf,"w"), indent=2, ensure_ascii=False)
    return jsonify({"id":name.replace(".enc","")})

@app.route("/api/backup", methods=["GET"])
def ls():
    auth()
    cid = hashlib.sha256(request.headers["X-Token"].encode()).hexdigest()[:16]
    mf = os.path.join(DATA_DIR, cid, "manifest.json")
    return jsonify({"backups":json.load(open(mf)) if os.path.exists(mf) else []})

@app.route("/api/backup/<bid>", methods=["GET"])
def dl(bid):
    auth()
    cid = hashlib.sha256(request.headers["X-Token"].encode()).hexdigest()[:16]
    p = os.path.join(DATA_DIR, cid, f"{bid}.enc")
    if not os.path.exists(p): return jsonify({"error":"not found"}), 404
    return send_file(p, as_attachment=True, download_name=f"{bid}.enc")

@app.route("/api/backup/<bid>", methods=["DELETE"])
def rm(bid):
    auth()
    cid = hashlib.sha256(request.headers["X-Token"].encode()).hexdigest()[:16]
    p = os.path.join(DATA_DIR, cid, f"{bid}.enc")
    if os.path.exists(p): os.remove(p)
    mf = os.path.join(DATA_DIR, cid, "manifest.json")
    if os.path.exists(mf):
        ml = [m for m in json.load(open(mf)) if m["id"] != bid]
        json.dump(ml, open(mf,"w"), indent=2, ensure_ascii=False)
    return jsonify({"status":"deleted"})

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=7890)
    p.add_argument("--data-dir")
    p.add_argument("--token")
    a = p.parse_args()
    if a.data_dir: DATA_DIR = a.data_dir
    if a.token: TOKENS = [a.token]
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"\n  AdCtira Backup Server")
    print(f"  Port: {a.port}")
    print(f"  Data: {DATA_DIR}")
    print(f"  Token: {TOKENS[0]}\n")
    from waitress import serve
    serve(app, host="0.0.0.0", port=a.port)
