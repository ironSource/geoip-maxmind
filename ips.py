import socket
import struct
import re


def is_valid_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None

def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None


def ip2long(ipaddr=''):
    """ Convert an IP address string to long integer
    Returns "False" if invalid IP address provided

    @param (string) ipaddr
        IP address as string; e.g. 127.0.0.1

    @return (int|boolean)
    """
    try:
        ipaddr_packed = socket.inet_aton(ipaddr)
        ipaddr_long = struct.unpack("!L", ipaddr_packed)[0]
    except:
        ipaddr_long = False
    return ipaddr_long


def is_private_ip(ipaddr=''):
    """ Method checks if provided IP address is in private network

    @param (string) ipaddr
        IP address as string; e.g. 127.0.0.1

    @return (boolean)
    """
    private_ips = [
        ['10.0.0.0', '10.255.255.255']
        , ['172.16.0.0', '172.31.255.255']
        , ['192.168.0.0', '192.168.255.255']
        , ['169.254.0.0', '169.254.255.255']
        , ['127.0.0.0', '127.255.255.255']
    ]

    # If invalid IP address provided - return false
    ipaddr_long = ip2long(ipaddr)
    if not ipaddr_long:
        return True

    for ipaddr_range in private_ips:
        # If provided IP address in range - it's private
        ipaddr_from = ip2long(ipaddr_range[0])
        ipaddr_to = ip2long(ipaddr_range[1])
        if not ipaddr_from or not ipaddr_to or (ipaddr_long >= ipaddr_from and ipaddr_long <= ipaddr_to):
            return True

    return False


def get_client_ip(headers):
    """ Method returns non-private ip addresses (or localhost)

    @param (dict) headers

    @return str
    """
    client_ips = []

    # Extract IP address from HTTP_X_FORWARDED_FOR header if exists
    # Can contain multiple IP addresses separated by comma
    if headers.has_key('X-Forwarded-For'):
        for ipaddr in headers['X-Forwarded-For'].split(','):
            client_ips.append(ipaddr.strip())

    # Extract IP address from HTTP_CLIENT_IP header if exists
    if headers.has_key('Client-Ip'):
        for ipaddr in headers['Client-Ip'].split(','):
            client_ips.append(ipaddr.strip())

    # Extract IP address from REMOTE_ADDR header if exists
    if headers.has_key('Remote-Addr'):
        client_ips.append(headers['Remote-Addr'].strip())

    # Find real client's IP address
    filtered_ips = filter(lambda ip: (is_valid_ipv4(ip) and not is_private_ip(ip)) or is_valid_ipv6(ip), client_ips)

    # If no real IP address found - return localhost
    if len(filtered_ips) > 0:
        return filtered_ips[0]
    elif len(client_ips) > 0:
        return client_ips[0]
    else:
        return '127.0.0.1'
