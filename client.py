#!/usr/bin/python

import argparse
import socket
import sys

received=None

parser = argparse.ArgumentParser()
parser.add_argument("message", nargs='?', help="string to send", type=str, default="Default Test Message")
parser.add_argument("-H", "--host", help="host to connect to", type=str, default="0.0.0.0")
parser.add_argument("-p", "--port", help="port to connect to", type=int, default=9000)
args = parser.parse_args()

port = args.port
host = args.host
message = args.message

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send message
    sock.connect((host, port))
    sock.sendall(message + "\n")

    # Receive data from the server and shut down
    received = sock.recv(1024)
except Exception as e:
    print "sock communication failed %s" % str(e)
finally:
    sock.close()

if received:
    print "To %s port %d:" % (host, port)
    print "Sent:     {}".format(message)
    print "Received: {}".format(received)

