# enclave

A minimal, modular c2 framework written in python

## setup

```
git clone --recurse-submodules -b adversary-dev git@gitlab.com:stevecoward/enclave.git
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

1. clone enclave and enclave-modules and use the `adversary-dev` branch
2. create a python virtual environment named `env`
3. activate new python virtual environment
4. install all required python libraries

## first-run

```
$ python enclave.py
                     .__
  ____   ____   ____ |  | _____ ___  __ ____
_/ __ \ /    \_/ ___\|  | \__  \  \/ // __ \
\  ___/|   |  \  \___|  |__/ __ \   /\  ___/
 \___  >___|  /\___  >____(____  /\_/  \___  >   .___
     \/     \/     \/          \/    _____ \/  __| _/__  __
                              ______ \__  \   / __ |\  \/ /
                             /_____/  / __ \_/ /_/ | \   /
                                     (____  /\____ |  \_/
                                          \/      \/
[*] enclave folder doesn't exist, creating...
[-] starting enclave api server...

enclave>
```

on startup, enclave will look for a folder named `.enclave` in the user's $HOME. this folder will serve as local storage for all tasks run from within enclave. important files to note are:

* enclave.db
  * sqlite database for the enclave framework
* spool
  * file containing all commands and output during a session in enclave

at the enclave prompt, typing `use` followed by tab-completing will list all available modules within enclave:

```
enclave> use 
                      implant/build/generic
                      implant/interact/generic
                      implant/interact/slowcheetah
                      implant/interact/asplant
                      tomcat/foolishtom
                      puppet
                      puppet/touch
enclave> use puppet
                                __
.-----.--.--.-----.-----.-----.|  |_
|  _  |  |  |  _  |  _  |  -__||   _|
|   __|_____|   __|   __|_____||____|
|__|        |__|  |__|


enclave: puppet> options
                                __
.-----.--.--.-----.-----.-----.|  |_
|  _  |  |  |  _  |  _  |  -__||   _|
|   __|_____|   __|   __|_____||____|
|__|        |__|  |__|

+options-----+---------+----------+-----------------------------------------------------------+
| name       | setting | required | description                                               |
+------------+---------+----------+-----------------------------------------------------------+
| vps        |         | False    | vps location for puppets (digitalocean | lightsail | ec2) |
| api key    |         | False    | api key or token for vps                                  |
| secret key |         | False    | secret key for vps if required                            |
+------------+---------+----------+-----------------------------------------------------------+

enclave: puppet> set vps digitalocean
[+] vps --> digitalocean

enclave: puppet> set api_key 8c75c15<redacted>bc1dba
[+] api_key --> 8c75c15<redacted>bc1dba

enclave: puppet> help

+available commands---------------------------------------------+
| command     | description                                     |
+-------------+-------------------------------------------------+
| list        | lists all puppets in databases                  |
| refresh     | grabs ip info from vps on puppets               |
| store_creds | stores set creds in db. list_creds to show them |
| list_creds  | lists all stored vps creds                      |
| touch       | use puppet/touch to create a new puppet         |
| help        | you are here                                    |
+-------------+-------------------------------------------------+

enclave: puppet> store_creds

[+] added new vps record

enclave: puppet> touch -vps b5a5663 -amount 1 -key /Users/scoward/.enclave/enclave-id_rsa.pub


 __                     __
|  |_.-----.--.--.----.|  |--.
|   _|  _  |  |  |  __||     |
|____|_____|_____|____||__|__|


[+] vps --> b5a5663
[+] amount --> 1
[+] key --> /Users/scoward/.enclave/enclave-id_rsa.pub
[-] building puppet(s)...
[-] pubkey confirmed, ready to touch
[+] created do puppet:91741846

enclave: puppet> list

 puppet 91741846 now has ip: 159.89.177.162
+puppets---------+--------------------------------------+------------------------------------------+-------------------------+
| ip             | name                                 | vps                                      | created                 |
+----------------+--------------------------------------+------------------------------------------+-------------------------+
| 159.89.177.162 | 4b3a5c72-8f55-43b9-8d11-d8cf48577593 | b5a56637c0037f7dd51a3010991a126dcaa91b8e | 2018-01-04 19:20:28 EST |
+----------------+--------------------------------------+------------------------------------------+-------------------------+

enclave: puppet>
```

more to come...