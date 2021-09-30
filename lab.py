from volterra_helpers import createVoltSession, createUserRoles, delUserNS, delUser, createUserNS

from optparse import OptionParser
from os import environ
import sys
import csv
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

    if session['lastOp']['status'] == 'error':
        raise Exception(session['lastOp']['message'])

    print(session['lastOp'])

    if options.action == 'create':
        namespace_roles = [
            {'namespace': 'system', 'role': 'ves-io-power-developer-role'},
            {'namespace': 'system', 'role': 'f5-demo-infra-write'},
            {'namespace': 'demo-app', 'role': 'ves-io-monitor-role'},
            {'namespace': 'default', 'role': 'ves-io-power-developer-role'},
            {'namespace': 'shared', 'role': 'ves-io-power-developer-role'}
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
    # CSV file
    for row in csv.reader(open(options.filename)):
        (username, fname, lname, namespace) = row
        try:
            update()
        except:
            print("error with",row)
else:
    update()    
#result = delUserNS(namespace, session)
#print(session['lastOp'])
#result = delUser(username, session)
#print(session['lastOp'])

