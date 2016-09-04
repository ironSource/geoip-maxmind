GEOIP service
=============

You can query the service if you supply valid JSON dictionary of following HTTP headers:

```
{
   "Client-Ip": "195.83.155.55",
   "X-Forwarded-For": "195.83.155.55",
   "Remote-Addr": "195.83.155.55",
   "X-Geoip-Dbs": "GEOIP_DB, GEOIP_CONNECTION_TYPE, GEOIP_ISP, GEOIP_DOMAIN, GEOIP_CITY"
}
```

You have to supply one of the headers with an actual ip address.

You will get a JSON response with all the info, and you can customize it with optional
`X-Geoip-Dbs` header, otherwise you will receive response from all available databases.

JSON should be a single string. You can check `test/test_socket.py` to see how to work with socket API.

Example response (formatted):

```
{
    "domain": "utc.fr",
    "ip": "195.83.155.55",
    "isp": "Commissariat a l\'Energie Atomique",
    "coordinates": "49.416700,2.833300",
    "connection": "Cable/DSL",
    "location": "Compiegne, France, Europe",
    "country": "FR",
    "continent": "EU",
    "organization": "UTC - Universite de Technologie de Compiegne"
}
```

Some fields may be populated with default values if no information is available. For example,

 * Default country code is `ZZ`
 * Default organization is `NO_ORG`
 * Default domain is `NO_DOMAIN`

Docker
------
TODO:

* Add geoip.conf support by coping environment variable
To build a container, simply execute `docker build -t ironsource/geoip_maxmind .`.

To run container accessible from other container, you have to use a `link`:

```
$ docker run --name geoip ironsource/geoip_maxmind
$ docker run --link geoip:geoip you-container
```

Now you can query tcp socket `geoip:8000` from your container.

To run container accessible from anywhere, run

```
$ docker run --name geoip -p 8000:8000 ironsource/geoip
```

Now you can query tcp socket `127.0.0.1:8000` or use your external ip address.

When you run your docker container, it is advised to run `sysctl -w net.core.somaxconn=32000`
as `root` user to get better socket performance.

Service may respond to socket or HTTP requests. By default, it response do socket,
but you can set `MODE=http` environment variable and query HTTP API.

To use HTTP API, simply make a POST request with serialized JSON as payload. Please
refer to example in the testing section.

Testing
-------

```
$ docker-compose -f docker-compose.test.yml up
```

Manual testing
--------------
HTTP mode:

```
curl -XPOST -H 'Content-Type:application/json' -d '{"X-Forwarded-For": "195.83.155.55"}' http://localhost:8000
```

Socket mode:

```
telnet localhost 8000
{"X-Forwarded-For": "195.83.155.55"}
```

Node.js HTTP example
--------------------

```
request.post({url: 'http://geoip:8000', json: {"X-Forwarded-For": "195.83.155.55"}},
  function (err, response, body) {
    console.log(body);
  });
```

Testing that geoip db update
-------------------------------------------------------
In geoip container:

```
$ docker run --name geoip ironsource/geoip
$ docker exec -t -i geoip /bin/bash
echo 1 > /usr/share/GeoIP2-Country.mmdb
/opt/geoip/update_geoip.sh
```

After that, check `/var/log/geoip.log` inside the container, you should see something like

```
2015-04-29 12:31:54,677 - INFO - Successfully updated database to /opt/geoip/etc/geoip/GeoIP2-Country.mmdb.PID3-1430310714
2015-04-29 12:31:54,679 - INFO - Watching /usr/share/GeoIP/GeoIP2-Country.mmdb
```
