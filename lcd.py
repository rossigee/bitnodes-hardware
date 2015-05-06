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
import threading
import time

from django.core.cache import cache


class Display(object):
    def __init__(self):
        self.node_status = None
        self.screen = None

    def show(self, screen):
        self.screen = screen
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.curs_set(0)

        t = threading.Thread(target=self.update)
        t.daemon = True
        t.start()

        self.screen.addstr(1, 2, 'BITNODES HARDWARE', curses.color_pair(1))
        self.screen.addstr(1, 20, 'LOADING', curses.color_pair(3))
        while True:
            event = self.screen.getch()
            if event == ord('q'):
                break

    def update(self):
        while True:
            self.node_status = cache.get('node_status')
            if self.node_status is None:
                time.sleep(1)
                continue

            bitcoind_running = self.node_status.get('bitcoind_running', False)
            lan_address = self.node_status.get('lan_address', '') or ''
            wan_address = self.node_status.get('wan_address', '') or ''
            port = self.node_status.get('port', '') or ''
            blocks = self.node_status.get('blocks', '') or ''
            connections = self.node_status.get('connections', '') or ''

            if bitcoind_running:
                self.screen.addstr(1, 20, 'RUNNING', curses.color_pair(2))
            else:
                self.screen.addstr(1, 20, 'STOPPED', curses.color_pair(4))

            self.screen.addstr(3, 2, 'LAN address')
            self.screen.addstr(3, 14, lan_address, curses.color_pair(2))

            self.screen.addstr(4, 2, 'WAN address')
            self.screen.addstr(4, 14, wan_address, curses.color_pair(2))

            self.screen.addstr(5, 2, 'Port')
            self.screen.addstr(5, 14, str(port), curses.color_pair(2))

            self.screen.addstr(6, 2, 'Blocks')
            self.screen.addstr(6, 14, str(blocks), curses.color_pair(2))

            self.screen.addstr(7, 2, 'Connections')
            self.screen.addstr(7, 14, str(connections), curses.color_pair(2))

            self.screen.refresh()
            time.sleep(10)


def main():
    display = Display()
    curses.wrapper(display.show)


if __name__ == '__main__':
    sys.exit(main())
