# Copyright (c) 2009 Paul Gebheim
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import socket
import array
from optparse import OptionParser
from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5

TELNET_PORT = 23

# The version of Blowfish supplied for the telenetenable.c implementation
# assumes Big-Endian data, but the code does nothing to convert the
# little-endian stuff it's getting on intel to Big-Endian
#
# So, since Crypto.Cipher.Blowfish seems to assume native endianness, we need
# to byteswap our buffer before and after encrypting it
#
# This helper does the byteswapping on the string buffer
def ByteSwap(data):
  a = array.array('i')
  if(a.itemsize < 4):
    a = array.array('L')
  
  if(a.itemsize != 4):
    print "Need a type that is 4 bytes on your platform so we can fix the data!"
    exit(1)

  a.fromstring(data)
  a.byteswap()
  return a.tostring()

def GeneratePayload(mac, username, password=""):
  # Pad the input correctly
  assert(len(mac) < 0x10)
  just_mac = mac.ljust(0x10, "\x00")

  assert(len(username) <= 0x10)
  just_username = username.ljust(0x10, "\x00")
  
  assert(len(password) <= 0x10)
  just_password = password.ljust(0x10, "\x00")

  cleartext = (just_mac + just_username + just_password).ljust(0x70, '\x00')
  md5_key = MD5.new(cleartext).digest()

  payload = ByteSwap((md5_key + cleartext).ljust(0x80, "\x00"))
  
  secret_key = "AMBIT_TELNET_ENABLE+" + password

  return ByteSwap(Blowfish.new(secret_key, 1).encrypt(payload))


def SendPayload(ip, payload):
  for res in socket.getaddrinfo(ip, TELNET_PORT, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP):
    af, socktype, proto, canonname, sa = res
    try:
      s = socket.socket(af, socktype, proto)
    except socket.error, msg:
      s = None
      continue

    try:
      s.connect(sa)
    except socket.error, msg:
      s.close()
      s= None
      continue
    break

  if s is None:
    print "Could not connect to '%s:%d'" % (ip, TELNET_PORT)
  else:
    s.send(payload)
    s.close()
    print "Sent telnet enable payload to '%s:%d'" % (ip, TELNET_PORT)
  
def main():
  args = sys.argv[1:]
  if len(args) < 3 or len(args) > 4:
    print "usage: python telnetenable.py <ip> <mac> <username> [<password>]"

  ip = args[0]
  mac = args[1]
  username = args[2]

  password = ""
  if len(args) == 4:
    password = args[3]

  payload = GeneratePayload(mac, username, password)
  SendPayload(ip, payload)

main()
