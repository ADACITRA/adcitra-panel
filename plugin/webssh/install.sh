#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
install_tmp='/tmp/bt_install.pl'
public_file=/www/adcitra/panel/install/public.sh
if [ ! -f $public_file ];then
	wget -O $public_file http://download.adcitra.cn/install/public.sh -T 5;
fi
. $public_file

download_Url=$NODE_URL

Install_webssh()
{
	mkdir -p /www/adcitra/panel/plugin/webssh
	echo '正在安装脚本文件...' > $install_tmp
	wget -O /www/adcitra/panel/plugin/webssh/index.html $download_Url/install/plugin/webssh/index.html -T 5
	wget -O /www/adcitra/panel/plugin/webssh/info.json $download_Url/install/plugin/webssh/info.json -T 5
	wget -O /www/adcitra/panel/plugin/webssh/icon.png $download_Url/install/plugin/webssh/icon.png -T 5
	echo '安装完成' > $install_tmp
}

Uninstall_webssh()
{
	rm -rf /www/adcitra/panel/plugin/webssh
}


action=$1
if [ "${1}" == 'install' ];then
	Install_webssh
else
	Uninstall_webssh
fi
