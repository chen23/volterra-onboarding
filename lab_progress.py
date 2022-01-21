from volterra_helpers import createCache, getHttpLoadBalancers, getTcpLoadBalancers, getItems

from optparse import OptionParser
from os import environ
from os.path import exists
import sys
import csv
import json
import datetime
import requests

parser = OptionParser()

parser.add_option("--tenant")
parser.add_option("--token")
parser.add_option("--action")
parser.add_option("--namespace")
parser.add_option("--filename")
parser.add_option("--resource")

(options, args) = parser.parse_args()

token = options.token or environ.get('VOLTERRA_TOKEN')

tenant = options.tenant

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
total = 0
resource_names = ["origin_pools","virtual_hosts"]
output = []
for row in csv.reader(open(options.filename)):
    namespaces = row[4].split(",")
    if namespaces == ['']:
        continue

#    print(namespaces)
    
    for namespace in namespaces:
        if not namespace.startswith("student"):
            continue
        if namespace.startswith("student4"):
            continue
        # https://www.volterra.io/#operation/ves.io.schema.route.API.List/api/config/namespaces/{namespace}/routes
        resource_list = {}
        for resource_name in resource_names:
            resource_url = "/api/config/namespaces/%s/%s" %(namespace,resource_name)
            resources = getItems(session,resource_url)
            if resources:

                if resource_name == 'virtual_hosts':
                    resource_list[resource_name] = ",".join([r['owner_view']['name'] for r in resources])
                else:
                    resource_list[resource_name] = ",".join(r['name'] for r in resources)
        if(resource_list):
            print(row[0],namespace,resource_list)
            output.append((namespace,row[1],resource_list))
#            print(row[0],namespace,",".join([r['name'] for r in resources]))            
#            print(row[0],namespace,",".join([r['owner_view']['name'] for r in resources]))
            total += len(resources)
            #print(namespace,[h['name'] for h in resources])
            continue
            for health_check in [h['name'] for h in health_checks]:
                health_check_delete_url = "/api/config/namespaces/%s/healthchecks/%s" %(namespace,health_check)
                payload = """{
                  "fail_if_referred": true,
                  "name": "%s",
                  "namespace":"system"
                }""" %(health_check)
                print(health_check_delete_url)
                print(payload)
                resp = session['session'].delete(session['urlBase'] + health_check_delete_url,data=payload)
                print(resp)
                print(resp.text)
output.sort()                
print(output)
import datetime
template = """
<!doctype html>
<head lang="en">

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

<title>Volterra WAF Status Board</title>
<script>
<!--
function timedRefresh(timeoutPeriod) {
	setTimeout("location.reload(true);",timeoutPeriod);
}

window.onload = timedRefresh(60000);

//   -->
</script>
</head><body>
<div class="col-lg-8 mx-auto p-3 py-md-5">
<main>
<h3>Volterra WAF Status Board</h3>
<em>Last updated %s EST</em>
<table class="table">
<thead>
<th scope="col">Student</th>
<th scope="col">Name</th>
<th scope="col">Pools</th>
<th scope="col">Load Balancers</th>
</thead>
""" %(datetime.datetime.now())
html = template
for row in output:
    html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" %(row[0],row[1],row[2].get("origin_pools","&nbsp;"),row[2].get("virtual_hosts","&nbsp;"))
    
#print(html + "</table></main></div></body></html>")
f = open("lab-status.html","w")
f.write(html)
f.write("</table></main></div></body></html>")
sys.exit(0)

#site_token_url = "/api/register/namespaces/system/tokens"
#site_tokens = [s for s in getItems(session,site_token_url) if options.namespace in s['name']]

#print("site tokens")
#print([s['name'] for s in site_tokens])

# print("cloud credentials")

# cloud_credential_url = "/api/config/namespaces/system/cloud_credentialss"
# cloud_credentials = [c for c in getItems(session, cloud_credential_url)]

# print([c['name'] for c in cloud_credentials if options.namespace in c['name']])



site_url = "/api/config/namespaces/system/sites"

#sites = [s for s in getItems(session,site_url) if options.namespace in s['name']]
#print("sites found")

# terraform_status_url = "/api/config/namespaces/system/terraform_parameters/aws_vpc_site/%s/status" %(options.namespace + "-awsnet")
# resp = session['session'].get(session['urlBase'] + terraform_status_url)
# print(terraform_status_url)
# print(resp.text)

# /api/terraform/namespaces/system/terraform/aws_vpc_site/student01-awsnet/run
# terraform_run_url = "/api/terraform/namespaces/system/terraform/aws_vpc_site/%s/run" %(options.namespace + "-awsnet")
# payload = """{
#   "action": "DESTROY",
#   "namespace": "system",
#   "view_kind": "aws_vpc_site",
#   "view_name": "%s"
# }""" %(options.namespace+"-awsnet")

# resp = session['session'].post(session['urlBase'] + terraform_run_url,data=payload)
# print(resp)
# print(resp.text)

# force delete

# terraform_delete_url = "/api/config/namespaces/system/aws_vpc_sites/%s" %(options.namespace + "-awsnet")
# payload = """{
#   "fail_if_referred": true,
#   "name": "%s",
#   "namespace":"system"
# }""" %(options.namespace+"-awsnet")
# print(terraform_delete_url)
# print(payload)
# resp = session['session'].delete(session['urlBase'] + terraform_delete_url,data=payload)
# print(resp)
# print(resp.text)

#site_url = "/api/config/namespaces/system/sites/%s-udf" %(options.namespace)
#site_url = "/api/register/namespaces/system/site/%s-udf/state" %(options.namespace)
# site_url = "/api/register/namespaces/system/registrations/%s-udf" %(options.namespace)
site_url = "/api/register/namespaces/system/site/%s-udf/state" %(options.namespace)
payload = """{
  "state": 7,
  "name": "%s",
  "namespace":"system"
}""" %(options.namespace+"-udf")
resp = session['session'].post(session['urlBase'] + site_url, data=payload)
print(resp)
print(resp.text)



print("site registrations")
site_names = ['student01-udf']
for name in site_names:
    reg_url = "/api/register/namespaces/system/registrations_by_site/%s" %(name)
    registrations = getItems(session,reg_url)
    print(name,registrations[0]['object']['spec']['gc_spec']['infra']['certified_hw'])
sys.exit(0)
pool_url = "/api/config/namespaces/%s/origin_pools" %(options.namespace)
origin_pools = getItems(session,pool_url)

if session['lastOp']['status'] == 'error':
    print(session['lastOp']['message'])
    raise Exception(session['lastOp']['message'])

print("origin pools")
print([o['name'] for o in origin_pools])

health_check_url = "/api/config/namespaces/%s/healthchecks" %(options.namespace)
health_checks = getItems(session,health_check_url)

if session['lastOp']['status'] == 'error':
    print(session['lastOp']['message'])
    raise Exception(session['lastOp']['message'])

print("health checks")
print([h['name'] for h in health_checks])

httplbs = getHttpLoadBalancers(session,options.namespace)

if session['lastOp']['status'] == 'error':
    print(session['lastOp']['message'])
    raise Exception(session['lastOp']['message'])

tcplbs = getTcpLoadBalancers(session,options.namespace)
print("http lb found")
print([h['name'] for h in httplbs])

print("tcp lb found")
print([t['name'] for t in tcplbs])

if session['lastOp']['status'] == 'error':
    print(session['lastOp']['message'])
    raise Exception(session['lastOp']['message'])


