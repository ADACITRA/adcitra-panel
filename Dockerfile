# ================================
# AdCtira\u706f\u5854 \u9762\u677f - Docker \u955c\u50cf
# ================================

FROM python:3.11-slim

LABEL maintainer=\"AdCtira Team <team@adcitra.cn>\"
LABEL description=\"AdCtira\u706f\u5854 - \u81ea\u6258\u7ba1\u90e8\u7f72\u5e73\u53f0\"
LABEL version=\"1.0.0\"

WORKDIR /app

# \u5b89\u88c5\u7cfb\u7edf\u4f9d\u8d56
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    ca-certificates \\
    procps \\
    && rm -rf /var/lib/apt/lists/*

# \u590d\u5236\u4ee3\u7801
COPY . /app

# \u5b89\u88c5 Python \u4f9d\u8d56\u770b\u7248\u9762\u8fd0\u884c\u5c31\u884c
RUN pip install --no-cache-dir flask psutil flask-session && \\
    echo \"\u4f9d\u8d56\u5b89\u88c5\u5b8c\u6210\"

# \u521b\u5efa\u6570\u636e\u76ee\u5f55
RUN mkdir -p /app/data /app/panel/templates

# \u66b4\u9732\u7aef\u53e3
EXPOSE 8888

# \u5065\u5eb7\u68c0\u67e5
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \\
    CMD curl -f http://localhost:8888/login || exit 1

# \u542f\u52a8\u6587\u4ef6
CMD [\"python\", \"panel_app.py\"]
