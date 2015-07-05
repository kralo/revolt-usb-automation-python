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

def main():
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

    action_values = {
        "on1": 15,
        "off1": 14,
        "on2": 13,
        "off2": 12,
        "on3": 11,
        "off3": 10,
        "on4": 9,
        "off4": 8,
        "on5": 7,
        "off5": 6,
        "on6": 5,
        "off6": 4,
        "on7": 3,  # has no off7 counterpart!
        "ona": 2,
        "offa": 1,
        "off8": 0,  # has no on8 counterpart!
    }

    if sys.argv[1] in action_values:
        raw_action = action_values[sys.argv[1]]

    else:
        raise ValueError('unknown action: %s' % sys.argv[1])

    MSG_ACTION = hex(raw_action).split('x')[1].ljust(2, '0')

    # compute the checksum: byte01+02+03+04 mod 256 have to be 255
    checksum = int(MSG_ID[:2], 16) + int(MSG_ID[2:], 16) + raw_action * 16

    raw_checksum = int(math.ceil(checksum / 256.0) * 256) - checksum - 1
    MSG_CHECKSUM = hex(raw_checksum).split('x')[1].ljust(2, '0')

    message = MSG_ID + MSG_ACTION + MSG_CHECKSUM + MSG_PADDING_BYTE5 + MSG_FRAME + MSG_FIN
    print "sent " + message

    # find our device
    device = usb.core.find(idVendor=0xffff, idProduct=0x1122)

    # was it found?
    if device is None:
        raise ValueError('Device not found')

    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    device.set_configuration()

    # get an endpoint instance
    device_configuration = device.get_active_configuration()
    interface_number = device_configuration[(0, 0)].bInterfaceNumber
    usb.util.claim_interface(device, interface_number)
    alternate_setting = usb.control.get_interface(device, interface_number)
    interface = usb.util.find_descriptor(
        device_configuration, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting
    )

    endpoint = usb.util.find_descriptor(
        interface,
        # match the first OUT endpoint
        custom_match=(lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
    )

    assert endpoint is not None

    # write the data
    endpoint.write(binascii.a2b_hex(message))
    usb.util.release_interface(device, interface_number)

if __name__ == "__main__":
    main()
