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

from django.conf import settings
from django.core.cache import cache
from hardware.celery import app
from hardware.rpc import RpcError, rpc
from hardware.utils import get_lan_address, get_wan_address

logger = logging.getLogger(__name__)


@app.task
def node_status_task():
    network_info = {}
    try:
        network_info = rpc('getnetworkinfo')
    except RpcError as err:
        logger.debug(err)

    block_count = None
    try:
        block_count = rpc('getblockcount')
    except RpcError as err:
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
    }
    logger.debug('node_status: %s', node_status)
    cache.set('node_status', node_status, None)  # Persistent cache
