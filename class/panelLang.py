#coding: utf-8
"""多语言管理模块 — 语言切换 API"""
import os, json

LANG_PATH = r"C:\Users\ADA\Documents\baota\AdCtiraPanel\languages"

def register_lang_routes(app):
    import public
    from flask import request
    
    @app.route("/config/set_language", methods=["POST"])
    def set_language():
        lang = request.form.get("lang", "zh_CN")
        pl = os.path.join(LANG_PATH, "language.pl")
        try:
            with open(pl, "w", encoding="utf-8") as f:
                f.write(lang)
            return public.returnMsg(True, {"lang": lang, "msg": "OK"})
        except Exception as e:
            return public.returnMsg(False, str(e))
    
    @app.route("/config/get_languages", methods=["GET"])
    def get_languages():
        sf = os.path.join(LANG_PATH, "settings.json")
        try:
            if os.path.exists(sf):
                with open(sf, "r", encoding="utf-8") as f:
                    return public.returnMsg(True, json.load(f))
        except:
            pass
        return public.returnMsg(True, {
            "languages": [
                {"name":"zh_CN","title":"简体中文"},
                {"name":"en","title":"English"},
                {"name":"ja","title":"日本語"}
            ],
            "default":"zh_CN"
        })
