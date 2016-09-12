# host-devel contains all the jails in one vagrant host!
# files/generate_devel.py generates the file
---
- name: configure devel
  hosts: devel
  gather_facts: no
  connection: local
  become: yes
  roles: []
