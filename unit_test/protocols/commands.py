import simplejson

from stats.protocol import stat_protocol

class protocol_commands(object):
	commands = {
		'connected': '{"cmd": "connected", "args": "null"}',
		'auth': '{"cmd": "auth", "args": "pouetpouet", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'create': '{"cmd": "create", "args": [ "protocol", "password" ], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'join': '{"cmd": "join", "args": [ "protocol", "password" ], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanMasterPwd': '{"cmd": "chanMasterPwd", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'chanAuth': '{"cmd": "chanAuth", "args": "passwordChan", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'nick': '{"cmd": "nick", "args": "protocolMaster", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'forward': '{"cmd": "forward", "args": "messageToForward", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'list': '{"cmd": "list", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'message': '{"cmd": "message", "args": ["message", [ "unknown" ]], "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'history': '{"cmd": "history", "args": "null", "uid": "$uid", "channel": "protocol", "app": "protocol"}',
		'setStatus': '{"cmd": "setStatus", "args": "protocolMasterNewStatus", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'getStatus': '{"cmd": "getStatus", "args": "null", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'timeConnect': '{"cmd": "timeConnect", "args": "null", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'part': '{"cmd": "part", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}',
		'remove': '{"cmd": "remove", "args": "protocol", "app": "protocol", "channel": "protocol", "uid": "$uid"}'
	}
	keys_needed = [
		'from',
		'value',
	]
	keys_default = [
		'app',
		'channel'
	]
	keys_error = [
		'message'
	]

	@staticmethod
	def test(method, client):
		client.send(protocol_commands.commands.get(method, ''))
		results = client.receive().strip(' \t\n\0').split("\n")
		for result in results:
			json = protocol_commands.check_json(method, result)
			if json is False:
				return False
			keys = protocol_commands.keys_needed
			if json['from'] == 'connected':
				client.uid = json['value']
			else:
				keys = protocol_commands.keys_needed + protocol_commands.keys_default
			if protocol_commands.check_keys(method, json, keys) is False:
				return False
		return True

	@staticmethod
	def check_json(name, json_encoded):
		try:
			json_decoded = simplejson.loads(json_encoded)
			return json_decoded
		except ValueError:
			error = '[%s] JSON malformed' % name
			error += '[%s][DEBUG] %s' % (name, json_encoded)
			stat_protocol.add(name, error)
			return False

	@staticmethod
	def check_keys(name, json, keys):
		result = True
		for k in keys:
			if json['from'] == 'status' and k == 'app':
				continue
			if json.get(k, None) is None:
				result = False
				error = '[%s] JSON key "%s" missing' % (name, k)
				error += '[%s][DEBUG] %s' % (name, str(json))
				stat_protocol.add(name, error)
		return result
