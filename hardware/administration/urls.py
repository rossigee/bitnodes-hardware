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
from django.conf.urls import url
from django.contrib.auth.views import login, logout
from . import views

urlpatterns = [
    url(r'^$', views.administration, name='administration'),
    url(r'^system-info/$', views.system_info, name='system_info'),
    url(r'^login/$', login, {'template_name': 'administration/login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': 'administration'}, name='logout'),
    url(r'^change-password/$', views.change_password, name='change_password'),
    url(r'^set-bitcoin-address/$', views.set_bitcoin_address, name='set_bitcoin_address'),
    url(r'^set-bandwidth/$', views.set_bandwidth, name='set_bandwidth'),
    url(r'^start-stop-bitcoind/$', views.start_stop_bitcoind, name='start_stop_bitcoind'),
    url(r'^shutdown/$', views.shutdown, name='shutdown'),
]
