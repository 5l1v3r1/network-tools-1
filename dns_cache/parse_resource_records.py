import struct
import time
TYPES = {1: 'A', 2: 'NS', 5: 'CNAME', 6: 'SOA', 12: 'PTR', 15: 'MX ', 28: 'AAAA', 255: '*'}


class DNSPacket:
    def __init__(self, data):
        self.len_name = 0
        self.info = data
        self.header = list(struct.unpack('!6H', self.info[:12])) # Get header as six half-ints
        self._query_name = None
        self._query_name = self.query_name
        try:
            self.query_type = TYPES[self.info[12 + len(self.query_name) + 4]]
        except KeyError:
            self.query_type = "*"
        # print(self.query_type)
        rest = data[12 + len(self.query_name) + 5:]
        self.records = parse_records(self.query_name, rest, self.header[3:])

    @property
    def query_name(self):
        if not self._query_name:
            length = self.info[12:].find(b'\x00')
            self.len_name = length
            name = self.info[12:12 + length]
            format = str(length) + 's'
            return struct.unpack(format, name)[0]
        return self._query_name

    def __bytes__(self):
        length = len(self.query_name)
        offset = 13 + length
        header = struct.pack('!6H', *self.header)
        format = str(length) + 's'
        name = struct.pack(format, self.query_name) + b'\x00'
        records = b''.join([bytes(record) for rs in self.records for record in rs])
        return header + name + self.info[offset:offset + 4] + records


class ResourceRecord:
    def __init__(self, record_name, record_data, record_time):
        self.name = record_name
        self.info = record_data
        self.time = record_time
        self._ttl = int.from_bytes(self.info[6:10] or '\x00', byteorder='big')

    def __bytes__(self):
        return self.info

    @property
    def ttl(self):
        self._ttl = int(self._ttl - time.time() + self.time)
        return self._ttl

        
def parse_records(name, data, counts):
    records = []
    pointer = 0
    sep = b'\xc0\x0c'
    packets = data[2:].split(sep)
    for count in counts:
        temp_records = []
        for i in range(count):
            try:
                temp_records.append(ResourceRecord(name, sep + packets[pointer + i], time.time()))
            except IndexError:
                break
        records.append(temp_records)
        pointer += count
    return records
