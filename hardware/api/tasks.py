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
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from hardware.celery import app
from hardware.rpc import RpcError, rpc
from hardware.utils import get_lan_address, get_wan_address

logger = logging.getLogger(__name__)


@app.task
def node_status_task():
    error = None

    network_info = {}
    try:
        network_info.update(rpc('getnetworkinfo'))
    except RpcError as err:
        error = err
        logger.debug(err)

    try:
        network_info.update(rpc('getnettotals'))
    except RpcError as err:
        error = err
        logger.debug(err)

    block_count = None
    try:
        block_count = rpc('getblockcount')
    except RpcError as err:
        error = err
        logger.debug(err)

    bitcoind_running = False
    if network_info or block_count:
        bitcoind_running = True

    node_status = {
        'bitcoind_running': bitcoind_running,
        'lan_address': get_lan_address(),
        'wan_address': get_wan_address(),
        'port': settings.BITCOIN_PORT,
        'user_agent': network_info.get('subversion', None),
        'protocol_version': network_info.get('protocolversion', None),
        'blocks': block_count,
        'connections': network_info.get('connections', None),
        'bytes_sent': network_info.get('totalbytessent', None),
        'bytes_recv': network_info.get('totalbytesrecv', None),
    }
    if error and isinstance(error.message, dict):
        node_status.update({
            'error': error.message.get('message', '').split()[0].upper(),
        })
    logger.debug('node_status: %s', node_status)
    cache.set('node_status', node_status, 600)


@app.task
def exchange_rate_task():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/USD.json'
    headers = {'user-agent': settings.USER_AGENT}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=settings.HTTP_TIMEOUT)
    except requests.exceptions.RequestException as err:
        logger.debug(err)
    else:
        if response.status_code == 200:
            key = 'exchange_rate'
            settings.REDIS_CONN.lpush(key, Decimal(response.json()['bpi']['USD']['rate_float']))
            settings.REDIS_CONN.ltrim(key, 0, 96)
