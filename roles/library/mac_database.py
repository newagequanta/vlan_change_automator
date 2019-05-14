#!/usr/local/bin/python

from ansible.module_utils.basic import *
import re
import csv
import json

def main():
    '''
    Ansible arguments supported:
        - hostname - The hostname of the switch that will appear in the
                     database
        - raw_data - Output of the "show mac address-table"
        - dest     - OPTIONAL (future) name of the file to store the database
    '''
    fields = {
        'hostname': {'default': True, 'type': 'str'},
        'raw_data': {'default': True, 'type': 'str'},
        'dest': {'default': False, 'type': 'path'}
    }

    #Mandatory for Ansible
    module = AnsibleModule(argument_spec=fields)

    #RegEx to find MAC
    mac_exp = re.compile(r'(([\d,A-F,a-f]{4}\.){2}[\d,A-F,a-f]{4})')

    macs = []
    macs_dict_hostname = {}

    hostname = module.params['hostname']
    raw_data = module.params['raw_data'].split('\n')
    dest = module.params['dest']

    #Load the file into a dictionary if it exists, create if it does not
    try:
        f_obj = open('mac_db_mac_based.json', 'r')
        macs_dict_mac = json.load(f_obj)['macs'][0]
        f_obj.close()
    except:
        macs_dict_mac = {}
    #for line in module.params['raw_data']:
    for line in raw_data:
        re_result = mac_exp.findall(line)
        if re_result:
            line_list = line.split()
            mac_addr = line_list[1]
            if_num = line_list[3]

            #Experimental CSV format
            macs.append([hostname, mac_addr, if_num])

            #Experimental JSON format keyed off the switch hostname
            if hostname in macs_dict_hostname:
                macs_dict_hostname[hostname].append([mac_addr, if_num])
            else:
                macs_dict_hostname[hostname] = [[mac_addr, if_num]]

            #Currently supported JSON format keyed off the MAC addresses
            macs_dict_mac[mac_addr] = [hostname, if_num]

    f_obj = open('mac_db_mac_based.json', 'w')
    #json.dump({"macs": [macs_dict_mac]}, f_obj)
    json.dump(macs_dict_mac, f_obj)
    f_obj.close()

    return_value = {"hello": "world"}
    module.exit_json(change=False, meta=return_value)

if __name__ == '__main__':
    main()
