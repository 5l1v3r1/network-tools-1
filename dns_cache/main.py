#!/usr/bin/python3
import select
import socket
import sys

from argparse import ArgumentParser
from dns_cache import CacheServer


def parse_args():
    parser = ArgumentParser(description='Simple forwarding caching dns server')
    parser.add_argument('-p', '--port', help='Port to listen', default=53, type=int)
    parser.add_argument('-f', '--forwarder', help='Forwarder IP/IP:port', type=str)
    return parser.parse_args()

def parse_forwarder(forwarder):
    forwarder_port = 53
    
    if '127.0.0.1' in forwarder:
        print('Setting server as forwarder is forbidden because of eternal loop')
        sys.exit(1)
    
    if ':' in forwarder:
        try:
            forwarder_data = forwarder.split(':')
            forwarder_ip = forwarder_data[0]
            forwarder_port = int(forwarder_data[1])
        except:
            print('Wrong forwarder address!')
            sys.exit(1)
    else:
        forwarder_ip = forwarder
    return (forwarder_ip, forwarder_port)

def main():
    args = parse_args()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    forwarder_addr = parse_forwarder(args.forwarder)
    with sock:
        try:
            sock.bind(('', args.port))
            print("Server was succesfully started")
            server = CacheServer(forwarder_addr, sock)
            while True:
                try:
                    ready, _, _ = select.select([sock], [], [], 0.4)
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    print("Ending work")
                    break
                except Exception as e:
                    print(e)
                for x in ready:
                    data, addr = sock.recvfrom(4096)
                    print("Got a new client - {}:{}".format(addr[0], addr[1]))
                    server.resolve(data, addr)
                    print()
        except PermissionError:
            print("Try launch as administrator!")
        except OSError:
            print("Port is already used, try to specify different one in arguments")
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    main()