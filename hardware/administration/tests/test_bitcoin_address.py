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
from django.test import TestCase
from hardware.administration.models import get_bitcoin_address_version


class TestBitcoinAddress(TestCase):
    def test_bitcoin_address_version(self):
        addresses = [
            '1DNgdwsFkX1dtCnYiAKSd4zxAuwgv2jhie',  # pubkey = 0
            '1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i',  # pubkey = 0
            '13p1ijLwsnrcuyqcTvJXkq2ASdXqcnEBLE',  # pubkey = 0
            '3CMNFxN1oHBc4R1EpboAL5yzHGgE611Xou',  # script = 5
            'mo9ncXisMeAoXwqcV5EWuyncbmCcQN4rVs',  # testnet pubkey = 111
            '11111111111111111111ufYVpS',  # short pubkey = 0
        ]
        versions = []
        for address in addresses:
            versions.append(get_bitcoin_address_version(address))
        self.assertEqual(versions, [0, 0, 0, 5, 111, 0])
