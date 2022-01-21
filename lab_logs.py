from volterra_helpers import createCache, getHttpLoadBalancers, getTcpLoadBalancers, getItems, getLogs
from dateutil.parser import parse
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

# payload = """{
#   "query": "{method=\\"POST\\"}",
#   "namespace": "system",
#   "sort": "DESCENDING",
#   "limit": 500,
#   "aggs": {},
#   "start_time": "2022-01-13T05:00:00.000Z",
#   "end_time": "2022-01-14T05:00:00.000Z"
# }"""

payload = """{
  "query": "{namespace!=\\"system\\"}",
  "namespace": "system",
  "sort": "DESCENDING",
  "limit": 500,
  "aggs": {},
  "start_time": "2022-01-13T05:00:00.000Z",
  "end_time": "2022-01-14T05:00:00.000Z"
}"""


# payload = """{
#   "query": "{method=\\"POST\\"}",
#   "namespace": "system",
#   "sort": "DESCENDING",
#   "limit": 500,
#   "aggs": {},
#   "start_time": "2022-01-13T10:00:00.000Z",
#   "end_time": "2022-01-14T05:00:00.000Z"
# }"""


# payload = """{
#   "query": "{method=\\"POST\\"}",
#   "namespace": "system",
#   "sort": "DESCENDING",
#   "limit": 500,
#   "aggs": {},
#   "start_time": "2022-01-14T05:00:00.000Z",
#   "end_time": "2022-01-15T05:00:00.000Z"
# }"""

payload = """{
  "query": "{namespace!=\\"system\\"}",
  "namespace": "system",
  "sort": "DESCENDING",
  "limit": 500,
  "scroll": true,
  "aggs": {},
  "start_time": "2022-01-18T05:00:00.000Z",
  "end_time": "2022-01-19T05:00:00.000Z"
}"""

payload = """{
  "query": "{namespace!=\\"system\\"}",
  "namespace": "system",
  "sort": "DESCENDING",
  "limit": 500,
  "scroll": true,
  "aggs": {},
  "start_time": "2022-01-19T15:00:00.000Z",
  "end_time": "2022-01-20T05:00:00.000Z"
}"""

payload = """{
  "query": "{namespace!=\\"system\\"}",
  "namespace": "system",
  "sort": "DESCENDING",
  "limit": 500,
  "scroll": true,
  "aggs": {},
  "start_time": "2022-01-19T18:00:00.000Z",
  "end_time": "2022-01-20T18:00:00.000Z"
}"""


payload = """{
  "query": "{namespace!=\\"system\\"}",
  "namespace": "system",
  "sort": "DESCENDING",
  "limit": 500,
  "scroll": true,
  "aggs": {},
  "start_time": "2022-01-20T00:00:00.000Z",
  "end_time": "2022-01-21T00:00:00.000Z"
}"""


#payload = "{}"
print(payload)
resp = getLogs(session,"/api/data/namespaces/system/audit_logs",payload)
#print(session['lastOp']['message'])
print(len(resp))
x = 0
output = []
for entry in resp:
#    if 'rpc' in entry and entry['rpc'].endswith("Create"):
    if 'rpc' in entry and (entry['rpc'].endswith("Create") or entry['rpc'].endswith(".Replace")):    
#    if 'rpc' in entry:
        if entry['rpc'] in ['ves.io.schema.user.CustomAPI.Create','ves.io.schema.namespace.API.Create','ves.io.schema.user.CustomAPI.Replace','ves.io.schema.namespace.API.Replace']:
            continue
#        print(entry)
        object_json = [e for e in entry.keys() if e.endswith(".object_json")]
        details = None
        if object_json:
            json_object = json.loads(entry[object_json[0]])
#            print(json_object)
            details = [json_object['metadata']['namespace'],json_object['metadata']['name']]
            output.append((entry['time'],details[0],entry['rpc'],details[1]))
        else:
            pass
            #output.append((entry['time'],entry['rpc'],entry))
        #output.append((entry['time'],entry['user'],entry['rpc'],x,details))



    x+=1
output.sort()
output.reverse()
import datetime
template = """
<!doctype html>
<head lang="en">

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

<title>Volterra WAF Lab Logs</title>
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
<th scope="col">Date/Time</th>
<th scope="col">Student</th>
<th scope="col">API</th>
<th scope="col">Object</th>
</thead>
""" %(datetime.datetime.now())
html = template
from dateutil import tz
to_zone = tz.tzlocal()
for x in output:
    if options.filename:

        html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" %(parse(x[0]).astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S EST"),x[1],x[2][14:],x[3])
    

        
        pass
    else:
        print(parse(x[0]).astimezone(to_zone).strftime("%Y-%m-%d %H:%M:%S EST"),x[1],x[2][14:],x[3])
#        print(x)
import pprint
#pprint.pprint(resp[463])
if options.filename:
    f = open(options.filename,"w")
    f.write(html)
    f.write("</table></main></div></body></html>")
