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
import json
import requests
import time
from requests.exceptions import ConnectionError

from django.conf import settings

SESSION = requests.Session()


class RpcError(Exception):
    pass


def rpc(cmd, params=None):
    allowed = (
        'getblockcount',
        'getnettotals',
        'getnetworkinfo',
    )
    if cmd not in allowed:
        raise RpcError('Unsupported RPC command: {}'.format(cmd))
    url = 'http://{}:{}/'.format(settings.RPC_HOST, settings.RPC_PORT)
    headers = {
        'content-type': 'application/json',
    }
    auth = (settings.RPC_USER, settings.RPC_PASSWORD)
    data = json.dumps({
        'id': str(int(time.time() * 1e6)),
        'jsonrpc': '1.0',
        'method': cmd,
        'params': params,
    })
    try:
        response = SESSION.post(url, headers=headers, auth=auth, data=data).json()
    except ConnectionError as err:
        raise RpcError(err)
    error = response.get('error', None)
    if error:
        raise RpcError(error)
    result = response.get('result', None)
    assert result
    return result
