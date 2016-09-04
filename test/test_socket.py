# Source: mostly Python documentation

import socket
import json
import sys

HOST = '127.0.0.1'
PORT = 8000

s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print msg
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        print msg
        s.close()
        s = None
        continue
    break

if s is None:
    print 'could not open socket'
    sys.exit(1)

payload = json.dumps({
   "Client-Ip": "195.83.155.55",
   "X-Forwarded-For": "195.83.155.55",
   "Remote-Addr": "195.83.155.55",
   "X-Geoip-Dbs": "GEOIP_DB, GEOIP_CONNECTION_TYPE, GEOIP_ISP, GEOIP_DOMAIN, GEOIP_CITY"
})

s.setblocking(False)
s.settimeout(5)

s.sendall(payload)
data = s.recv(1024)
s.close()

print 'Received', repr(data)