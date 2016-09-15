#!/usr/bin/python
# a ansible inventory script that will output the inventory for vagrant development setup
# based on https://gist.github.com/lorin/4cae51e123b596d5c60d
import argparse
import json
import os
import sys

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Vagrant inventory script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--host')
    return parser.parse_args()


def load_cfg():
    cfg = yaml.load(open("group_vars/all"))
    jail_host = {}
    for host in cfg['hosts_ips']:
        if host.startswith("service"):
            jail_host[host] = host
            with open("host-{}.yml".format(host)) as f:
                servicecfg = yaml.load(f)
                for play in servicecfg:
                    for role in play['roles']:
                        if role['role'] == "jail":
                            jail_host[role['name']] = host
    cfg['jail_host'] = jail_host
    return cfg


def list_running_hosts():
    cfg = load_cfg()
    return cfg['jail_host'].keys()


def get_host_details(host):
    cfg = load_cfg()
    ip = "{}.{}".format(cfg["internal_network"], cfg['hosts_ips'][host])
    pwd = os.path.dirname(__file__)
    return {'ansible_ssh_host': ip,
            'ansible_ssh_port': 22,
            'ansible_ssh_user': 'vagrant',
            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
            'ansible_ssh_private_key_file': '{}/.vagrant/machines/{}/virtualbox/private_key'.format(
                pwd, cfg['jail_host'][host])}


def main():
    args = parse_args()
    if args.list:
        hosts = list_running_hosts()
        json.dump({'vagrant': hosts}, sys.stdout)
    else:
        details = get_host_details(args.host)
        json.dump(details, sys.stdout)

if __name__ == '__main__':
    main()
