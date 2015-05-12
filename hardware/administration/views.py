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
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import resolve_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from . import forms
from .tasks import bandwidth_task, start_stop_bitcoind_task, shutdown_task


@user_passes_test(lambda u: u.is_superuser)
def administration(request, template='administration/administration.html'):
    system_info = cache.get('system_info')
    context = {
        'system_info': system_info,
    }
    return render(request, template, context)


def system_info(request, template='administration/system_info.html'):
    if not request.user.is_superuser:
        return HttpResponse('Not authenticated.', status=403)
    return administration(request, template=template)


@sensitive_post_parameters()
@user_passes_test(lambda u: u.is_superuser)
def change_password(request, template='administration/change_password.html',
                    change_password_form=PasswordChangeForm):
    if request.method == 'POST':
        form = change_password_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password updated.')
            return HttpResponseRedirect(resolve_url('administration'))
    else:
        form = change_password_form(user=request.user)
    context = {
        'form': form,
    }
    return render(request, template, context)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def set_bitcoin_address(request, bitcoin_address_form=forms.BitcoinAddressForm):
    form = bitcoin_address_form(request.POST, instance=request.bitcoin_address)
    if form.is_valid():
        form.save()
        messages.success(request, 'Bitcoin address updated.')
    else:
        msg = form.errors[form.errors.keys()[0]][0]  # First error message
        messages.error(request, msg)
    return HttpResponseRedirect(resolve_url('administration'))


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def set_bandwidth(request, bandwidth_form=forms.BandwidthForm):
    form = bandwidth_form(request.POST, instance=request.bandwidth)
    if form.is_valid():
        form.save()
        bandwidth_task.delay()
        messages.success(request, 'Bandwidth limit updated.')
    else:
        msg = form.errors[form.errors.keys()[0]][0]  # First error message
        messages.error(request, msg)
    return HttpResponseRedirect(resolve_url('administration'))


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def start_stop_bitcoind(request):
    command = request.POST.get('command', None)
    commands = {
        'start': 'starting',
        'stop': 'stopping',
    }
    if command not in commands.keys():
        command = None
    if command is None:
        return HttpResponse('Invalid command.', status=400)
    start_stop_bitcoind_task.delay(command)
    return HttpResponse(
        'Bitcoin client is {}. This can take a few minutes.'.format(commands.get(command)))


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(['POST'])
def shutdown(request):
    method = request.POST.get('method', None)
    methods = {
        '-r': 'restart',
        '-h': 'shutdown',
    }
    if method not in methods.keys():
        method = None
    if method is None:
        return HttpResponse('Invalid shutdown method.', status=400)
    shutdown_task.delay(method)
    return HttpResponse(
        'System {} in progress. This can take a few minutes.'.format(methods.get(method)))
