import os
import json
import base64
import subprocess


class bcolors:
	'''This class is designed to display text in color format'''
	red = "\033[31m"
	green = "\033[32m"
	yellow = "\033[33m"
	blue = "\033[34m"
	magenta = "\033[35m"
	cyan = "\033[36m"
	endc = "\033[0m"
	bold = "\033[1m"
	underline = "\033[4m"
	default = "\033[39m"

	DEBUG = magenta
	INFO = blue
	OKGREEN = green
	WARNING = yellow
	ERROR = red
	ENDC = endc
	BOLD = bold
	UNDERLINE = underline

	def get_args(*args):
		text = ""
		for item in args:
			if item is None:
				continue
			text += str(item)
		return text
	#end define

	def magenta_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.magenta + text + bcolors.endc
		return text
	#end define

	def blue_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.blue + text + bcolors.endc
		return text
	#end define

	def green_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.green + text + bcolors.endc
		return text
	#end define

	def yellow_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.yellow + text + bcolors.endc
		return text
	#end define

	def red_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.red + text + bcolors.endc
		return text
	#end define

	def bold_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.bold + text + bcolors.endc
		return text
	#end define

	def underline_text(*args):
		text = bcolors.get_args(*args)
		text = bcolors.underline + text + bcolors.endc
		return text
	#end define

	colors = {"red": red, "green": green, "yellow": yellow, "blue": blue, "magenta": magenta, "cyan": cyan,
			  "endc": endc, "bold": bold, "underline": underline}
#end class

class Dict(dict):
	def __init__(self, *args, **kwargs):
		for item in args:
			self._parse_dict(item)
		self._parse_dict(kwargs)
	#end define

	def _parse_dict(self, d):
		for key, value in d.items():
			if type(value) in [dict, Dict]:
				value = Dict(value)
			if type(value) == list:
				value = self._parse_list(value)
			self[key] = value
	#end define

	def _parse_list(self, lst):
		result = list()
		for value in lst:
			if type(value) in [dict, Dict]:
				value = Dict(value)
			result.append(value)
		return result
	#end define

	def __setattr__(self, key, value):
		self[key] = value
	#end define

	def __getattr__(self, key):
		return self.get(key)
	#end define
#end class

def print_table(arr):
	buff = dict()
	for i in range(len(arr[0])):
		buff[i] = list()
		for item in arr:
			buff[i].append(len(str(item[i])))
	for item in arr:
		for i in range(len(arr[0])):
			index = max(buff[i]) + 2
			ptext = str(item[i]).ljust(index)
			if item == arr[0]:
				ptext = bcolors.blue_text(ptext)
				ptext = bcolors.bold_text(ptext)
			print(ptext, end='')
		print()
#end define



def get_validator_console_args():
	user = os.getenv("USER")
	file_path = f"/home/{user}/.local/share/mytoncore/mytoncore.db"
	if user == "root":
		file_path = f"/usr/local/bin/mytoncore/mytoncore.db"
	with open(file_path, 'rt') as file:
		mconfig_text = file.read()
	#end with

	mconfig = Dict(json.loads(mconfig_text))
	validator_console = f"/usr/bin/ton/validator-engine-console/validator-engine-console -k /var/ton-work/keys/client -p /var/ton-work/keys/server.pub -a {mconfig.validatorConsole.addr}"
	validator_console_args = validator_console.split(' ')
	return validator_console_args
#end define

def get_stats():
	save_peers = dict()

	validator_console_args = get_validator_console_args()
	adnl_cmd_args = validator_console_args + ["--cmd", "get-adnl-stats-json /tmp/adnl_stats.json all"]
	overlays_cmd_args = validator_console_args + ["--cmd", "get-overlays-stats-json /tmp/overlays_stats.json"]
	process_1 = subprocess.run(adnl_cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process_2 = subprocess.run(overlays_cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if process_1.returncode != 0:
		raise Exception(process_1.stderr)
	if process_2.returncode != 0:
		raise Exception(process_2.stderr)
	#end if

	with open("/tmp/adnl_stats.json", 'rt') as file:
		adnl_stats_text = file.read()
	with open("/tmp/overlays_stats.json", 'rt') as file:
		overlay_stats_text = file.read()
	#end with

	my_adnls = list()
	adnl_stats = Dict(json.loads(adnl_stats_text))
	overlay_stats = json.loads(overlay_stats_text)
	for local_id in adnl_stats.local_ids:
		my_adnls.append(local_id.short_id)
		peers = convert_peers(local_id.peers)
		for peer in peers:
			save_peers[peer.peer_id] = peer
	#end for

	with open("/tmp/my_adnls.json", 'wt') as file:
		file.write(json.dumps(my_adnls, indent=2))
	with open("/tmp/save_peers.json", 'wt') as file:
		file.write(json.dumps(save_peers, indent=2))
	#end with

	overlay_stats_new = list()
	for overlay in overlay_stats:
		overlay_stats_new.append(Dict(overlay))
	#end for

	return adnl_stats, overlay_stats_new, save_peers, my_adnls
#end define

def convert_peers(peers):
	for peer in peers:
		peer.channel_status = int(peer.channel_status)
		peer.packets_recent.in_packets = int(peer.packets_recent.in_packets)
		peer.packets_recent.in_packets_channel = int(peer.packets_recent.in_packets_channel)
		peer.packets_recent.out_packets = int(peer.packets_recent.out_packets)
		peer.packets_recent.out_packets_channel = int(peer.packets_recent.out_packets_channel)
	return peers
#end define

def print_peers(peers):
	peers = convert_peers(peers)
	sorted_peers = sorted(peers, key=lambda peer: peer.packets_recent.in_packets)
	table = [["addr", "channel_status", "in_packets", "in_packets_channel", "out_packets", "out_packets_channel"]]
	minimum_packets = 10
	for peer in sorted_peers:
		if (peer.packets_recent.in_packets < minimum_packets and
			peer.packets_recent.in_packets_channel < minimum_packets and
			peer.packets_recent.out_packets < minimum_packets and
			peer.packets_recent.out_packets_channel < minimum_packets):
			continue
		table += [[peer.ip_str, 
			peer.channel_status, 
			peer.packets_recent.in_packets, 
			peer.packets_recent.in_packets_channel, 
			peer.packets_recent.out_packets, 
			peer.packets_recent.out_packets_channel]]
	print_table(table)
#end define

def get_peer_by_adnl(adnl_hex, my_adnls):
	adnl_bytes = bytes.fromhex(adnl_hex)
	adnl_b64 = base64.b64encode(adnl_bytes).decode("utf-8")
	for peer_id, peer in save_peers.items():
		if peer_id == adnl_b64:
			return peer
		elif adnl_b64 in my_adnls:
			return Dict(ip_str="myself")
	#raise Exception(f"get_peer_by_adnl error: peer not found: {adnl_hex} -> {adnl_b64}")
	print(f"get_peer_by_adnl error: peer not found: {adnl_hex} -> {adnl_b64}")
#end define

def get_overlay_peers(overlay, save_peers, my_adnls):
	for node in overlay.nodes:
		node.peer = get_peer_by_adnl(node.adnl_id, my_adnls)
	#end for
#end define

def get_overlay_name(overlay):
	if overlay.scope.type == "shard":
		return f"{overlay.scope.type}.{overlay.scope.workchain_id}.{overlay.scope.shard_id}"
	elif overlay.scope.type == "custom-overlay":
		return f"{overlay.scope.type}.{overlay.scope.name}"
	else:
		return f"{overlay.scope.type}"
#end define

def print_nodes_old(nodes):
	table = [["adnl_id", "throughput.in_pckts_sec", "throughput.out_pckts_sec", "throughput_responses.in_pckts_sec", "throughput_responses.out_pckts_sec"]]
	for node in nodes:
		if (node.throughput.in_pckts_sec == 0 and
			node.throughput.out_pckts_sec == 0 and
			node.throughput_responses.in_pckts_sec == 0 and
			node.throughput_responses.out_pckts_sec == 0):
			continue
		table += [[node.adnl_id, 
			node.throughput.in_pckts_sec, 
			node.throughput.out_pckts_sec, 
			node.throughput_responses.in_pckts_sec,
			node.throughput_responses.out_pckts_sec]]
	print_table(table)
#end define

def short_adnl(adnl):
	return adnl[:6] + "..." + adnl[58:]
#end define

def print_nodes(nodes):
	table = [["addr", "channel_status", "in_packets", "in_packets_channel", "out_packets", "out_packets_channel"]]
	for node in nodes:
		if node.peer == None:
			table += [[short_adnl(node.adnl_id), None, None, None, None, None]]
			continue
		if node.peer.ip_str == "myself":
			table += [[node.peer.ip_str, "---", "---", "---", "---", "---"]]
			continue
		table += [[node.peer.ip_str, 
			node.peer.channel_status, 
			node.peer.packets_recent.in_packets, 
			node.peer.packets_recent.in_packets_channel, 
			node.peer.packets_recent.out_packets, 
			node.peer.packets_recent.out_packets_channel]]
	print_table(table)
#end define

def print_adnl_peers(adnl_stats):
	for local_id in adnl_stats.local_ids:
		if len(local_id.peers) == 0:
			continue
		print(f"{bcolors.green} ADNL: {local_id.short_id} {bcolors.endc}")
		print_peers(local_id.peers)
	#end for
#end define

def print_overlay_peers(overlay_stats, save_peers, my_adnls):
	for overlay in overlay_stats:
		get_overlay_peers(overlay, save_peers, my_adnls)
		overlay_name = get_overlay_name(overlay)
		print(f"{bcolors.green} OVERLAY: {overlay.overlay_id}, {overlay_name} {bcolors.endc}")
		print_nodes(overlay.nodes)
	#end for
#end define

def print_peers_stats(adnl_stats):
	print(f"{bcolors.green}ADNL's:{bcolors.endc}")
	for local_id in adnl_stats.local_ids:
		print(f"{local_id.short_id} -> {len(local_id.peers)} peers")
	print()
#end define

def print_overlay_stats(overlay_stats):
	print(f"{bcolors.green}Overlays:{bcolors.endc}")
	for overlay in overlay_stats:
		overlay_name = get_overlay_name(overlay)
		print(f"{overlay.overlay_id} -> {overlay_name}")
	print()
#end define


###
### Start program
###



adnl_stats, overlay_stats, save_peers, my_adnls = get_stats()
print_peers_stats(adnl_stats)
print_overlay_stats(overlay_stats)
#print_adnl_peers(adnl_stats)
print_overlay_peers(overlay_stats, save_peers, my_adnls)

