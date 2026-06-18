#!/bin/bash
set -e
PORT="${1:-7890}"
TOKEN="${2:-backup_admin_$(openssl rand -hex 8)}"
DOMAIN="${3:-backup.adcitra.cn}"
DIR="/opt/adcitra-backup"
DATA="/data/adcitra-backups"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "  AdCtira Backup Server Installer"
echo "  ==============================="
echo "  Port: $PORT"
echo "  Token: $TOKEN"
echo "  Domain: $DOMAIN"
echo ""

# 1. OS detection
if [ -f /etc/debian_version ]; then
    apt-get update -qq && apt-get install -y -qq python3-pip nginx certbot python3-certbot-nginx
elif [ -f /etc/redhat-release ]; then
    yum install -y -q python3-pip nginx certbot python3-certbot-nginx
fi

# 2. Python deps
pip3 install flask waitress pycryptodome requests 2>/dev/null || pip install flask waitress pycryptodome requests

# 3. Create dirs
mkdir -p "$DIR" "$DATA"

# 4. Copy server code
cp "$SCRIPT_DIR/../server/backup_server.py" "$DIR/"

# 5. Systemd service
cat > /etc/systemd/system/adcitra-backup.service << EOF
[Unit]
Description=AdCtira Backup Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 $DIR/backup_server.py --port $PORT --token $TOKEN --data-dir $DATA
Restart=always
RestartSec=5
Environment=AD_BACKUP_DIR=$DATA
Environment=AD_TOKENS=$TOKEN

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adcitra-backup
systemctl start adcitra-backup

# 6. Nginx
cat > /etc/nginx/sites-available/adcitra-backup << 'NGINX'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    location / {
        proxy_pass http://127.0.0.1:PORT_PLACEHOLDER;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 0;
        proxy_request_buffering off;
    }
}
NGINX

sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/adcitra-backup
sed -i "s/PORT_PLACEHOLDER/$PORT/g" /etc/nginx/sites-available/adcitra-backup
ln -sf /etc/nginx/sites-available/adcitra-backup /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 7. Test
sleep 2
curl -s http://127.0.0.1:$PORT/health > /dev/null && echo "  OK: server running" || echo "  FAIL: server not running"

echo ""
echo "  ======================== ???? ========================"
echo "  AdCtira Backup Server"
echo "  URL: https://$DOMAIN"
echo "  Token: $TOKEN"
echo ""
echo "  ????? (????????????):"
echo "  cd /path/to/adcitra-panel"
echo "  python innovations/dataport.py remote config"
echo "  ???: https://$DOMAIN"
echo "  Token: $TOKEN"
echo ""
echo "  ????:"
echo "  python innovations/dataport.py backup"
echo "  ========================================================="
