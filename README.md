# RPiGrab

This script uses the Shodan API to search for Raspbian devices running an SSH server, and tries to SSH into them by using the default credentials `pi:raspberry`.

## Requirements
* `paramiko` (the SSH client)  
* `shodan` (the API client)
* `colorama` (the colored output module)

...which can be installed by running `pip3 install -r requirements.txt` on Linux and `python3 -m pip install -r requirements.txt` on Windows.

## Usage
```
usage: rpigrab.py [-h] [-i FILE] [-n] [-k KEY] [-l FILE] [-w FILE]
                       [-u USERNAME] [-p PASSWORD] [-d] [-s SSTRING] [-sk KEY]
                       [-c CMD] [--enum]

optional arguments:
  -h, --help            show this help message and exit
  -i FILE, --input FILE
                        List of IPs
  -n, --no-exit         Run indefinitely, restarting once the scan is finished
  -k KEY, --api-key KEY
                        Use KEY as the Shodan API key
  -l FILE, --log-paramiko FILE
                        Log Paramiko SSH's progress to FILE
  -w FILE, --workfile FILE
                        Output successful IPs to FILE
  -u USERNAME, --username USERNAME
                        Use alternate username
  -p PASSWORD, --password PASSWORD
                        Use alternate password
  -d, --debug           Show debug information
  -s SSTRING, --search-string SSTRING
                        Use SSTRING as the Shodan query string
  -sk KEY, --ssh-key KEY
                        Try auth with KEY as SSH key
  -c CMD, --command CMD
                        Run CMD after a successful connection
  --enum                Enumerate system specs
```

Additionally, the script can be edited (specifically the variable `api_key`) to not require an API key argument.

By default, the script will poll Shodan for results and write the IPs into a list, trying them until it reaches the end.
## Bugs

Running with `-n`/`--no-exit` resets the successful and total tries counters on every try.

`--enum` will print out an empty character if there's no L3 cache (`[1] 192.168.178.42      4 CPUs |  L3 | 0 GPU(s)`)

# NOTES

NOTE: It is Only For Educational Purposes. Neither I Say Nor I Promote To Do Anything Illegal  
YouTube <a href="https://www.youtube.com/c/SpeedXTech">Channel</a>: https://www.youtube.com/c/SpeedXTech  
To Support Me By Either Helping In Project Or Donating Small Amount To Me For That Contact Me By [Telegram](https://t.me/TheSpeedX)  
That's All !!
