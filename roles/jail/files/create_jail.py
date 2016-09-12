import subprocess
import sys

(ezjail_default_flavour, name, ip,
 internal_network, external_network, internet_visible,
 internal_if, external_if) = sys.argv[1:]

ip_addresses = []

if external_if and internet_visible == "True":
    ip_addresses.append(external_if + "|" + external_network + "." + ip)

if internal_if:
    ip_addresses.append(internal_if + "|" + internal_network + "." + ip)

subprocess.check_call(["ezjail-admin", "create", "-f", ezjail_default_flavour,
                       name, ",".join(ip_addresses)])
