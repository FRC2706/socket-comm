#!/usr/bin/python

import socket
import threading
import SocketServer
import signal
import time

stop_requested = False

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global stop_requested
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        print "%s started" % cur_thread.name
        if data[0:4] == "KILL":
            stop_requested = True
        else:
            response = "{}: {}".format(cur_thread.name, data[0:2])
            self.request.sendall(response)
            time.sleep(5)
        print "%s exiting" % cur_thread.name


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

#def client(ip, port, message):
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    sock.connect((ip, port))
#    try:
#        sock.sendall(message)
#        response = sock.recv(1024)
#        print "Received: {}".format(response)
#    finally:
#        sock.close()

def handler(signum, frame):
    print "do whatever, like call thread.interrupt_main()"
    global stop_requested
    stop_requested = True


if __name__ == "__main__":

    signal.signal(signal.SIGINT, handler)

    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9998

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

#   client(ip, port, "Hello World 1")
#   client(ip, port, "Hello World 2")
#   client(ip, port, "Hello World 3")

    while not stop_requested:
        try:
            count = threading.active_count()
            print ("Thread count is %d in %s" % (count, threading.current_thread().name))
            time.sleep(1)
        except Exception as e:
            print "handled %s" % str(e)
            break

    print "shutting down"
    server.shutdown()
    server.server_close()
    print "done"

