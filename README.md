revolt-usb-automation-python
============================

Python example to control wireless 433MHz power outlets

The Pearl / revolt PX-1672 and PX-1674 is a package with a power outlet that be
controlled remotely via 433 MHz RF and a USB dongle.
Pearl only supplies a Windows-only GUI application `Huading RF.exe` (About
Dialog: First RF V1.0 Hanson Han) to control the outlets, but their USB
protocol has been reverse-engineered.

The dongle has the USB ID ffff:1122 and the program talks to it via USB urb out
packets. Windows recognizes the dongle as an HID device.

The protocol
============

between the supplied exe and the USB dongle can be sniffed with Wireshark. You
will find payloads like this: `1A85F070200A0018`.
The program also has 3 parameters (find them in the settings box):
* Bit Width 100-400 (in 50 increments): seems to be not relevant to generation
  of the control code.
* Frame 3-255: the number of times the frame is resent. The more often, the
  more likely the outlet will receive the message, but the USB dongle will be
  working longer on it.
* ID 0-65535: To control separate sets of power outlets (as the program only
  supports switching 4 outlets per ID).

Then you have the "switch number" (1-4, all) and action (on, off). Observations
in the spreadsheet.
Take the first example:
Bit width = 100, Frame = 10, ID = 6789

* The first two byte are the ID in hex: `1A85`.
* action byte: 1_ON is `F0`.
* checksum: sum(byte 1 + byte 2 + byte 3 + byte 4) mod 256 has to be 255
* one byte of useless padding (value not important; `20` in this example)
* frame resend count in hex: `0A`
* two more bytes that seem to have no function and change every time you
  restart the program. here `0018`

Assemble and you get the above code `1A85_F0_70_20_0A_0018`.

Demo implementation
===================

is based on pyusb. Make sure you have installed pyusb first, tested with
version pyusb-1.0.0b1.
With this command-line script you can control your outlets (Funksteckdose) by
command line, scripts, etc. -- use your fantasy!

Execute with `python revoltoutlets.py offa` to switch off all outlets.
Possible commands are `on<id>`, `off<id>`, `ona`, and `offa`.
The script accepts multiple commands at once, but they might not all be sent
reliably due to delays in the transmitter. Use at your own risk or only send
one command at a time if you want to be sure.

Additional Credits
==================
go to Ralph Babel, http://babel.de, for finding the checksum and the
resend-frame behavior. Thanks!

lsusb -vv output for the USB dongle
===================================


```
Bus 001 Device 008: ID ffff:1122
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               1.10
  bDeviceClass            0 (Defined at Interface level)
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0         8
  idVendor           0xffff 
  idProduct          0x1122 
  bcdDevice            0.01
  iManufacturer           1 HANSON
  iProduct                2 USB Remote
  iSerial                 0 
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength           34
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0 No Subclass
      bInterfaceProtocol      0 None
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.00
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      53
          Report Descriptor: (length is 53)
            Item(Global): Usage Page, data= [ 0xff ] 255
                            Vendor Specific
            Item(Local ): Usage, data= [ 0xff ] 255
                            (null)
            Item(Main  ): Collection, data= [ 0x01 ] 1
                            Application
            Item(Global): Usage Page, data= [ 0x01 ] 1
                            Generic Desktop Controls
            Item(Local ): Usage Minimum, data= [ 0x00 ] 0
                            Undefined
            Item(Local ): Usage Maximum, data= [ 0xff ] 255
                            (null)
            Item(Global): Logical Minimum, data= [ 0x00 ] 0
            Item(Global): Logical Maximum, data= [ 0xff ] 255
            Item(Global): Report Size, data= [ 0x08 ] 8
            Item(Global): Report Count, data= [ 0x08 ] 8
            Item(Main  ): Input, data= [ 0x02 ] 2
                            Data Variable Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Global): Usage Page, data= [ 0x02 ] 2
                            Simulation Controls
            Item(Local ): Usage Minimum, data= [ 0x00 ] 0
                            Undefined
            Item(Local ): Usage Maximum, data= [ 0xff ] 255
                            (null)
            Item(Global): Logical Minimum, data= [ 0x00 ] 0
            Item(Global): Logical Maximum, data= [ 0xff ] 255
            Item(Global): Report Count, data= [ 0x08 ] 8
            Item(Global): Report Size, data= [ 0x08 ] 8
            Item(Main  ): Output, data= [ 0x02 ] 2
                            Data Variable Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Global): Usage Page, data= [ 0x0c ] 12
                            Consumer
            Item(Local ): Usage, data= [ 0x00 ] 0
                            Unassigned
            Item(Global): Logical Minimum, data= [ 0x80 ] 128
            Item(Global): Logical Maximum, data= [ 0x7f ] 127
            Item(Global): Report Size, data= [ 0x08 ] 8
            Item(Global): Report Count, data= [ 0x08 ] 8
            Item(Main  ): Feature, data= [ 0x02 ] 2
                            Data Variable Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Main  ): End Collection, data=none
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x02  EP 2 OUT
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval              10
Device Status:     0x0000
  (Bus Powered)
```
