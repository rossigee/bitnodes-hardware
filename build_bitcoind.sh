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

Checkout and build Bitcoin client from github.com/bitcoin/bitcoin using the
specified tag.

Usage: $0 [-h] [-s <src>] [-t <tag>]

-h
    Print usage.

-s <src>
    Existing source directory from github.com/bitcoin/bitcoin

-t <tag>
    Git tag to checkout.

EOF
}

while getopts ":s:t:" opt
do
    case "$opt" in
        h)
            usage
            exit 0
            ;;
        s)
            src=${OPTARG}
            ;;
        t)
            tag=${OPTARG}
            ;;
        ?)
            usage >& 2
            exit 1
            ;;
    esac
done

if [ -z ${src} ] || [ -z ${tag} ]
then
    usage
    exit 1
fi

echo "src = ${src}"
echo "tag = ${tag}"

cd ${src}
git fetch
git checkout ${tag}

make clean && \
    ./configure --without-gui --without-miniupnpc --disable-wallet && \
    make && \
    exit 0

exit 1
