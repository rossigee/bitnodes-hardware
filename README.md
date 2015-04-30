![Bitnodes Hardware](static/img/bitnodes-hardware.png?raw=true "Bitnodes Hardware")

Thank you for purchasing Bitnodes Hardware!

The Bitnodes Hardware is an easy-to-use device that allows you to participate in the Bitcoin peer-to-peer network by verifying and relaying transactions and blocks across the network.

## Hardware Features
1. Amlogic quad-core ARM Cortex-A5 1.5GHz CPU
1. 1GB DDR3 SDRAM
1. Hardware RNG
1. 8GB eMMC for Operating System
1. 64GB Micro SD UHS-1 Class 10 for User Data
1. 3.2-inch TFT LCD
1. Gigabit Ethernet (CAT6 cable included)
1. 5V 2A DC Input (APAC/AU/EU/US/ compatible)
1. Bitnodes Hardware Clear Acrylic Case

## Software Features
1. Powered by the latest version of Ubuntu operating system.
1. Latest version of Bitcoin client synced up to the latest block prior to dispatch.
1. Built-in open source web-based administration interface:
    * Start or stop Bitcoin client.
    * Restart or shutdown your Bitnodes Hardware.
    * Set or unset bandwidth limit for Bitcoin client.
1. Public status page with real-time stats for your Bitnodes Hardware.

## Quickstart
1. Unpack your Bitnodes Hardware.
1. Plug in the power cord and the Ethernet cable.
1. Note down the LAN IP address (`LAN_IP_ADDRESS`) and the WAN IP address (`WAN_IP_ADDRESS`) for your Bitnodes Hardware displayed on the LCD.
1. Using another computer in the same LAN, open the administration page at `http://LAN_IP_ADDRESS:8080` with a web browser.
1. Click on the **ADMINISTRATION** link at the top-right corner of the page.
1. Login using `admin` as the password.
1. Click **CHANGE PASSWORD** to change your password now.
1. Your Bitnodes Hardware will take a couple hours to sync up with the latest blocks from the network.
1. Once synced, your Bitnodes Hardware will start to verify and relay new transactions and blocks.

## Port Forwarding
Port forwarding must be configured on your router to allow incoming connections to your Bitnodes Hardware. Look for **Port Forwarding** page or similar in your router administration page and add the entries as shown in the table below.

Note that the equivalent fields may be named differently depending on the make and model of your router. Be sure to replace `LAN_IP_ADDRESS` with the actual LAN IP address for your Bitnodes Hardware.

| Service Name       | Internal IP Address | Internal Port | External Port |
|--------------------|---------------------|---------------|---------------|
| Public status page | `LAN_IP_ADDRESS`    | 80            | 80            |
| Bitcoin client     | `LAN_IP_ADDRESS`    | 8333          | 8333          |

Restart your Bitnodes Hardware from its administration page for the changes to take effect. You should now be able to access the public status page for your Bitnodes Hardware from `http://WAN_IP_ADDRESS`. Enter your `WAN_IP_ADDRESS` in https://getaddr.bitnodes.io/#join-the-network to confirm that your Bitcoin client is accepting incoming connections.

## Remote Access
SSH is enabled on your Bitnodes Hardware if you need remote shell access from another computer in the same LAN. Login as `bitnodes` with `bitnodes` as the password. Be sure to change the password as soon as you are logged in. `root` password has been removed for security reason. You will need to be logged in as `bitnodes`, which has sudo access, to execute privileged commands.

    $ ssh bitnodes@LAN_IP_ADDRESS
    $ passwd

## Help
If you need assistance setting up your Bitnodes Hardware, please send an email to service@bitnodes.io.

## Developer Guide
The sections below describe the steps that were taken to configure your Bitnodes Hardware prior to dispatch. These sections are for your reference only. You are NOT required to execute any of the steps below to start your Bitnodes Hardware.

### Ubuntu Setup
Update your system and install required packages.

    $ sudo apt-get update
    $ sudo apt-get -y upgrade
    $ sudo apt-get -y install autoconf build-essential git-core libboost-all-dev libssl-dev libtool pkg-config python-dev

Update sudoers file to allow normal user to execute certain privileged commands without password prompt.

    $ sudo visudo

Add the following lines at the end of the file to allow normal user to restart the system and to configure bandwidth limit for the system. Note that tc and iptables are only available on Linux.

    bitnodes ALL=NOPASSWD: /sbin/shutdown
    bitnodes ALL=NOPASSWD: /sbin/tc
    bitnodes ALL=NOPASSWD: /sbin/iptables

Build and install Bitcoin client from source.

    $ cd
    $ git clone https://github.com/bitcoin/bitcoin.git
    $ cd bitcoin
    $ git checkout v0.10.1
    $ make clean
    $ ./autogen.sh
    $ ./configure --without-gui --without-miniupnpc --disable-wallet
    $ make
    $ make check
    $ sudo make install

The administration page and the public status page for your Bitnodes Hardware are powered by the same [Django](https://www.djangoproject.com/) project installed inside a virtualenv environment. Install virtualenv and pip to manage Python packages inside the virtualenv environment.

    $ sudo apt-get -y install python-pip
    $ sudo pip install --upgrade pip
    $ sudo pip install --upgrade virtualenv
    $ sudo pip install virtualenvwrapper

    $ vi ~/.profile

Add the following lines at the end of the file.

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

Install Nginx for use as the front-end web server for the Django project.

    $ sudo apt-get -y install nginx

Install Supervisor to manage processes for the Django project.

    $ sudo apt-get -y install supervisor

### Django Project Installation
The project is currently supported on Linux and Mac OS X with Python 2.7.x. Clone the project into the home directory and run `setup.sh` to bootstrap the project.

    $ cd
    $ git clone git@github.com:ayeowch/hardware.git
    $ cd hardware
    $ source ~/.profile
    $ mkvirtualenv -a "$PWD" hardware
    $ ./setup.sh

Register the project's supervisor with system's supervisor.

    $ cd /etc/supervisor/conf.d
    $ sudo ln -s /home/bitnodes/hardware/supervisor.conf hardware.conf
    $ sudo supervisorctl reread
    $ sudo supervisorctl update

Register the project with Nginx so that you can access the administration page from `http://LAN_IP_ADDRESS:8080` and the public status page from `http://LAN_IP_ADDRESS`. Access to the administration page is limited to localhost and private networks only.

    $ cd /etc/nginx/sites-enabled
    $ sudo rm default
    $ sudo ln -s /home/bitnodes/hardware/nginx.conf hardware.conf
    $ sudo service nginx reload

### Django Project Development
If you are not already in the project's virtualenv environment, execute the following command before executing any of the commands shown in this section.

    $ workon hardware

Execute the following command to access the project's shell.

    $ ./manage.py shell

Run tests.

    $ ./manage.py test

Use supervisor to start all the necessary processes. The administration page is available at http://localhost:8000 and the public status page is available at http://localhost:9000.

    $ ./manage.py supervisor

To start or stop Bitcoin client manually using supervisor. The project expects the executable to exist at `/usr/local/bin/bitcoind`.

    $ ./manage.py supervisor start hardware-bitcoind
    $ ./manage.py supervisor stop hardware-bitcoind

Execute the following command to run the website locally with the administration page enabled at http://localhost:8000.

    $ NETWORK=private ./manage.py runserver

Execute the following command to run the website locally with the public status page enabled at http://localhost:8000.

    $ ./manage.py runserver

In order to run the project in debug mode, i.e. `settings.DEBUG=True`, bootstrap the project using the following command.

    $ ./setup.sh -d

To start celery without using supervisor.

    $ celery worker -A hardware -B --loglevel=INFO

Execute the following command to monitor all log files written by the project in production mode.

    $ tail -f *.log /tmp/*.log

### Rebuild System
WARNING: THIS WILL REMOVE THE OPERATING SYSTEM, ALL APPLICATIONS AND THEIR ASSOCIATED DATA ON THE PRIMARY DISK (eMMC) OF YOUR BITNODES HARDWARE. YOU SHOULD ONLY NEED TO REBUILD YOUR SYSTEM IF IT IS NO LONGER BOOTING UP OR YOU HAVE FORGOTTEN THE PASSWORD TO ACCESS YOUR BITNODES HARDWARE.

If you wish to rebuild the system for your Bitnodes Hardware, you will need a Linux or Mac OS X host system and a Micro SD card reader to write a new image into the eMMC.

Detach the eMMC from the back of the main board of your Bitnodes Hardware. Attach the eMMC to the eMMC adapter and plug in the adapter into your Micro SD card reader. Plug in the Micro SD card reader into a USB port on your host system. The boot volume on the eMMC should now be mounted on your host system. Confirm this by checking the output of `df` command on your host system.

    $ df -h

Unmount the boot volume as shown in the output of the `df` command, e.g. /dev/disk2s1, and flash the [Bitnodes Hardware image](https://getaddr.bitnodes.io/hardware/) into the entire disk of the eMMC, e.g. /dev/rdisk2.

    $ sudo diskutil unmount /dev/disk2s1
    $ sudo dd if=bitnodes-hardware-2015-04-27.img of=/dev/rdisk2 bs=1m
    $ sync

A new boot volume on the eMMC will be mounted on your host system after the steps above. Eject the eMMC.

    $ sudo diskutil eject /dev/rdisk2

Attach the eMMC to the back of the main board of your Bitnodes Hardware and power it up.
