from volterra_helpers import createVoltSession, createCache, getHttpLoadBalancers, getTcpLoadBalancers, getItems

from optparse import OptionParser
from os import environ
import sys
import csv

parser = OptionParser()

parser.add_option("--tenant")
parser.add_option("--token")
parser.add_option("--action")
parser.add_option("--namespace")
parser.add_option("--filename")

(options, args) = parser.parse_args()

token = options.token or environ.get('VOLTERRA_TOKEN')

tenant = options.tenant

session = createVoltSession(token, tenant)
createCache(session)

site_token_url = "/api/register/namespaces/system/tokens"
site_tokens = [s for s in getItems(session,site_token_url) if options.namespace in s['name']]

print("site tokens")
print([s['name'] for s in site_tokens])

print("cloud credentials")

cloud_credential_url = "/api/config/namespaces/system/cloud_credentialss"
cloud_credentials = [c for c in getItems(session, cloud_credential_url)]

print([c['name'] for c in cloud_credentials if options.namespace in c['name']])

site_url = "/api/config/namespaces/system/sites"

sites = [s for s in getItems(session,site_url) if options.namespace in s['name']]
print("sites found")
site_names = [s['name'] for s in sites]
print(site_names)

print("site registrations")
for name in site_names:
    reg_url = "/api/register/namespaces/system/registrations_by_site/%s" %(name)
    registrations = getItems(session,reg_url)
    print(name,registrations[0]['object']['spec']['gc_spec']['infra']['certified_hw'])

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


