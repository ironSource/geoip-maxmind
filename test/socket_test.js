var net = require('net');
var express = require("express");
var app = express();
var port = 80;


var HOST = 'geoip';
var PORT = 8000;
var sum = 0;
var count = 0;

app.get("/", function(req, res){
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client
    var paylod = JSON.stringify({
       "Client-Ip": "195.83.155.55",
       "X-Forwarded-For": "195.83.155.55",
       "Remote-Addr": "195.83.155.55",
//      "X-Geoip-Dbs": "GEOIP_DB"
//, GEOIP_CONNECTION_TYPE, GEOIP_ISP, GEOIP_DOMAIN, GEOIP_CITY"
    });

    var client = new net.Socket();
    client.connect(PORT, HOST, function() {
        console.log('CONNECTED TO: ' + HOST + ':' + PORT);
    });
    var date = new Date().getTime();
    client.write(paylod);
    // Add a 'data' event handler for the client socket
    // data is what the server sent to this socket
    client.on('data', function(data) {
        console.log('data' + data);
        sum += new Date().getTime()-date;
        count += 1;
        client.destroy();
    });

    res.send("DONE");
});

app.get("/sum", function(req, res){
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client
    res.send("Total of " + count + " requests, took " + sum + "ms, avg is: " + sum/count + "ms");
});

app.listen(port);
console.log("Listening on port " + port);