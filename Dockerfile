# ============================================
# AdCtira灯塔 面板 - Docker 镜像
# 基于宝塔Linux面板复刻
# ============================================

FROM python:3.11-slim

LABEL maintainer="AdCtira Team <team@adcitra.cn>"
LABEL description="AdCtira灯塔 - 服务器运维面板 Docker 镜像"
LABEL version="12.0.0"

WORKDIR /www/adcitra/panel

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    nginx-light \
    supervisor \
    cron \
    openssl \
    ca-certificates \
    procps \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制面板源码
COPY . /www/adcitra/panel

# 安装 Python 依赖
RUN pip install --no-cache-dir -r /www/adcitra/panel/requirements.txt 2>/dev/null || \
    pip install --no-cache-dir flask flask-sock flask-session flask-compress \
        psutil requests paramiko pycryptodome Pillow qrcode gevent pyyaml \
        bcrypt certifi cffi chardet configparser cryptography dnspython \
        docker idna IPy Jinja2 MarkupSafe oauthlib packaging pycparser \
        pymysql PyNaCl pyOpenSSL pyparsing redis rsa six Werkzeug && \
    echo "依赖安装完成"

# 创建必要目录
RUN mkdir -p /www/server \
    /www/wwwlogs \
    /www/adcitra/panel/logs \
    /www/adcitra/panel/data \
    /var/log/supervisor \
    /var/run

# 复制 Supervisor 配置
COPY docker/supervisord.conf /etc/supervisor/conf.d/adcitra.conf

# 暴露端口
EXPOSE 8888 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/ || exit 1

# 启动入口
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
