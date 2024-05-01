#!/usr/bin/python3

"""
Script to read data from a KACO solar inverter

This script reads data via ModbusTCP from the Inverter.
It is tested with an KACO 5.0 NX3 M2
"""

import sys
import json
import argparse
import pathlib
import socket
import time

from pymodbus.client import ModbusTcpClient

# Argument Parster
parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', dest='ipaddress', type=socket.gethostbyname, default='127.0.0.1',
                    help='Hostname or IP address (default:127.0.0.1)')
parser.add_argument('-p', '--port', dest='port',
                    help='ModbusTCP Port (default: 502)', default=502)
parser.add_argument('-s', '--slave', dest='slave', default=3,
                    help='Modbus Slave address (default: 3)')
parser.add_argument('-o', '--output', dest='outfile', type=pathlib.Path,
                    help='Outpout json file')
parser.add_argument('-P', '--print', dest='print', action='store_true', default=False,
                    help='print to StdOut')
parser.add_argument('-c', '-config', dest='config', default='/etc/kaco/modbus.json',
                    help='Config file (default: /etc/kaco/modbus.json)')
parser.add_argument('-r', '-retries', dest='retries', default=1,
                    help='retries if register read failed (default: 1)')
args = parser.parse_args()

# setup Modbus TCP Client        
def setup_client():
    cl = ModbusTcpClient(
            args.ipaddress,
            args.port,
            timeout=1,
            retry_on_empty=False,
            retries=1)
    cl.connect()
    return cl

# read modbus register
#   -client handle
#   -json key
#   -number of register to read
def rmodbusreg(client, key, Size):
    try:
        i=0
        while (i < args.retries):
            i += 1
            request = client.read_holding_registers(
                address=int(key),
                count=Size,
                slave=args.slave)
            if not request.isError():
                return request
            time.sleep (0.1)
        return i
    except:
        print ("[ERROR] Connection Error")
        sys.exit(1)

def unsignedToSigned(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, 'little', signed=False), 'little', signed=True)

def signedToUnsigned(n, byte_count):
    return int.from_bytes(n.to_bytes(byte_count, 'little', signed=True), 'little', signed=False)

def readconfig(filename):
    try:
        # open json file
        with open(filename) as user_file:
            file_contents = user_file.read()
        # read json object as list object
        jo = json.loads(file_contents)
        return jo
    except:
        print ("Could not read config")

def writefile(filename, content):
    try:
        f = open(filename, "w")
        f.write(json.dumps(content, indent=2))
        f.close()
    except:
        print("could not write file")
        sys.exit(1)
    
def main():
    config=readconfig(args.config)
    client=setup_client()
    data = {}
    for key in config:
        value = config[key]
        Description=config[key]['Description']
        Format=config[key]['Format']
        Size=config[key]['Size']
        unitread=config[key]['Unit']
        read=bool(config[key]['read'])
        if (read):
            request = rmodbusreg(client, key, Size)
            if isinstance(request, int):
                data[key] = {'Failed': str(request), 'Description': Description}
            else:
                if ( Format == "string"):
                    outstr=""
                    for val in request.registers:
                        outstr=outstr + chr(val >> 8) + chr(val & 0x00ff)
                    outstr = outstr.replace('\u0000',"") # remove null strings
                    data[key] = {'Unit': str(unitread), 'Value': outstr, 'Description': Description}

                if ( Format == "acc32"):
                    val=request.registers
                    y=(val[0]<<16) + val[1]
                    data[key] = {'Unit': str(unitread), 'Value': y, 'Description': Description}

                if ( Format == "sunssf"):
                    val=request.registers[0]
                    data[key] = {'Unit': str(unitread), 'Value': val, 'Description': Description}

                if ( Format == "int16"):
                    val=int(request.registers[0])
                    data[key] = {'Unit': str(unitread), 'Value': val, 'Description': Description}

                if ( Format == "uint16" ):
                    val=unsignedToSigned(request.registers[0], 2) 
                    data[key] = {'Unit': str(unitread), 'Value': val, 'valhex': hex(val), 'Description': Description}

    client.close()
    if ( args.outfile ):
        writefile(args.outfile, data)
    elif (args.print):
        print(json.dumps(data, sort_keys=True, indent=2))
    else:
        print(json.dumps(data))

if __name__ == '__main__':
    main()
