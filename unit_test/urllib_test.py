import urllib
import simplejson

host = '192.168.104.182'
port = 8081

def main():
	raw_create = urllib.urlencode({ 'json': { "cmd": "httpCreateChannel", "args": { "chan": "monchandeouf", "pwd": "testpwd", "adminPwd": "pouetpouet", "masterPwd": "testMasterPwd" }, "app": "whiteboard"} }).replace('%27', '%22')
	ressource = urllib.urlopen("http://%s:%d" % (host, port), raw_create)
	raw_response = ressource.read()
	print raw_response
	try:
		json = simplejson.loads(raw_response)
		uid = json.get('value', None)
	except ValueError:
		pass
if __name__ == '__main__':
	main()