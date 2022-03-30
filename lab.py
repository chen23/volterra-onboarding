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
        if namespace:
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
import re
get_num = re.compile("student(\d+)").search
if options.filename:
    createCache(session)
    existing_namespaces = [a['name'] for a in session['cache']['namespaces']]
    existing_users = dict([(a['name'],a['namespace_roles']) for a in session['cache']['users']])
    # CSV file
#    print(existing_users)
    existing_namespaces.sort()
    existing_students = [a for a in existing_namespaces if a.startswith("student")]    
#    print(existing_namespaces)
#    print(existing_students)
    last_student = existing_students[-1]
    m = get_num(last_student)
    if m:
        last_student_num = int(m.groups()[0])
    else:
        last_student_num = 100

    for row in csv.reader(open(options.filename)):
        if len(row) == 0:
            continue
        if len(row) == 3:
            (username, fname, lname) = row
            last_student_num += 1
            namespace = "student%03d" %(last_student_num)
        else:
            (username, fname, lname, namespace) = row
#        if username not in existing_users and namespace not in existing_namespaces:
        if username not in existing_users:
            if options.action == "delete":
                print("skipping",username,namespace)
                print("test delete")                
                continue
        if username in existing_users:
            namespace_roles = existing_users[username]
            namespaces = list(set([n['namespace'] for n in namespace_roles if n['namespace'] not in ['system','shared',"*","default","demo-app"]]))
            if namespaces:
                namespace = namespaces[0]
            else:
                namespace = None
            if options.action == "create":
                print("skipping",username)
        print(username,namespace)
#        continue
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

