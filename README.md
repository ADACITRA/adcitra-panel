##### AdCtira灯塔开源许可协议：https://www.adcitra.cn/kyxy.html
##### 使用手册：http://docs.adcitra.cn
##### 论坛地址：https://www.adcitra.cn/bbs
##### 反馈建议： https://www.adcitra.cn/bbs/forum-43-1.html
##### Bug提交：https://www.adcitra.cn/bbs/forum-39-1.html

#### 安装命令：
##### 通用脚本[推荐]
```bash
if [ -f /usr/bin/curl ];then curl -sSO https://download.adcitra.cn/install/install_panel.sh;else wget -O install_panel.sh https://download.adcitra.cn/install/install_panel.sh;fi;bash install_panel.sh btg26
```

#### Centos/OpenCloud/Alibaba
```bash
url=https://download.adcitra.cn/install/install_panel.sh;if [ -f /usr/bin/curl ];then curl -sSO $url;else wget -O install_panel.sh $url;fi;bash install_panel.sh btg26

```

##### Debain
```bash
wget -O install_panel.sh https://download.adcitra.cn/install/install_panel.sh && bash install_panel.sh btg26
```

#### Ubuntu/Deepin
```bash
wget -O install_panel.sh https://download.adcitra.cn/install/install_panel.sh && sudo bash install_panel.sh btg26
```