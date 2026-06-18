# coding: utf-8
# -------------------------------------------------------------------
# AdCtira灯塔Linux面板
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Author: wzz <wzz@adcitra.cn>
# -------------------------------------------------------------------
# ------------------------------
# docker模型 - docker runtime 基类
# ------------------------------
import json
import os
import sys
import time
from datetime import datetime, timedelta

if "/www/adcitra/panel/class" not in sys.path:
    sys.path.insert(0, "/www/adcitra/panel/class")

import public
from mod.project.docker.composeMod import main as composeMod


class Runtime(composeMod):

    def __init__(self):
        super(Runtime, self).__init__()