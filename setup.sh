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

Installs the required Python packages into current virtualenv environment and
initializes a new database to bootstrap the project.

Usage: $0 [-h] [-d]

-h
    Print usage.

-d
    Setup the project in debug mode, i.e. settings.DEBUG=True

EOF
}

debug=0

while getopts ":d" opt
do
    case "$opt" in
        h)
            usage
            exit 0
            ;;
        d)
            debug=1
            ;;
        ?)
            usage >& 2
            exit 1
            ;;
    esac
done

find . -name '*.pyc' -exec rm -vf '{}' \; -print

if [ ${debug} -eq 0 ]
then
    /usr/bin/pkill -f lcd.py
    echo "Stopping project's supervisor. This can take a few minutes."
    echo "Ignore ImportError when setup.sh is executed for the first time."
    ./manage.py supervisor stop all
    dropdb --echo bitnodes
    createdb --echo bitnodes
fi

rm -vf *.log *.db db.sqlite3 .secret_key .debug

if [ ${debug} -eq 1 ]
then
    touch .debug
fi

# Required to build Bitcoin Core >= v0.12.0
sudo apt-get install libevent-dev

# Update project
git checkout master && git pull

pip install --upgrade pip
pip install --upgrade -r requirements.txt -e .

./manage.py migrate

# Install default site admin user
./manage.py loaddata default.json

# Create default cache table
./manage.py createcachetable default_cache

# Copy all static files to be served directly by Nginx
./manage.py collectstatic --noinput --clear

# Create a new bitcoin.conf with random RPC username and password
rm -vf .bitcoin/bitcoin.conf
if [ ${debug} -eq 0 ]
then
    rm -vf /media/data/.bitcoin/bitcoin.conf
fi
./manage.py create_bitcoin_conf

# Create a new nginx.conf
cp nginx.conf.tmpl nginx.conf

./manage.py makemigrations
./manage.py migrate

if [ ${debug} -eq 0 ]
then
    setsid sh -c 'exec ./lcd.py <> /dev/tty1 >&0 2>&1' &
    echo "Restarting system's supervisor. This can take a few minutes."
    sudo service supervisor stop
    sudo service supervisor start
fi

echo "Setup completed!"
