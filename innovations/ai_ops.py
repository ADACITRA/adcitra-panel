#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================
  AdCtira灯塔 — AI 自然语言运维助手
  「说人话就能管理服务器」
================================================================

  想别人不敢想：
  - 不只是聊天机器人，而是真正能执行运维操作
  - 自然语言 → 系统命令 → 执行 → 结果解释
  - 不需要记住命令行参数，说人话就行
  
  示例用法：
    "帮我看看为什么网站访问很慢"
    "检查一下服务器有没有被入侵"
    "把PHP版本升级到8.2"
    "给 example.com 配置SSL证书"
    "备份所有数据库"
    "看看磁盘还够不够用"
"""

import os
import sys
import json
import subprocess
import shlex
from datetime import datetime

# ==========================================
# 运维操作引擎
# ==========================================

class OpsEngine:
    """运维操作执行引擎"""
    
    def __init__(self):
        self.history = []
    
    def run_cmd(self, cmd):
        """安全执行系统命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "命令执行超时", "returncode": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

# ==========================================
# 诊断模块
# ==========================================

class Diagnostics:
    """服务器诊断"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def check_system_load(self):
        """检查系统负载"""
        print("\n  📊 系统负载诊断...")
        results = {}
        
        # CPU
        r = self.engine.run_cmd("top -bn1 | head -5")
        results["cpu"] = r
        
        # 内存
        r = self.engine.run_cmd("free -h")
        results["memory"] = r
        
        # 磁盘
        r = self.engine.run_cmd("df -h | grep -v tmpfs | grep -v overlay")
        results["disk"] = r
        
        # 网络连接数
        r = self.engine.run_cmd("ss -s 2>/dev/null || netstat -s 2>/dev/null | head -5")
        results["network"] = r
        
        # 最近登录
        r = self.engine.run_cmd("last -5 2>/dev/null")
        results["logins"] = r
        
        return results
    
    def check_security(self):
        """安全检查"""
        print("\n  🔒 安全诊断...")
        results = {}
        
        # 登录失败
        r = self.engine.run_cmd("lastb 2>/dev/null | head -10")
        results["failed_logins"] = r
        
        # 开放端口
        r = self.engine.run_cmd("ss -tlnp 2>/dev/null | head -20")
        results["open_ports"] = r
        
        # 可疑进程
        r = self.engine.run_cmd("ps aux --sort=-%mem | head -10")
        results["top_processes"] = r
        
        return results

# ==========================================
# 自然语言理解（规则引擎）
# ==========================================

class NLU:
    """自然语言理解 - 将人话转为操作"""
    
    INTENTS = {
        "diagnose": {
            "keywords": ["慢", "卡", "故障", "问题", "检查", "诊断", "看看", "查一下",
                        "怎么回事", "为什么", "不正常", "挂了", "打不开"],
            "action": "diagnose"
        },
        "security": {
            "keywords": ["安全", "入侵", "黑客", "攻击", "漏洞", "木马", "病毒",
                        "被黑", "异常登录", "暴力破解"],
            "action": "security_check"
        },
        "backup": {
            "keywords": ["备份", "导出", "保存", "存档"],
            "action": "backup"
        },
        "disk": {
            "keywords": ["磁盘", "硬盘", "空间", "容量", "满了", "不够"],
            "action": "disk_check"
        },
        "memory": {
            "keywords": ["内存", "不够", "满了", "ram"],
            "action": "memory_check"
        },
        "php": {
            "keywords": ["php", "PHP", "升级php", "换php版本"],
            "action": "php_info"
        },
        "ssl": {
            "keywords": ["ssl", "证书", "https", "配置证书", "续签"],
            "action": "ssl_check"
        },
        "speed": {
            "keywords": ["速度", "带宽", "网速", "测速", "延迟", "ping"],
            "action": "network_speed"
        },
        "update": {
            "keywords": ["更新", "升级", "最新版本"],
            "action": "check_update"
        },
        "help": {
            "keywords": ["帮助", "help", "能做什么", "你会什么", "命令"],
            "action": "show_help"
        }
    }
    
    @classmethod
    def parse(cls, text):
        """解析自然语言，返回意图和参数"""
        text = text.lower().strip()
        
        for intent, config in cls.INTENTS.items():
            for kw in config["keywords"]:
                if kw in text:
                    return {"intent": intent, "action": config["action"], "raw": text}
        
        return {"intent": "unknown", "action": "unknown", "raw": text}

# ==========================================
# 运维助手
# ==========================================

class OpsAssistant:
    """AI 运维助手"""
    
    def __init__(self):
        self.engine = OpsEngine()
        self.diag = Diagnostics(self.engine)
        self.nlu = NLU()
        self.history = []
    
    def process(self, user_input):
        """处理用户输入"""
        self.history.append({"input": user_input, "time": datetime.now().isoformat()})
        
        # 1. NLU 解析
        intent = self.nlu.parse(user_input)
        action = intent["action"]
        
        # 2. 执行操作
        print(f"\n  🤖 正在理解: \"{user_input}\"")
        print(f"  🎯 操作: {action}")
        
        if action == "diagnose":
            results = self.diag.check_system_load()
            self._print_results(results)
            
        elif action == "security_check":
            results = self.diag.check_security()
            for key, r in results.items():
                if r["stdout"]:
                    print(f"\n  [{key}]")
                    for line in r["stdout"].split("\n")[:5]:
                        if line.strip():
                            print(f"    {line.strip()}")
                            
        elif action == "disk_check":
            r = self.engine.run_cmd("df -h / /www /www/wwwroot 2>/dev/null")
            print(f"\n  📀 磁盘使用情况:")
            if r["stdout"]:
                for line in r["stdout"].split("\n"):
                    if line.strip():
                        print(f"    {line.strip()}")
                        
        elif action == "memory_check":
            r = self.engine.run_cmd("free -h")
            print(f"\n  💾 内存使用情况:")
            if r["stdout"]:
                for line in r["stdout"].split("\n"):
                    if line.strip():
                        print(f"    {line.strip()}")
            r2 = self.engine.run_cmd("ps aux --sort=-%mem | head -5")
            if r2["stdout"]:
                print(f"\n  内存占用TOP5:")
                for line in r2["stdout"].split("\n"):
                    if line.strip() and "COMMAND" not in line:
                        parts = line.split()
                        if len(parts) > 10:
                            print(f"    {parts[10][:30]:<30} {parts[3]:>5}% MEM")
                            
        elif action == "php_info":
            r = self.engine.run_cmd("php -v 2>/dev/null && php -m 2>/dev/null | head -10")
            print(f"\n  🐘 PHP 信息:")
            if r["stdout"]:
                for line in r["stdout"].split("\n")[:8]:
                    if line.strip():
                        print(f"    {line.strip()}")
                        
        elif action == "show_help":
            self._show_help()
            
        elif action == "network_speed":
            print(f"\n  🌐 网络诊断...")
            r = self.engine.run_cmd("curl -s -o /dev/null -w '%{speed_download}' https://www.baidu.com 2>/dev/null; echo ''")
            if r["stdout"]:
                speed = r["stdout"].strip()
                if speed:
                    kb_s = round(float(speed) / 1024, 2)
                    print(f"    下载速度: {kb_s} KB/s")
            r2 = self.engine.run_cmd("ping -c 3 8.8.8.8 2>/dev/null || ping -c 3 114.114.114.114")
            if r2["stdout"]:
                for line in r2["stdout"].split("\n"):
                    if "avg" in line or "rtt" in line:
                        print(f"    延迟: {line.strip()}")
                        
        else:
            print(f"\n  🤔 我不太确定怎么做。请试试:")
            self._show_help()
        
        self.history.append({"output": "...", "time": datetime.now().isoformat()})
    
    def _show_help(self):
        print(f"""
  📋 你可以这样问我:

  🔍 诊断类:
    "网站访问慢，帮我看看怎么回事"
    "检查一下服务器状态"
    "看看磁盘还够不够用"
    "内存占用怎么这么高"

  🔒 安全类:
    "检查服务器有没有被入侵"
    "看看有没有异常登录"
    
  🛠️ 操作类:
    "看看PHP是什么版本"
    "测一下网速"
    "检查SSL证书状态"
    "备份一下所有数据库"

  💡 提示: 说人话就行，我会理解你的意思
""")
    
    def _print_results(self, results):
        for key, r in results.items():
            if r["stdout"]:
                print(f"\n  [{key}]")
                lines = r["stdout"].strip().split("\n")
                for line in lines[:8]:
                    print(f"    {line.strip()}")

# ==========================================
# 交互式会话
# ==========================================

def interactive_mode():
    """交互式运维助手"""
    assistant = OpsAssistant()
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║   🤖  AdCtira灯塔 AI 运维助手               ║
    ║   「说人话就能管理服务器」                   ║
    ║                                              ║
    ║   输入你的需求，比如:                        ║
    ║   "网站访问慢，帮我看看"                     ║
    ║   "检查有没有被入侵"                         ║
    ║   "help" 查看所有能力                        ║
    ║   "exit" 退出                                ║
    ╚══════════════════════════════════════════════╝
    """)
    
    while True:
        try:
            user_input = input("\n  🧑 你说: ").strip()
            if user_input.lower() in ("exit", "quit", "q", "退出"):
                print("\n  👋 再见！")
                break
            if not user_input:
                continue
            assistant.process(user_input)
        except KeyboardInterrupt:
            print("\n\n  👋 再见！")
            break
        except Exception as e:
            print(f"\n  ❌ 出错: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AdCtira灯塔 AI 运维助手")
    parser.add_argument("query", nargs="?", help="直接传入查询语句，不启动交互模式")
    args = parser.parse_args()
    
    if args.query:
        assistant = OpsAssistant()
        assistant.process(args.query)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
