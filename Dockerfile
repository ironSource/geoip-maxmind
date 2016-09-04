FROM centos:centos7

ADD . /opt/geoip

RUN /opt/geoip/build.sh

VOLUME /usr/share/GeoIP/

EXPOSE 8000

CMD /usr/bin/supervisord -c /opt/geoip/supervisord.conf
