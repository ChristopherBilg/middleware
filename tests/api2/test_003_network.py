#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

import pytest
import sys
import os
apifolder = os.getcwd()
sys.path.append(apifolder)
from auto_config import ha, interface
from functions import GET, PUT


# Only read and run HA test on HA else run non-HA tests.
if ha and "domain" in os.environ:
    domain = os.environ["domain"]
    gateway = os.environ["gateway"]
    hostname = os.environ["hostname"]
    hostname_b = os.environ["hostname_b"]
    hostname_virtual = os.environ["hostname_virtual"]
    primary_dns = os.environ["primary_dns"]
    secondary_dns = os.environ["secondary_dns"]
    ip = os.environ["controller1_ip"]

    def test_01_set_network_for_ha():
        payload = {
            "domain": domain,
            "ipv4gateway": gateway,
            "hostname": hostname,
            "hostname_b": hostname_b,
            "hostname_virtual": hostname_virtual,
            "nameserver1": primary_dns,
            "nameserver2": secondary_dns
        }
        results = PUT("/network/configuration/", payload, controller_a=ha)
        assert results.status_code == 200, results.text

else:
    from auto_config import hostname, domain, ip

    def test_02_get_default_network_general_summary():
        global gateway, nameservers
        results = GET("/network/general/summary/")
        assert results.status_code == 200
        assert isinstance(results.json(), dict), results.text
        assert isinstance(results.json()['default_routes'], list), results.text
        assert isinstance(results.json()['nameservers'], list), results.text
        # get default_routes to set ipv4gateway for network/configuration
        gateway = results.json()['default_routes'][0]
        # get nameservers to set nameservers for network/configuration
        nameservers = results.json()['nameservers']

    def test_03_configure_setting_domain_hostname_and_dns():
        global payload, results
        payload = {
            "domain": domain,
            "hostname": hostname,
            "ipv4gateway": gateway,
        }
        # set nameservers
        for num, nameserver in enumerate(nameservers, start=1):
            payload[f'nameserver{num}'] = nameserver
        results = PUT("/network/configuration/", payload)
        assert results.status_code == 200, results.text
        assert isinstance(results.json(), dict), results.text

    @pytest.mark.parametrize('dkeys', ["domain", "hostname", "ipv4gateway", "nameserver1"])
    def test_04_looking_put_network_configuration_output_(dkeys):
        assert results.json()[dkeys] == payload[dkeys], results.text

    def test_05_get_network_configuration_info_():
        global results
        results = GET("/network/configuration/")
        assert results.status_code == 200, results.text
        assert isinstance(results.json(), dict), results.text

    @pytest.mark.parametrize('dkeys', ["domain", "hostname", "ipv4gateway", "nameserver1"])
    def test_06_looking_get_network_configuration_output_(dkeys):
        assert results.json()[dkeys] == payload[dkeys], results.text

    def test_07_get_network_general_summary():
        global results
        results = GET("/network/general/summary/")
        assert results.status_code == 200, results.text
        assert isinstance(results.json(), dict), results.text

    def test_08_verify_network_general_summary_nameservers():
        for nameserver in nameservers:
            assert nameserver in results.json()['nameservers'], results.text

    def test_09_verify_network_general_summary_default_routes():
        assert gateway in results.json()['default_routes'], results.text

    def test_09_verify_network_general_summary_ips():
        for value in results.json()['ips'][interface]['IPV4']:
            if ip in value:
                assert ip in value, results.text
