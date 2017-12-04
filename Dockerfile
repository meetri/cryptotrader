FROM centos:7
LABEL maintainer "Demetrius Bell <meetri@gmail.com>"

RUN yum install -y epel-release 
RUN yum groupinstall -y "Development Tools"

RUN mkdir /opt/build \
&& cd /opt/build \ 
&& curl -LO http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
&& tar -xvzf ta-lib-0.4.0-src.tar.gz \
&& cd ta-lib \
&& ./configure \
&& make install \
&& cd / \
&& rm -Rf /opt/build

RUN yum install -y python34 python34-devel python34-pip tmux vim \
&& pip3 install --upgrade pip \
&& pip3 install psycopg2 influxdb redis pg numpy ta-lib flask pyyaml

RUN rpm -ivh https://kojipkgs.fedoraproject.org//packages/http-parser/2.7.1/3.el7/x86_64/http-parser-2.7.1-3.el7.x86_64.rpm && yum -y install nodejs

RUN yum install -y npm \
&& npm install redis pg \
&& npm install node.bittrex.api 

RUN npm install console-stamp

ENV LD_LIBRARY_PATH=/usr/local/lib

COPY vim_runtime /root/.vim_runtime
COPY configs/vimrc /root/.vimrc
COPY configs/tmux /root/.tmux.conf

COPY src /opt/crypto
WORKDIR /opt/crypto/

ENTRYPOINT ["/bin/bash","/opt/crypto/bootstrap.sh"]
#ENTRYPOINT ["/usr/bin/node","/opt/crypto/node/coinigy/rt_selected_markets.js"]
