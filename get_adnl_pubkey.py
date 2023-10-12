#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import json
import socket
import struct
import base64
from nacl.signing import SigningKey

def int2ip(dec):
	return socket.inet_ntoa(struct.pack("!i", dec))
#end define

config_path = "/var/ton-work/db/config.json"
with open(config_path, 'rt') as file:
	text = file.read()
	vconfig = json.loads(text)
#end with

dht_id = vconfig["dht"][0]["id"]
dht_id_hex = base64.b64decode(dht_id).hex().upper()


key_path = f"/var/ton-work/db/keyring/{dht_id_hex}"
with open(key_path, 'rb') as file:
	data = file.read()
	private_key = data[4:]
#end with

signing_key = SigningKey(private_key)
public_key_bytes = signing_key.verify_key.encode()
public_key = base64.b64encode(public_key_bytes).decode()

data = dict()
data["ip"] = int2ip(vconfig["addrs"][0]["ip"])
data["port"] = vconfig["addrs"][0]["port"]
data["pubkey"] = public_key
result = json.dumps(data, indent=4)

print("adnl_over_udp settings:")
print(result)
