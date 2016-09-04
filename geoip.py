import logging
from ips import get_client_ip
import shutil
import geoip2
import os
import time
from unidecode import unidecode
import config
from json_formatter import configure_logging

DEFAULT_COUNTRY_CODE = 'ZZ'
DEFAULT_CONTINENT_CODE = 'YY'
DEFAULT_ORGANIZATION = 'NO_ORG'
DEFAULT_DOMAIN = 'NO_DOMAIN'
GEOIP_LOCAL_DIR = os.path.dirname(os.path.abspath(__file__)) + '/etc/geoip'

configure_logging()


# The purpose of this class is to always have an object to refer to
# and be able to easily swap one database for another.
#
# In database swap goes wrong, old database keeps being used for request processing
class DatabaseAtom:
    db = None
    filename = ''

    def swap(self, filename):
        try:
            old_db = self.db
            old_filename = self.filename

            new_db = geoip2.database.Reader(filename, geoip2.database.MODE_MMAP_EXT)
            self.db = new_db
            self.filename = filename

            if old_db:
                old_db.close()

            logging.info('Successfully updated database', extra={'db': filename})

            if len(old_filename) > 0 and os.path.exists(old_filename):
                os.remove(old_filename)
        except Exception, e:
            logging.exception('Could not update database', extra={'db': old_filename, 'triedWith': filename})
            raise e

LOOKUP = {'GEOIP': DatabaseAtom(), 'GEOIP_ISP': DatabaseAtom(),
          'GEOIP_DOMAIN': DatabaseAtom(), 'GEOIP_CITY': DatabaseAtom(),
          'GEOIP_CONNECTION_TYPE': DatabaseAtom()}

LOOKUP_KEYS = set(LOOKUP.keys())

# Copies db file to a special location
# If is run first time and something goes wrong, crashes the whole process
def __load_db(db, path, init=False):
    pid = os.getpid()
    destination = os.path.join(GEOIP_LOCAL_DIR, os.path.basename(path) + '.PID' + str(pid) + '-' + str(time.strftime('%s')))

    # Copy db file to a local storage and swap global db objects
    try:
        shutil.copy(path, destination)
        LOOKUP[db].swap(destination)
    except Exception, e:
        logging.critical('Problem copying the GeoDB file to %s. %s' % (destination, str(e)))
        if init:
            exit(1)


def __get_db_list(headers):
    if 'X-Geoip-Dbs' in headers:
        dbs = map(lambda s: s.strip(), headers['X-Geoip-Dbs'].split(','))
        return LOOKUP_KEYS.intersection(dbs)

    return LOOKUP_KEYS


def __find_geoip_db_by_path(path):
    try:
        return filter(lambda key: config.SETTINGS[key + '_DB_FILE'] == path, LOOKUP_KEYS)[0]
    except Exception, e:
        logging.warning('Could not find corresponding db for file %s: %s', path, e)
        return None


def __create_geoip_dir():
    try:
        os.makedirs(GEOIP_LOCAL_DIR)  # works with UTF-8 chars
    except OSError, e:
        logging.error('Could not create temporary directory', extra={'path': GEOIP_LOCAL_DIR})
        exit(1)


# Loads the db and reschedules a callback to a file
# Because old file is being replaces, old watcher is destroyed with IN_IGNORED event
def geoip_callback(event):
    db = __find_geoip_db_by_path(event.pathname)

    if db:
        __load_db(db, event.pathname)

# Attaches pyinotify callback to ioloop
def __watch_geoip_db(pyinotify):
    try:
        wm = pyinotify.WatchManager()
        notifier = pyinotify.AsyncNotifier(wm, default_proc_fun=geoip_callback)

        logging.info('Watching db', extra={'db': config.SETTINGS['GEOIP_DB_PATH']})
        wm.add_watch(config.SETTINGS['GEOIP_DB_PATH'], pyinotify.IN_MOVED_TO)
    except pyinotify.NotifierError, err:
        logging.critical(err)


# Converts string from unicode to ascii (because it's too much hustle to store unicode values in RedShift)
def __convert_to_ascii(s):
    if isinstance(s, str):
        return s
    elif isinstance(s, unicode):
        return unidecode(s)
    else:
        return str(s)


# Utility function to wrap lookups with try
def __wrap_with_try(f):
    try:
        return f()
    except:
        return None

# Extracts ip and country information from headers
# Will try to return public ip associated with a country
# @return country
def country_lookup(headers, clientip):
    lscc = None
    continent = None

    try:
        geoip_result = LOOKUP['GEOIP'].db.country(clientip)
        lscc = geoip_result.country.iso_code  # from unicode to utf8 string
        continent = geoip_result.continent.code
    except Exception, e:
        logging.warning('Error occured while doing geoip lookup for client ip', extra={'ip': clientip})
        lscc = headers.get('X-Geoip-Country')  # Country code based on IP

    return (lscc or DEFAULT_COUNTRY_CODE, continent or DEFAULT_CONTINENT_CODE)


def org_lookup(clientip):
    try:
        org_geoip = LOOKUP['GEOIP_ISP']
        geoip_result = org_geoip.db.isp(clientip)
        return {'organization': (geoip_result.organization or DEFAULT_ORGANIZATION),
                'isp': (geoip_result.isp or DEFAULT_ORGANIZATION)}
    except Exception, e:
        logging.warning('Error occured while doing geoip ISP lookup for client ip', extra={'ip': clientip})

    return {'organization': DEFAULT_ORGANIZATION, 'isp': DEFAULT_ORGANIZATION}


def location_lookup(clientip):
    try:
        city_geoip = LOOKUP['GEOIP_CITY']
        result = city_geoip.db.city(clientip)

        location_parts = map(__wrap_with_try, [lambda: result.city.names['en'],
                  lambda: result.country.names['en'],
                  lambda: result.continent.names['en']
                 ])

        location = ', '.join(filter(lambda p: p is not None, location_parts))
        coords = '%f,%f' % (result.location.latitude, result.location.longitude)
        country_confidence = result.country.confidence or ''
        subdivisions = map(lambda obj: {
                'iso_code': str(obj.iso_code),
                'name': str(obj.names['en'])
                }, 
                result.subdivisions)

        return {'coordinates': coords, 
            'location': location, 
            'country_confidence':country_confidence,
            'subdivisions':subdivisions}
    except Exception, e:
        logging.warning('Error occured while doing geoip location lookup for client ip', extra={'ip': clientip})

    return {'coordinates': '', 'location': ''}


def domain_lookup(clientip):
    try:
        org_geoip = LOOKUP['GEOIP_DOMAIN']
        geoip_result = org_geoip.db.domain(clientip)
        return {'domain': (geoip_result.domain or DEFAULT_DOMAIN)}
    except Exception, e:
        logging.warning('Error occured while doing geoip domain lookup for client ip', extra={'ip': clientip})

    return {'domain': DEFAULT_DOMAIN}


def connection_type_lookup(clientip):
    try:
        connection_geoip = LOOKUP['GEOIP_CONNECTION_TYPE']
        geoip_result = connection_geoip.db.connection_type(clientip)
        return {'connection': geoip_result.connection_type or ''}
    except Exception, e:
        logging.warning('Error occured while doing geoip connection type lookup for client ip', extra={'ip': clientip})

    return {'connection': ''}


# Extracts public ip and country associated with it, then looks up name of the ISP (internet service provider)
# @return (clientip, country, organization)
def ip_lookup(headers):
    clientip = get_client_ip(headers)  # User IP address
    dbs = __get_db_list(headers)
    country, continent = country_lookup(headers, clientip)

    result = {'ip': clientip, 'country': country, 'continent': continent}

    if 'GEOIP_ISP' in dbs:
        result.update(org_lookup(clientip))

    if 'GEOIP_DOMAIN' in dbs:
        result.update(domain_lookup(clientip))

    if 'GEOIP_CITY' in dbs:
        result.update(location_lookup(clientip))

    if 'GEOIP_CONNECTION_TYPE' in dbs:
        result.update(connection_type_lookup(clientip))

    return dict(map(lambda (k, v): (k, __convert_to_ascii(v)), result.iteritems()))


# Checks if temporary directory for geoip db files is in place
# Checks if GEOIP2 library is in place
def configure_geoip():
    if os.path.exists(GEOIP_LOCAL_DIR):
        shutil.rmtree(GEOIP_LOCAL_DIR)

    __create_geoip_dir()

    try:
        import geoip2.database
    except:
        logging.error('Exiting. Problems loading geoip database. Make sure library is installed properly.')
        exit(1)


# Loads geoip database information
def load_geoip_database(init=False):
    # After forking, load geoip databases into memory
    # process will exit if it fails

    for key in LOOKUP_KEYS:
        __load_db(key, config.SETTINGS[key + '_DB_FILE'], init=init)

    try:
        import pyinotify

        __watch_geoip_db(pyinotify)
    except Exception, e:
        logging.exception('Pyinotify is not installed, maybe it is not supported by your platform? %s', e)
