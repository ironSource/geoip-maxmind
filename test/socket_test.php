<?php

$fp = fsockopen("127.0.0.1", 8000, $errno, $errstr, 30);
if (!$fp) {
    echo "$errstr ($errno)<br />\n";
} else {
    $out =  json_encode(array(
    		"Remote-Addr" => "70.72.169.241", 
    		"X-Forwarded-For" => "70.72.169.241", 
    		"Client-Ip" => "70.72.169.241", 
    		"X-Geoip-Dbs" => "GEOIP_DB, GEOIP_ISP, GEOIP_DOMAIN, GEOIP_CITY"
    		));

    fwrite($fp, $out);
    while (!feof($fp)) {
        var_dump(fgets($fp, 1024));
    }
    fclose($fp);
}
