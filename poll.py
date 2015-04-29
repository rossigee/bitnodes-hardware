#!/usr/bin/env python
#
# Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware.settings')

import functools
import json
import logging
import threading
import time
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from collections import deque
from psutil import net_io_counters
from tornado.options import define, options

from django.conf import settings

define('address', type=str, default=settings.WEBSOCKET_HOST)
define('port', type=int, default=settings.WEBSOCKET_PORT)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/poll', PollHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


class PollHandler(tornado.websocket.WebSocketHandler):
    clients = []
    ticks = deque([], maxlen=180)

    def open(self):
        if self not in PollHandler.clients:
            PollHandler.clients.append(self)
            self.write_ticks()

    def on_close(self):
        PollHandler.clients.remove(self)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        self.write_message(message)

    def write_ticks(self):
        _ticks = []
        for tick in PollHandler.ticks:
            _ticks.append(tick)
        message = json.dumps(_ticks)
        logging.info(message)
        self.write_message(message)


class NetworkStat(object):
    def __init__(self, network_interface):
        self.timestamp = time.time()
        self.network_interface = network_interface
        data = self._get_data()
        self.bytes_sent = data.bytes_sent
        self.bytes_recv = data.bytes_recv
        self.sent_bps = 0
        self.recv_bps = 0

    def get(self):
        timestamp = time.time()
        seconds = timestamp - self.timestamp

        if seconds >= 1:
            self.timestamp = timestamp

            data = self._get_data()
            bytes_sent = data.bytes_sent
            bytes_recv = data.bytes_recv

            self.sent_bps = max((bytes_sent - self.bytes_sent) / seconds, 0)
            self.recv_bps = max((bytes_recv - self.bytes_recv) / seconds, 0)

            self.bytes_sent = bytes_sent
            self.bytes_recv = bytes_recv

        return {
            'sent_bps': int(self.sent_bps),
            'recv_bps': int(self.recv_bps),
        }

    def _get_data(self):
        return net_io_counters(pernic=True)[self.network_interface]


def publish():
    io_loop = tornado.ioloop.IOLoop.instance()
    network_stat = NetworkStat(settings.NETWORK_INTERFACE)
    while True:
        tick = {
            'timestamp': int(time.time() * 1000),  # In ms
            'network': network_stat.get(),
        }
        PollHandler.ticks.append(tick)
        message = json.dumps([tick])
        logging.info(message)
        for client in PollHandler.clients:
            io_loop.add_callback(functools.partial(client.on_message, message))
        time.sleep(5)


if __name__ == '__main__':
    threading.Thread(target=publish).start()
    tornado.options.parse_command_line()
    application = Application()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port, address=options.address)
    tornado.ioloop.IOLoop.instance().start()
