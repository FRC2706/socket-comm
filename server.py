#!/usr/bin/python

import multiprocessing
import socket
import time

def handle(data):
    import logging

    process = multiprocessing.current_process()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("process-%r (%r)" % (process.name, process.pid,))

    logger.debug("Received data %r", data)
    # Real work goes here
    time.sleep(5)
    logger.debug("Terminating")

class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)
        self.data = ""

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Connected %r", address)

            try:
                while True:
                    data = conn.recv(1024)
                    if data == "":
                        self.logger.debug("Socket closed remotely")
                        self.logger.debug("Closing socket")
                        conn.close()
                        break
             
                    self.logger.debug("Received data %r", self.data)
                    conn.sendall(data)
                    self.logger.debug("Sent data")
                    self.data = data
            except:
                self.logger.exception("Problem handling request")
            finally:
                # Doesn't hurt to close twice (just in case we got here via an exception
                conn.close()

            if self.data[0:4] == "KILL":
                self.logger.debug("got KILL message")
            else:
                process = multiprocessing.Process(target=handle, args=(self.data,))
                process.daemon = True
                process.start()


if __name__ == "__main__":
    import logging
    import argparse

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="port to listen on", type=int, default=9000)
    parser.parse_args()
    args = parser.parse_args()

    port = args.port

    server = Server("0.0.0.0", port)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
