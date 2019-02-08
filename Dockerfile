FROM alpine:edge
MAINTAINER w8ay@qq.com
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN set -x \
    && apk update \
    && apk add python3 \
    && apk add nmap \
    && apk add masscan --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted
# install w12scan
RUN mkdir -p /opt/w12scan-client
COPY . /opt/w12scan-client

RUN set -x \
    && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /opt/w12scan-client/requirements.txt

WORKDIR /opt/w12scan-client

CMD ["rm","-f","/var/cache/apk/*"]
CMD ["python3","main.py"]