SETTINGS = {
    ##
    # GEOIP_DB_FILE
    # Geoip Database File location
    "GEOIP_DB_PATH": "/usr/share/GeoIP/"

    , "GEOIP_DB_FILE": "/usr/share/GeoIP/GeoIP2-Country.mmdb"

    , "GEOIP_ISP_DB_FILE": "/usr/share/GeoIP/GeoIP2-ISP.mmdb"

    , "GEOIP_DOMAIN_DB_FILE": "/usr/share/GeoIP/GeoIP2-Domain.mmdb"

    , "GEOIP_CITY_DB_FILE": "/usr/share/GeoIP/GeoIP2-City.mmdb"

    , "GEOIP_CONNECTION_TYPE_DB_FILE": "/usr/share/GeoIP/GeoIP2-Connection-Type.mmdb"

    , "BIND_TO": ('0.0.0.0', 8000)

    , "LOG_PATH": "/var/log/geoip.log"

    # Size of request queue for socket
    , "MAX_BACKLOG": 1000
}
