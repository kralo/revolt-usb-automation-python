#!/usr/bin/python
#
# Script to control the revolt-power px-1672 outlets via usb with the provided dongle.
# usage python revolt...py <action> <id>

# based on the pyusb tutorial script

import usb.core
import usb.util
import binascii
import sys
import math

# the original software knows 3 parameters
# Bit Width 100+6*50 seems not to be used, doesn't change the message
# ID 0-65535
raw_id = 6789
raw_frame = 2  # 3-255 number of sent frames (resend)
raw_action = 00  # placeholder for action

if len(sys.argv) >= 3:  # if you provided arg, take it
    raw_id = int(sys.argv[2])

print raw_id
MSG_FRAME = hex(raw_frame).split('x')[1].ljust(2, '0')  #
# convert the id to hex but get rid of the '0x' at the beginning to be able to concatenate the message and make sure there are 4 characters (1 byte in hex)
MSG_ID = hex(raw_id).split('x')[1].ljust(4, '0')

MSG_PADDING_BYTE5 = "20"  # not relevant padding

MSG_FIN = "0000"  # unknown, not relevant

if len(sys.argv) < 2:
    raise ValueError('no action specified')

if sys.argv[1] == "on1":
    raw_action = 15
elif sys.argv[1] == "off1":
    raw_action = 14
elif sys.argv[1] == "on2":
    raw_action = 13
elif sys.argv[1] == "off2":
    raw_action = 12
elif sys.argv[1] == "on3":
    raw_action = 11
elif sys.argv[1] == "off3":
    raw_action = 10
elif sys.argv[1] == "on4":
    raw_action = 9
elif sys.argv[1] == "off4":
    raw_action = 8
elif sys.argv[1] == "on5":
    raw_action = 7
elif sys.argv[1] == "off5":
    raw_action = 6
elif sys.argv[1] == "on6":
    raw_action = 5
elif sys.argv[1] == "off6":
    raw_action = 4
elif sys.argv[1] == "on7":  # has no off7 counterpart !
    raw_action = 3
elif sys.argv[1] == "ona":
    raw_action = 2
elif sys.argv[1] == "offa":
    raw_action = 1
elif sys.argv[1] == "off8":  # has no on8 counterpart!
    raw_action = 0

else:
    raise ValueError('no known action')

MSG_ACTION = hex(raw_action).split('x')[1].ljust(2, '0')

# compute the checksum: byte01+02+03+04 mod 256 have to be 255
checksum = int(MSG_ID[:2], 16) + int(MSG_ID[2:], 16) + raw_action * 16

raw_checksum = int(math.ceil(checksum / 256.0) * 256) - checksum - 1
MSG_CHECKSUM = hex(raw_checksum).split('x')[1].ljust(2, '0')

message = MSG_ID + MSG_ACTION + MSG_CHECKSUM + MSG_PADDING_BYTE5 + MSG_FRAME + MSG_FIN
print "sent " + message

# find our device
dev = usb.core.find(idVendor=0xffff, idProduct=0x1122)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# was it found?
if dev is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
interface_number = cfg[(0, 0)].bInterfaceNumber
usb.util.claim_interface(dev, interface_number)
alternate_setting = usb.control.get_interface(dev, interface_number)
intf = usb.util.find_descriptor(
    cfg, bInterfaceNumber=interface_number,
    bAlternateSetting=alternate_setting
)

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match=(lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
)

assert ep is not None

# write the data
ep.write(binascii.a2b_hex(message))
usb.util.release_interface(dev, interface_number)
