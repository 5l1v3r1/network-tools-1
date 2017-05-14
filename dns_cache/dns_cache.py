# !/usr/bin/python3
# -*- coding: utf-8 -*-
import socket
import struct
import time

from parse_resource_records import DNSPacket

CACHE = {}


def ask_forwarder_server(data, addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    with sock:
        try:
            sock.sendto(data, addr)
            response = sock.recv(4096)
            return DNSPacket(response)
        except socket.error:
            # Fix for availability
            return ask_forwarder_server(data, ('8.8.8.8', 53))


class CacheServer:
    def __init__(self, forwarder, sock):
        self.forwarder = forwarder
        self.sock = sock

    def forward(self, data, key):
        pack = ask_forwarder_server(data, self.forwarder)
        CACHE[key] = pack.records
        print('Got data from forwarder')
        return bytes(pack)

    def resolve(self, data, client):
        pack = DNSPacket(data)
        key = pack.query_name
        name = self.deserialize_name(key, 0)
        print(name)
        source = ""
        if key in CACHE:
            packet = self.pack_packet(key, data)
            source = "cache"
            self.sock.sendto(packet, client)
        else:
            source = "forwarder"
            self.sock.sendto(self.forward(data, key), client)
        request = [client[0], pack.query_type, name, source]
        print(", ".join(request))

    def deserialize_name(self, data, offset):
        domain = ''
        data += b"\x00"
        while True:
            length = data[offset]
            offset += 1
            if length & 0xC0 == 0 and length > 0:
                domain += data[offset: offset + length].decode('utf-8') + '.'
                offset += length
            else:
                return domain

    def pack_packet(self, key, data):
        cdata = CACHE[key]
        for records in cdata:
            for record in records:
                if time.time() - record.time >= record.ttl:
                    print('Going to ask forwarder about {} [because of TTL]'.format(record.name))
                    return self.forward(data, key)
        print('Got data from cache')
        end = 12 + data[12:].find(b'\x00') + 5
        question = data[12:end]
        counts = struct.pack('!4H', 1, len(cdata[0]), len(cdata[1]), len(cdata[2]))
        records = b''.join([bytes(record) for rs in cdata for record in rs])
        packet = data[:2] + b'\x81\x80' + counts + question + records
        return packet
