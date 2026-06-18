#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

check_gevent_version(){
    is_gevent140=$(/www/adcitra/panel/pyenv/bin/python3 -c "import gevent;print(gevent.__version__)"|grep  -E '^1.')
}

check_gevent_version
if [ "${is_gevent140}" = "" ];then
    echo > /www/adcitra/panel/data/upgrade_gevent.lock
    exit;
fi

/www/adcitra/panel/pyenv/bin/pip3 install gevent -U

check_gevent_version
if [ "${is_gevent140}" = "" ];then
    rm -f /www/adcitra/panel/script/upgrade_gevent.sh
    echo > /www/adcitra/panel/data/upgrade_gevent.lock
    bash /www/adcitra/panel/init.sh reload
fi
