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
from django import forms
from . import models


class BitcoinAddressForm(forms.ModelForm):
    class Meta:
        model = models.BitcoinAddress
        fields = ['bitcoin_address',]


class BandwidthForm(forms.ModelForm):
    class Meta:
        model = models.Bandwidth
        fields = ['max_uplink',]
        error_messages = {
            'max_uplink': {
                'required': 'Enter a number for max. uplink.',
                'min_value': 'Ensure max. uplink is greater than or equal to 0.',
                'invalid': 'Enter a number for max. uplink.'
            },
        }

    def clean_max_uplink(self):
        max_uplink = self.cleaned_data['max_uplink']
        if max_uplink > 10000000:
            raise forms.ValidationError(
                'Ensure max. uplink is no greater than 10000000 (10 Gbps).')
        return max_uplink
