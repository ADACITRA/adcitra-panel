# coding: utf-8
# +-------------------------------------------------------------------
# | AdCtira
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 AdCtira(www.adcitra.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: hwliang <team@adcitra.cn>
# +-------------------------------------------------------------------

# --------------------------------
# AdCtira灯塔公共库
# --------------------------------

from .common import *
from .exceptions import *

    
def is_bind():
    # if not os.path.exists('{}/data/bind.pl'.format(get_panel_path())): return True
    return not not get_user_info()
