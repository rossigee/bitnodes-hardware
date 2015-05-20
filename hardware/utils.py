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
import logging
import requests
from psutil import net_if_addrs
from socket import AF_INET

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_lan_address():
    lan_address = cache.get('lan_address')
    if lan_address is None:
        for address in net_if_addrs().get(settings.NETWORK_INTERFACE):
            if address.family == AF_INET:
                lan_address = address.address
                cache.set('lan_address', lan_address, 600)
                return lan_address
    return lan_address


def get_wan_address():
    wan_address = cache.get('wan_address')
    if wan_address is None:
        url = 'https://dazzlepod.com/ip/me.json'
        headers = {'user-agent': settings.USER_AGENT}
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as err:
            logger.debug(err)
        else:
            if response.status_code == 200:
                wan_address = response.json().get('ip')
                cache.set('wan_address', wan_address, 600)
    return wan_address
