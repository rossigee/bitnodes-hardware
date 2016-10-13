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
from django.conf import settings
from hardware.administration import models


class GlobalSettingsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.private = settings.PRIVATE

        try:
            bitcoin_address = models.BitcoinAddress.objects.get(site=request.site)
        except models.BitcoinAddress.DoesNotExist:
            bitcoin_address = models.BitcoinAddress(site=request.site)
            bitcoin_address.save()
        request.bitcoin_address = bitcoin_address

        try:
            bandwidth = models.Bandwidth.objects.get(site=request.site)
        except models.Bandwidth.DoesNotExist:
            bandwidth = models.Bandwidth(site=request.site)
            bandwidth.save()
        request.bandwidth = bandwidth

        response = self.get_response(request)

        return response
