from volterra_helpers import createVoltSession, createUserRoles, delUserNS, delUser, createUserNS, createCache

from optparse import OptionParser
from os import environ
import sys
import csv

parser = OptionParser()

parser.add_option("--tenant")
parser.add_option("--token")
parser.add_option("--action")
parser.add_option("--filename",help="output CSV to this file")

(options, args) = parser.parse_args()

token = options.token or environ.get('VOLTERRA_TOKEN')

tenant = options.tenant

session = createVoltSession(token, tenant)
createCache(session)
#print(session['cache'])
#print(session['cache']['users'])
#print(session['cache']['namespaces'])

has_nologin = list(filter(lambda a: not a['last_login_timestamp'], session['cache']['users']))

has_login = list(filter(lambda a: a['last_login_timestamp'], session['cache']['users']))

has_login.sort(key=lambda a: a['last_login_timestamp'])

has_nologin.sort(key=lambda a:a['creation_timestamp'])

nologin = [(a['first_name'],a['last_name'],a['email'],a['creation_timestamp']) for a in has_nologin]

if options.filename:
    output = open(options.filename,"w")
else:
    output = sys.stdout

def update_user(user):
    user['first_name'] = user['first_name'].lstrip()
    user['last_name'] = user['last_name'].lstrip()
    user['creation_timestamp'] = user['creation_timestamp'].split('T')[0]
    user['custom_namespaces'] = '"' +  ",".join(list(set([n['namespace'] for n in user['namespace_roles'] if n['namespace'] not in ['system','shared',"*","default","demo-app"]]))) + '"'
    if user['last_login_timestamp']:
        user['last_login_timestamp'] = user['last_login_timestamp'].split('T')[0]

#print("Users that have not logged in",file=output)
print("#Email, Name, Creation Timestamp, Last Login Timestamp, Namespaces",file=output)

for user in has_nologin:
    update_user(user)
    print("{email},{first_name} {last_name},{creation_timestamp},,{custom_namespaces}".format(**user),file=output)
    
#print("Users that have logged in")

for user in has_login: 
    update_user(user)       
    print("{email},{first_name} {last_name},{creation_timestamp},{last_login_timestamp},{custom_namespaces}".format(**user),file=output)
