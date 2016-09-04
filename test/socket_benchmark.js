var net = require('net');
var Benchmark = require('benchmark').Benchmark;

var HOST = 'geoip'; //'192.168.59.103';
var PORT = 8000;

var payload = JSON.stringify({
    "Client-Ip": "195.83.155.55",
    "X-Forwarded-For": "195.83.155.55",
    "Remote-Addr": "195.83.155.55",
//    "X-Geoip-Dbs": "GEOIP_DB"
//, GEOIP_CONNECTION_TYPE, GEOIP_ISP, GEOIP_DOMAIN, GEOIP_CITY"
    });

var query = function (done) {
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client

    var client = new net.Socket();
    client.connect(PORT, HOST, function() {
//        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    var date = new Date().getTime();
    client.write(payload);
    // Add a 'data' event handler for the client socket
    // data is what the server sent to this socket
    client.on('data', function(data) {
//        console.log('data' + data);
        client.destroy();
        done.resolve();
    });
};

var bench = new Benchmark('geoip', {
  // a flag to indicate the benchmark is deferred
  'defer': true,
//  'async': true,
  // benchmark test function
  'fn': query
}).on('complete', function () {
    console.log(this.stats);
});

bench.run();