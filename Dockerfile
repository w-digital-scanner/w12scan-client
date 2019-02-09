FROM debian
MAINTAINER w8ay@qq.com
RUN set -x \
    && apt update \
    && apt install python3 nmap masscan python3-pip -y
# install w12scan
RUN mkdir -p /opt/w12scan-client
COPY . /opt/w12scan-client

RUN set -x \
    && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /opt/w12scan-client/requirements.txt

WORKDIR /opt/w12scan-client
ENTRYPOINT ["python3","main.py"]