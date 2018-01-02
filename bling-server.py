#!/usr/bin/python

import multiprocessing
import socket
import time
import sys

from neopixel import *

# LED strip configuration:
LED_COUNT      = 120      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()

def handle(data):
    import logging
    import signal

    def clear():
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, 0)
        strip.show()

    def sig_term_handler(signal,frame):
        logger.debug("Received SIGTERM")
        clear()
        sys.exit(0)

    def colorWipe(strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

    signal.signal(signal.SIGTERM, sig_term_handler)

    process = multiprocessing.current_process()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("process-%r (%r)" % (process.name, process.pid,))

    logger.debug("Received data %r", data)
    # Real work goes here
    #-------------------------------------------------------------------------#
    colorWipe(strip, Color(255, 0, 0))  # Red wipe
    colorWipe(strip, Color(0, 255, 0))  # Blue wipe
    colorWipe(strip, Color(0, 0, 255))  # Green wipe
    clear()
    #-------------------------------------------------------------------------#
    logger.debug("Terminating")

class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        process = None

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

            if process and process.is_alive():
               self.logger.debug("terminating child process")
               process.terminate()
               process.join()

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
        logging.info("Listening on port %r", port)
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
