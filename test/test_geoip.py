import unittest

import sys

sys.path.append('.')

import time
import os
from geoip import configure_geoip
from geoip import ip_lookup
from geoip import load_geoip_database
from geoip import LOOKUP
import config


class ipResolveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_geoip()
        load_geoip_database()

    def test_resolve_country(self):
        headers = {'Client-Ip': '199.203.61.108'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '199.203.61.108',
            'country': 'IL',
            'continent': 'AS',
            'coordinates': '32.066700,34.766700',
            'domain': 'netvision.net.il',
            'isp': 'Elron Technologies',
            'location': 'Tel Aviv, Israel, Asia',
            'organization': 'GTEK Technologies',
            'country_confidence': '',
            'subdivisions': "[{'iso_code': 'TA', 'name': 'Tel Aviv'}]",
            'connection': 'Cable/DSL'
        })

    def test_resolve_regular_country(self):
        headers = {'Client-Ip': '199.203.61.108'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '199.203.61.108',
            'country': 'IL',
            'continent': 'AS',
            'coordinates': '32.066700,34.766700',
            'domain': 'netvision.net.il',
            'isp': 'Elron Technologies',
            'location': 'Tel Aviv, Israel, Asia',
            'organization': 'GTEK Technologies',
            'country_confidence': '',
            'subdivisions': "[{'iso_code': 'TA', 'name': 'Tel Aviv'}]",
            'connection': 'Cable/DSL'
        })

    def test_resolve_google_ip(self):
        headers = {'Client-Ip': '66.249.81.164'}

        geoip_data = ip_lookup(headers)
        self.assertEquals(geoip_data, {
            'ip': '66.249.81.164',
            'country': 'ZZ',
            'continent': 'EU',
            'coordinates': '47.000000,8.000000',
            'location': 'Europe',
            'domain': 'google.com',
            'isp': 'Google',
            'organization': 'Google',
            'connection': 'Cellular',
            'country_confidence': '',
            'subdivisions': '[]'
        })

    def test_resolve_local_address(self):
        headers = {'Client-Ip': '10.0.0.1'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '10.0.0.1',
            'country': 'ZZ',
            'continent': 'YY',
            'coordinates': '',
            'domain': 'NO_DOMAIN',
            'isp': 'NO_ORG',
            'location': '',
            'organization': 'NO_ORG',
            'connection': ''
        })

    def test_resolve_through_header(self):
        headers = {'X-Geoip-Country': 'NL', 'Client-Ip': '10.0.0.1'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '10.0.0.1',
            'country': 'NL',
            'continent': 'YY',
            'coordinates': '',
            'domain': 'NO_DOMAIN',
            'isp': 'NO_ORG',
            'location': '',
            'organization': 'NO_ORG',
            'connection': ''
        })

    def test_resolve_multiple(self):
        headers = {'Client-Ip': '10.0.0.1', 'Remote-Addr': '199.203.61.108'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '199.203.61.108',
            'country': 'IL',
            'continent': 'AS',
            'coordinates': '32.066700,34.766700',
            'domain': 'netvision.net.il',
            'isp': 'Elron Technologies',
            'location': 'Tel Aviv, Israel, Asia',
            'organization': 'GTEK Technologies',
            'country_confidence': '',
            'subdivisions': "[{'iso_code': 'TA', 'name': 'Tel Aviv'}]",
            'connection': 'Cable/DSL'
        })

    def test_resolve_multiple_with_proxy(self):
        headers = {'Client-Ip': '10.0.0.1', 'X-Forwarded-For': '199.203.61.108',
                   'Remote-Addr': '78.129.168.146'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '199.203.61.108',
            'country': 'IL',
            'continent': 'AS',
            'coordinates': '32.066700,34.766700',
            'domain': 'netvision.net.il',
            'isp': 'Elron Technologies',
            'location': 'Tel Aviv, Israel, Asia',
            'organization': 'GTEK Technologies',
            'country_confidence': '',
            'subdivisions': "[{'iso_code': 'TA', 'name': 'Tel Aviv'}]",
            'connection': 'Cable/DSL'
        })

    def test_resolve_with_weird_name(self):
        headers = {'Client-Ip': '195.83.155.55'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '195.83.155.55',
            'country': 'FR',
            'continent': 'EU',
            'coordinates': '49.416700,2.833300',
            'domain': 'utc.fr',
            'isp': "Renater",
            'location': 'Compiegne, France, Europe',  # This is totally French name: Compi\xc3gne
            'organization': 'UTC - Universite de Technologie de Compiegne',
            'subdivisions': "[{'iso_code': '60', 'name': 'Oise'}]",
            'country_confidence': '',
            'connection': 'Cable/DSL'
        })

    def test_resolve_with_weird_location(self):
        headers = {'Client-Ip': '62.112.234.12'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '62.112.234.12',
            'country': 'NL',
            'continent': 'EU',
            'coordinates': '52.382400,4.899500',
            'domain': 'NO_DOMAIN',
            'isp': 'ASP4all Hosting B.V.',
            'location': 'Netherlands, Europe',
            'organization': 'ASP4all Hosting B.V.',
            'connection': '',
            'country_confidence': '',
            'subdivisions': '[]'
        })

    def test_resolve_with_geoip_off(self):
        headers = {'Client-Ip': '10.0.0.1'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '10.0.0.1',
            'country': 'ZZ',
            'continent': 'YY',
            'coordinates': '',
            'domain': 'NO_DOMAIN',
            'isp': 'NO_ORG',
            'location': '',
            'organization': 'NO_ORG',
            'connection': ''
        })

    def test_resolve_through_header_with_geoip_off(self):
        headers = {'Client-Ip': '10.0.0.1', 'X-Geoip-Country': 'NL'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '10.0.0.1',
            'country': 'NL',
            'continent': 'YY',
            'coordinates': '',
            'domain': 'NO_DOMAIN',
            'isp': 'NO_ORG',
            'location': '',
            'organization': 'NO_ORG',
            'connection': ''
        })

    def test_resolve_specific_db(self):
        headers = {'Client-Ip': '195.83.155.55', 'X-Geoip-Dbs': 'GEOIP_CONNECTION_TYPE, FAKE_DB_NAME'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '195.83.155.55',
            'country': 'FR',
            'continent': 'EU',
            'connection': 'Cable/DSL'
        })

    def test_ipv6_1(self):
        headers = {'Client-Ip': '2001:4d68:200e:1222:a1ae:8ef:369d:5a1'}

        geoip_data = ip_lookup(headers)
        print geoip_data

        self.assertEquals(geoip_data, {
            'domain': 'NO_DOMAIN',
            'ip': '2001:4d68:200e:1222:a1ae:8ef:369d:5a1',
            'isp': 'Imagine Group',
            'coordinates': '53.333100,-6.248900',
            'connection': '',
            'location': 'Dublin, Ireland, Europe',
            'country': 'IE',
            'continent': 'EU',
            'organization': 'Imagine Group',
            'subdivisions': "[{'iso_code': 'L', 'name': 'Leinster'}]",
            'country_confidence': ''
        })

    def test_ipv6_2(self):
        headers = {'Client-Ip': '2001:4d68:200e:1221:dcd6:ff49:5e3b:ee8a1'}

        geoip_data = ip_lookup(headers)
        print geoip_data

        self.assertEquals(geoip_data, {
            'domain': 'NO_DOMAIN',
            'ip': '2001:4d68:200e:1221:dcd6:ff49:5e3b:ee8a1',
            'isp': 'NO_ORG',
            'coordinates': '',
            'connection': '',
            'location': '',
            'country': 'ZZ',
            'continent': 'YY',
            'organization': 'NO_ORG'
        })


class TestDatabaseAtom(unittest.TestCase):
    def setUp(self):
        load_geoip_database()

        self.old_db = LOOKUP['GEOIP'].db
        self.old_db_path = LOOKUP['GEOIP'].filename
        self.old_geoip_path = config.SETTINGS['GEOIP_DB_FILE']

    def tearDown(self):
        config.SETTINGS['GEOIP_DB_FILE'] = self.old_geoip_path

    def run_asserts(self):
        headers = {'Client-Ip': '199.203.61.108'}

        geoip_data = ip_lookup(headers)

        self.assertEquals(geoip_data, {
            'ip': '199.203.61.108',
            'country': 'IL',
            'continent': 'AS',
            'coordinates': '32.066700,34.766700',
            'domain': 'netvision.net.il',
            'isp': 'Elron Technologies',
            'location': 'Tel Aviv, Israel, Asia',
            'organization': 'GTEK Technologies',
            'country_confidence': '',
            'subdivisions': "[{'iso_code': 'TA', 'name': 'Tel Aviv'}]",
            'connection': 'Cable/DSL'
        })

    def test_regular_swap(self):
        self.run_asserts()

        time.sleep(1)  # to make sure that destination path will be different
        load_geoip_database()

        self.run_asserts()
        self.assertNotEquals(LOOKUP['GEOIP'].filename, self.old_db_path)
        self.assertNotEquals(LOOKUP['GEOIP'].db, self.old_db)

    def test_broken_copy(self):
        self.run_asserts()

        config.SETTINGS['GEOIP_DB_FILE'] = os.path.abspath(os.path.dirname(__file__))
        load_geoip_database()

        self.run_asserts()
        self.assertEquals(LOOKUP['GEOIP'].filename, self.old_db_path)
        self.assertEquals(LOOKUP['GEOIP'].db, self.old_db)

    def test_broken_swap(self):
        self.run_asserts()

        config.SETTINGS['GEOIP_DB_FILE'] = os.path.abspath(__file__)
        load_geoip_database()

        self.run_asserts()
        self.assertEquals(LOOKUP['GEOIP'].filename, self.old_db_path)
        self.assertEquals(LOOKUP['GEOIP'].db, self.old_db)
