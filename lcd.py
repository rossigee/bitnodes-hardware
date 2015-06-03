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

import curses
import sys
import time
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache


def get_cpu_temp():
    """
    CPU temperature should be below 80C for normal operation.
    """
    celcius = None
    temp = '/sys/devices/virtual/thermal/thermal_zone0/temp'
    if os.path.exists(temp):
        celcius = int(open(temp).read().strip()) / 1000
    return celcius


def get_exchange_rate():
    ticks = settings.REDIS_CONN.lrange('exchange_rate', 0, -1)
    if len(ticks) == 0:
        return (None, None)
    curr = ticks[0]
    prev = curr
    if len(ticks) > 1:
        prev = ticks[1]
    curr = Decimal(curr).quantize(Decimal('.01'))
    prev = Decimal(prev).quantize(Decimal('.01'))
    return (curr, prev)


class Display(object):
    def __init__(self):
        self.node_status = None
        self.screen = None

    def show(self, screen):
        self.screen = screen

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.white = curses.color_pair(1)

        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.green = curses.color_pair(2)

        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.yellow = curses.color_pair(3)

        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        self.red = curses.color_pair(4)

        curses.curs_set(0)

        self.addstr(1, 1, 'BITNODES HARDWARE', self.white)
        self.addstr(1, 19, 'LOADING', self.yellow)

        while True:
            time.sleep(self.update())

    def update(self):
        self.node_status = cache.get('node_status')
        if self.node_status is None:
            return 1

        bitcoind_running = self.node_status.get('bitcoind_running', False)
        lan_address = self.node_status.get('lan_address', '')
        wan_address = self.node_status.get('wan_address', '')
        port = self.node_status.get('port', '')
        user_agent = self.node_status.get('user_agent', '')
        blocks = self.node_status.get('blocks', '')
        connections = self.node_status.get('connections', '')
        cpu_temp = get_cpu_temp()
        (curr_exchange_rate, prev_exchange_rate) = get_exchange_rate()

        if bitcoind_running:
            self.addstr(1, 19, 'RUNNING', self.green, clr=True)
        else:
            self.addstr(1, 19, 'STOPPED', self.red, clr=True)

        self.addstr(3, 1, 'LAN address', self.white)
        self.addstr(3, 13, lan_address, self.green, clr=True)

        self.addstr(4, 1, 'WAN address', self.white)
        self.addstr(4, 13, wan_address, self.green, clr=True)

        self.addstr(5, 1, 'Port', self.white)
        self.addstr(5, 13, port, self.green, clr=True)

        self.addstr(6, 1, 'User agent', self.white)
        self.addstr(6, 13, user_agent, self.green, clr=True)

        self.addstr(7, 1, 'Blocks', self.white)
        self.addstr(7, 13, blocks, self.green, clr=True)

        self.addstr(8, 1, 'Connections', self.white)
        color = self.red
        if connections and int(connections) > 8:
            color = self.green
        self.addstr(8, 13, connections, color, clr=True)

        self.addstr(9, 1, 'CPU temp', self.white)
        if cpu_temp:
            color = self.red
            if cpu_temp <= 80:
                color = self.green
            cpu_temp = '%dC' % cpu_temp
            self.addstr(9, 13, cpu_temp, color, clr=True)

        self.addstr(10, 1, 'USD/BTC', self.white)
        if curr_exchange_rate:
            color = self.yellow
            if curr_exchange_rate > prev_exchange_rate:
                color = self.green
            elif curr_exchange_rate < prev_exchange_rate:
                color = self.red
            self.addstr(10, 13, curr_exchange_rate, color, clr=True)

        self.screen.refresh()
        return 15

    def addstr(self, row, col, value, color, clr=False):
        if value is None:
            value = ''
        value = str(value)
        if clr:
            self.screen.move(row, col)
            self.screen.clrtoeol()
        self.screen.addstr(row, col, value, color)


def main():
    display = Display()
    curses.wrapper(display.show)


if __name__ == '__main__':
    sys.exit(main())
