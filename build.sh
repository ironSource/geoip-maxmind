#!/bin/bash

# yum -y update &&

yum install -y epel-release && yum install -y wget curl tar zlib-devel libcurl-devel openssl-devel gcc gcc-c++ make libtool anacron python-devel python-pip &&\
cd /tmp/ &&\
wget https://github.com/maxmind/geoipupdate/releases/download/v2.2.1/geoipupdate-2.2.1.tar.gz &&\
tar -zxvf geoipupdate* &&\
cd /tmp/geoipupdate-2.2.1/ && ./configure && make && make install &&\
cd /tmp/ &&\
wget https://github.com/maxmind/libmaxminddb/releases/download/1.0.4/libmaxminddb-1.0.4.tar.gz &&\
tar -zxvf libmaxminddb* &&\
cd /tmp/libmaxminddb* && ./configure && make && make check && make install &&\
sh -c "echo /usr/local/lib  >> /etc/ld.so.conf.d/local.conf" && ldconfig &&\
cd /opt/geoip && pip install -r requirements.txt &&\
yum autoremove -y wget tar zlib-devel libcurl-devel openssl-devel gcc gcc-c++ make libtool &&\
yum clean all &&\
rm -rf /var/cache/yum /tmp/* &&\

mkdir /usr/share/GeoIP/ &&\
mkdir /var/log/supervisor &&\

crontab /opt/geoip/crontab
