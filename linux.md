# Linux Specific Instructions

# udev

In order to flash the board using WebUSB on Linux, udev rules will need to be configured. Without doing this you will get an "Access denied" error.

1. Create a file named `/etc/udev/rules.d/60-rp2040.rules` as root or with sudo, which contains the following:
```
SUBSYSTEMS=="usb", ATTRS{idVendor}=="2e8a", MODE:="0666"
```
2. Run `sudo udevadm trigger`
3. Run `sudo udevadm control --reload-rules`
4. If the board was plug in previously, unplug and plug it back in.
