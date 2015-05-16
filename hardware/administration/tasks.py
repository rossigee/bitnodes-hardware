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
import os
import platform
import pytz
import subprocess
import time
from celery.signals import celeryd_init
from datetime import datetime
from psutil import boot_time, disk_partitions, disk_usage, virtual_memory

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import management
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from hardware.celery import app

logger = logging.getLogger(__name__)


@app.task
def bandwidth_task():
    site = Site.objects.get(id=settings.SITE_ID)
    try:
        bandwidth = site.bandwidth
    except ObjectDoesNotExist:
        return
    command = [
        '/bin/bash', os.path.join(settings.BASE_DIR, 'bandwidth_control.sh'),
        '-i', settings.NETWORK_INTERFACE,
        '-p', str(settings.BITCOIN_PORT),
        '-u', str(bandwidth.max_uplink),
    ]
    logger.debug('command: %s', command)
    if not settings.DEBUG:
        subprocess.call(command)


@app.task
def start_stop_bitcoind_task(command):
    if not settings.DEBUG:
        program = '{}-bitcoind'.format(settings.SUPERVISOR['NAME'])
        logger.debug('supervisor %s %s', command, program)
        management.call_command('supervisor', command, program)


@app.task
def shutdown_task(method):
    # Stop bitcoind gracefully to avoid SIGKILL from shutdown command
    start_stop_bitcoind_task('stop')
    command = [
        '/usr/bin/sudo',
        '/sbin/shutdown',
        method,
        'now',
    ]
    logger.debug('command: %s', command)
    if not settings.DEBUG:
        subprocess.call(command)


@app.task
def system_info_task():
    """
    Enumerates and caches processor, memory and storage information.
    """
    processor = None
    system = platform.system()
    if system == 'Linux':
        with open('/proc/cpuinfo') as cpuinfo:
            for line in cpuinfo:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    if key in ('model name', 'Processor'):
                        processor = value.strip()
    elif system == 'Darwin':
        processor = subprocess.check_output(
            ['/usr/sbin/sysctl', '-n', 'machdep.cpu.brand_string']).strip()
    else:
        processor = platform.processor()

    # Physical devices only
    partitions = {}
    for partition in disk_partitions():
        partitions[partition.mountpoint] = disk_usage(partition.mountpoint)

    boot_datetime = datetime.utcfromtimestamp(boot_time()).replace(tzinfo=pytz.UTC)

    system_info = {
        'boot_datetime': boot_datetime,
        'processor': processor,
        'memory': virtual_memory().total,
        'storage': partitions,
    }
    logger.debug('system_info: %s', system_info)
    cache.set('system_info', system_info, 3600)


@celeryd_init.connect
def startup_task(sender=None, conf=None, **kwargs):
    cache.clear()
    bandwidth_task()
    system_info_task()
