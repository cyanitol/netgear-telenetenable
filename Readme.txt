telnetenable.py
Paul Gebheim
Translated from the C source available from
http://wiki.openwrt.org/oldwiki/openwrtdocs/hardware/netgear/telnetconsole


Running:
python telnetenable.py <IP> <MAC> <Username> <Password>

IP - The IP of your Netgear device, usually 192.168.1.1

MAC - The mac address should be the MAC address of the LAN port on your Netgear device, WITHOUT the ":". e.g. "00:40:5E:21:14:4E" would be written as "00405E21144E".

Username - Username for accessing the telnet console, usually 'Gearguy'

Password - Password for accessing the telnet console, usually 'Geardog'
