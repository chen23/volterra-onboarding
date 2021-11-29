from volterra_helpers import createVoltSession, createUserRoles, delUserNS, delUser, createUserNS

from optparse import OptionParser
from os import environ
import sys
import csv
import datetime
import requests

from os.path import exists
import json

parser = OptionParser()

parser.add_option("--tenant")
parser.add_option("--token")
parser.add_option("--email")
parser.add_option("--first_name")
parser.add_option("--last_name")
parser.add_option("--namespace")
parser.add_option("--filename")
parser.add_option("--action")

(options, args) = parser.parse_args()

token = environ.get('VOLTERRA_TOKEN') or options.token

tenant = options.tenant
username = options.email
fname = options.first_name
lname = options.last_name
namespace = options.namespace


def createVoltSession(token, tenantName):
    now = datetime.datetime.now()
    apiToken = "APIToken {0}".format(token)
    s = requests.Session()
    s.headers.update({'Authorization': apiToken})
    urlBase = "https://{0}.console.ves.volterra.io".format(tenantName)
    create = {
        'operation': 'createVoltSession',
        'status': 'success',
        'message': 'voltSession created',
        'time': now.strftime("%m/%d/%Y, %H:%M:%S")
    }
    session = {'session': s, 'urlBase': urlBase, 'lastOp': create}
    return session

session = createVoltSession(token, tenant)
if(exists("cache.json")):
    print("loading cache")
    session['cache'] = json.load(open("cache.json"))
else:
    createCache(session)
    json.dump(session['cache'],open("cache.json","w"))

email = options.namespace.replace("-",".") + "@f5.com"
user_roles_url = session['urlBase'] + "/api/web/custom/namespaces/system/user_roles"

for user in session['cache']['users']:
    if user['name'] == email:
        role_cache = {}
        
        for idx in ['namespace', 'email', 'first_name', 'last_name', 'namespace_roles']:
            role_cache[idx] = user[idx]
            
        delUserNS(email,session)
        createUserNS(email,session)
        # restore roles
        resp = session['session'].put(user_roles_url, json=role_cache)
        print(resp)
        print(resp.text)
        namespace_roles = user['namespace_roles']
