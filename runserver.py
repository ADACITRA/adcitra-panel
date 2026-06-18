#coding: utf-8
# +-------------------------------------------------------------------
# | AdCtira灯塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 AdCtira灯塔软件(http://adcitra.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: AdCtira Team
# +-------------------------------------------------------------------
from os import environ
from AdCtiraPanel import app,sys

if __name__ == '__main__':
    f = open('data/port.pl')
    PORT = int(f.read())
    HOST = '0.0.0.0'
    f.close()
    app.run(host=HOST,port=PORT)
