# gqrx2rig - modification for one way control (gqrx->rig), it changes frequency + mode
#
# for example for yaesu ft817 run rigctld as
# rigctld -m 120 -r /dev/ttyRADIO1 -P RTS -p /dev/ttyRADIO1 -t 4532 --set-conf=serial_handshake=None,dtr_state=Unset,rts_state=Unset,stop_bits=2,serial_speed=9600 -vvv
# then run gqrx and eanble remote control
# then run python ./gqrx2rig.py
#
##################################
# gqrx-hamlib - a gqrx to Hamlib interface to keep frequency
# between gqrx and a radio in sync when using gqrx as a panadaptor
# using Hamlib to control the radio
#
# The Hamlib daemon (rigctld) must be running, gqrx started with
# the 'Remote Control via TCP' button clicked and
# comms to the radio working otherwise an error will occur when
# starting this program. Ports used are the defaults for gqrx and Hamlib.
#
# Return codes from gqrx and Hamlib are printed to stderr
#
# This program is written in Python 2.7
# To run it type the following on the command line in the directory where
# you have placed this file:
#   python ./gqrx-hamlib.py
#
# Copyright 2017 Simon Kennedy, G0FCU, g0fcu at g0fcu.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import sys
import time

TCP_IP = "localhost"
RIG_PORT = 4532
GQRX_PORT = 7356

FREQ = "f\n"
MODE = "m\n"

forever = 1
rig_freq = 0
gqrx_freq = 0
old_rig_freq = 0
old_gqrx_freq = 0
old_gqrx_mode = 0

def getfreq(PORT):
    sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)

    sock.sendall(FREQ)
    # Look for the response
    amount_received = 0
    amount_expected = 8 #len(message)
    while amount_received < amount_expected:
        datafreq = sock.recv(16)
        amount_received += len(datafreq)

    if (PORT == RIG_PORT):
        port="rig "
    else:
        port="gqrx"

    print >>sys.stderr, "get", port, "freq:", datafreq.rstrip()

    sock.close()
    return datafreq

def getmode(PORT):
    sock = socket.socket(socket.AF_INET,
                     socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)

    sock.sendall(MODE)
        # Look for the response
    amount_received = 0
    amount_expected = 8 #len(message)
    while amount_received < amount_expected:
        datamode = sock.recv(16)
        amount_received += len(datamode)

    if (PORT == RIG_PORT):
        port="rig "
    else:
        port="gqrx"

    print >>sys.stderr, "get", port, "mode:", datamode.splitlines()

    sock.close()
    return datamode


def setfreq(PORT, freq):
    sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_STREAM) 
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall("F " + freq + '\n')
    # Look for the response
    amount_received = 0
    amount_expected = 7 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)

    if (PORT == RIG_PORT):
        port="rig "
    else:
        port="gqrx"

    print >>sys.stderr, "set", port, "freq:", freq.rstrip()

    sock.close()
    return data

def setmode(PORT, mode):
    sock = socket.socket(socket.AF_INET,
                     socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = (TCP_IP, PORT)
    sock.connect(server_address)
    sock.sendall("M " + mode + '\n')
    # Look for the response
    amount_received = 0
    amount_expected = 7 #len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
    
    if (PORT == RIG_PORT):
        port="rig "
    else:
        port="gqrx"
    
    print >>sys.stderr, "set", port, "mode:", mode.rstrip()
    
    sock.close()
    return data


old_gqrx_freq = getfreq(GQRX_PORT)
old_gqrx_mode = getmode(GQRX_PORT)

while forever:
    time.sleep(3)
    
    gqrx_freq = getfreq(GQRX_PORT)
    gqrx_mode = getmode(GQRX_PORT)

    # change rig frequency only if gqrx frequency changed more than delta (200Hz for example)

    if abs(int(gqrx_freq) - int(old_gqrx_freq)) >= 200:

        rc = setfreq(RIG_PORT, gqrx_freq)
        print >>sys.stderr, 'Return Code from Hamlib: "%s"' % rc.rstrip()

        old_gqrx_freq = gqrx_freq

    # change rig mode if gqrx changed mode

    if (gqrx_mode != old_gqrx_mode):

        if ("AM" in gqrx_mode):
            temp_mode="AM"
        if ("WFM" in gqrx_mode):
            temp_mode="WFM"
        elif ("FM" in gqrx_mode):
            temp_mode="FM"
        if ("USB" in gqrx_mode):
            temp_mode="USB"
        if ("CW" in gqrx_mode):
            temp_mode="CW"

        temp_mode=temp_mode + " 0"
        rc = setmode(RIG_PORT, temp_mode)
        print >>sys.stderr, 'Return Code from Hamlib: "%s"' % rc.rstrip()

        old_gqrx_mode = gqrx_mode


