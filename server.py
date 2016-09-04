import geoip
import asynchat
import asyncore
import socket
import json
import config
import os
from werkzeug.wrappers import Request, Response


class RequestHandler(asynchat.async_chat):
    TERMINATOR = '}'
    ac_in_buffer_size = 512    # Should be enough for average incoming request
    ac_out_buffer_size = 1024  # Should be enough for average response

    def __init__(self, sock):
        self.received_data = []
        asynchat.async_chat.__init__(self, sock)
        self.set_terminator('}')
        return

    def collect_incoming_data(self, data):
        self.received_data.append(data)

    def found_terminator(self):
        self.process_data()

    def process_data(self):
        data = ''.join(self.received_data) + self.TERMINATOR
        headers = json.loads(data)
        result = json.dumps(geoip.ip_lookup(headers))

        self.push(result)
        self.close_when_done()


class Server(asyncore.dispatcher):
    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsockname()
        self.listen(config.SETTINGS['MAX_BACKLOG'])
        return

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        RequestHandler(sock=client_info[0])
        return

    def handle_close(self):
        self.close()


def run(address):
    Server(address)

    print 'Listening on', address
    asyncore.loop(use_poll=True)


@Request.application
def application(request):
    headers = json.loads(request.data)
    result = json.dumps(geoip.ip_lookup(headers))

    return Response(result)


def run_http(address):
    from werkzeug.serving import run_simple
    run_simple(address[0], address[1], application)

if __name__ == '__main__':
    geoip.configure_geoip()
    geoip.load_geoip_database(init=True)

    if os.environ.get('MODE') == 'http':
        run_http(config.SETTINGS['BIND_TO'])
    else:
        run(config.SETTINGS['BIND_TO'])
