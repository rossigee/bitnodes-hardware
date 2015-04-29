#!/bin/bash
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
usage()
{
    cat <<EOF

Set uplink and downlink bandwidth limit for a network interface. This script is
supported only on Linux as it uses tc and iptables.

Usage: $0 [-h] [-i <iface>] [-l <linkspeed>] [-u <up>] [-d <down] [-s]

-h
    Print usage.

-i <iface>
    Name of network interface, e.g. eth0

-l <linkspeed>
    Provisioned link speed in kbps.

-u <up>
    Uplink bandwidth limit in kbps. Set to 0 to remove limit (default).

-d <down>
    Downlink bandwidth limit in kbps. Set to 0 to remove limit (default).

-s
    Show status and exit.

EOF
}

requirement()
{
    cat <<EOF

tc and iptables are required to run this script.

EOF
}

status=0

while getopts ":i:l:u:d:s" opt
do
    case "$opt" in
        h)
            usage
            exit 0
            ;;
        i)
            iface=${OPTARG}
            ;;
        l)
            linkspeed=${OPTARG}
            ;;
        u)
            up=${OPTARG}
            ;;
        d)
            down=${OPTARG}
            ;;
        s)
            status=1
            ;;
        ?)
            usage >& 2
            exit 1
            ;;
    esac
done

if [ -z ${iface} ]
then
    usage
    exit 1
fi

echo "iface = ${iface}"

tc=$(which tc)
iptables=$(which iptables)
if [ -z "${tc}" ] || [ -z "${iptables}" ]
then
    requirement
    exit 1
fi

# Show status and exit
if [ ${status} -eq 1 ]
then
    sudo ${tc} -s qdisc ls dev ${iface}
    exit 0;
fi

# Remove bandwidth limit by default
if [ -z ${up} ]
then
    up=0
fi
echo "up = ${up}kbps"

if [ -z ${down} ]
then
    down=0
fi
echo "down = ${down}kbps"

# Set default link speed to 100Mbps
if [ -z ${linkspeed} ] || [ ${linkspeed} -eq 0 ]
then
    linkspeed=100000
fi
echo "linkspeed = ${linkspeed}"

# Delete existing qdiscs to remove bandwidth limit
sudo ${tc} qdisc del dev ${iface} root
sudo ${tc} qdisc del dev ${iface} ingress

# Delete existing iptables rules
sudo ${iptables} -t mangle -F
sudo ${iptables} -t mangle -X

sleep 1

# No further setup is required for unlimited bandwidth
if [ ${up} -eq 0 ] && [ ${down} -eq 0 ]
then
    exit 0
fi

### Uplink ####################################################################

# HTB (Hierarchical Token Bucket) root qdisc, default traffic to 1:10
sudo ${tc} qdisc add dev ${iface} root handle 1: htb default 10

# Shape everything at reduced link speed
sudo ${tc} class add dev ${iface} parent 1: classid 1:1 htb rate \
    ${linkspeed}kbit ceil ${linkspeed}kbit

# High priority class 1:10
sudo ${tc} class add dev ${iface} parent 1:1 classid 1:10 htb rate \
    ${linkspeed}kbit ceil ${linkspeed}kbit prio 1

# Bandwidth limited class 1:20
sudo ${tc} class add dev ${iface} parent 1:1 classid 1:20 htb rate \
    ${up}kbit ceil ${up}kbit prio 2

# Packets with mark 1 in class 1:10
sudo ${tc} filter add dev ${iface} parent 1: protocol ip prio 1 \
    handle 1 fw classid 1:10

# Packets with mark 2 in class 1:20
sudo ${tc} filter add dev ${iface} parent 1: protocol ip prio 2 \
    handle 2 fw classid 1:20

### Downlink ##################################################################

if [ ${down} -gt 0 ]
then
    # Attach ingress policer; ffff: is reserved for ingress qdisc
    sudo ${tc} qdisc add dev ${iface} handle ffff: ingress

    # Filter everything (0.0.0.0/0) to policer that allows burst of 10 full
    # packets with MTU of 1500 bytes or drop if too fast
    sudo ${tc} filter add dev ${iface} parent ffff: protocol ip prio 50 u32 \
        match ip src 0.0.0.0/0 \
        police rate ${down}kbit burst 15k drop \
        flowid :1
fi

### Marker ####################################################################

# Mark incoming Bitcoin client packets to go to class 1:20
sudo ${iptables} -t mangle -A OUTPUT \
    -p tcp -m tcp --dport 8333 -j MARK --set-mark 0x2

# Mark outgoing Bitcoin client packets to go to class 1:20
sudo ${iptables} -t mangle -A OUTPUT \
    -p tcp -m tcp --sport 8333 -j MARK --set-mark 0x2

### Status ####################################################################

# Show status
sudo ${tc} -s -d -p qdisc show dev ${iface}
