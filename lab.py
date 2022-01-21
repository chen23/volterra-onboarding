from volterra_helpers import createVoltSession, createUserRoles, delUserNS, delUser, createUserNS, createCache

from optparse import OptionParser
from os import environ
import sys
import csv
import time
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

session = createVoltSession(token, tenant)

def update():
    if options.action == 'create':
        result = createUserNS(namespace, session)
    elif options.action == 'delete':
        result = delUserNS(namespace, session)

    if session['lastOp']['status'] == 'error' and options.action == 'create':
        print(session['lastOp']['message'])
#        raise Exception(session['lastOp']['message'])
    else:
        print(session['lastOp']['message'])
    #print(session['lastOp'])
#            {'namespace': 'demo-app', 'role': 'ves-io-monitor-role'},
#            {'namespace': '*', 'role': 'ves-io-monitor-role'},
#             {'namespace': 'demo-app', 'role': 'ves-io-monitor-role'},            
    if options.action == 'create':
        namespace_roles = [
            {'namespace': 'system','role':'chen-lab-users'},
#            {'namespace': 'system', 'role': 'ves-io-power-developer-role'},
#            {'namespace': 'system', 'role': 'f5-demo-infra-write'},
#            {'namespace': 'shared', 'role': 'ves-io-power-developer-role'}
        ]

        result = createUserRoles(username, fname, lname, session, namespace, False, False, idm_type = 'VOLTERRA_MANAGED', namespace_roles = namespace_roles)    
    elif options.action == 'delete':
        result = delUser(username, session)
    #print(result)
    if session['lastOp']['status'] == 'error':
        print(session['lastOp']['message'])
        raise Exception(session['lastOp']['message'])        
    print(session['lastOp'])

if options.filename:
    createCache(session)
    existing_namespaces = [a['name'] for a in session['cache']['namespaces']]
    existing_users = [a['name'] for a in session['cache']['users']]
    # CSV file
    for row in csv.reader(open(options.filename)):
        if len(row) == 0:
            continue
        (username, fname, lname, namespace) = row
        if username not in existing_users and namespace not in existing_namespaces:
            if options.action == "delete":
                print("skipping",username,namespace)
                continue
        if username[0] == '#':
            continue
        try:
            update()
        except:
            print(session['lastOp']['message'])            
            print("error with",row)
        time.sleep(3)            
else:
    update()    
#result = delUserNS(namespace, session)
#print(session['lastOp'])
#result = delUser(username, session)
#print(session['lastOp'])

