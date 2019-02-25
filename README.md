# w12scan-client
网络资产搜索发现引擎,大规模资产识别，毕业设计，w12scan 客户端程序

## 配置说明
- 这是w12scan的扫描端，基于python3编写，在进行扫描之前，需要安装`nmap`和`masscan`，并将它们设置为环境变量，当然，如果你是使用docker编译安装的就不需要此步骤了。
- `config.py`中定义了扫描的相关配置，你可以设置masscan扫描的`rate`，是否扫描全端口(默认扫描部分端口)，线程数以及节点名称等等...

## docker编译
- 本仓库所有代码提交都会自动编译到dockerhub上，所以你无需下载这里的仓库。你只需要按照[https://github.com/boy-hack/w12scan](https://github.com/boy-hack/w12scan)的要求运行即可。
- 除非你想自己修改一些配置可以使用如下命令,在本文件目录下
```bash
$docker build -t w12scan-client:lastest .
$docker tag w12scan-client:latest boyhack/w12scan-client
```
再按照[https://github.com/boy-hack/w12scan](https://github.com/boy-hack/w12scan)的要求运行即可。

# IP数据库更新
- 网络上大部分ip接口都有频率限制，所以IP数据使用GEOIP数据，但不保证数据的时效性，可以通过下载最新数据库解决
- https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz  
- 放到data/GeoLite2目录下