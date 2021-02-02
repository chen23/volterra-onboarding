import requests
import json
import datetime

def updateSO(s, op, status, message):
    now = datetime.datetime.now()
    action = {
        'operation': op,
        'status': status,
        'time': now.strftime("%m/%d/%Y, %H:%M:%S"),
        'message': message
    }
    s['log'].append(action)
    return s

def createUserCache(s, cacheTO=60):
    url = s['urlBase'] + "/api/web/custom/namespaces/system/user_roles"
    try:
        resp = s['session'].get(url)
        resp.raise_for_status()
        users = json.loads(resp.text)['items']
    except requests.exceptions.RequestException as e: 
        return updateSO(s, 'popUserCache', 'error', e)
    except json.decoder.JSONDecodeError as e:
        return updateSO(s, 'popUserCache', 'error', e)
    expiry = datetime.datetime.now() + datetime.timedelta(seconds=cacheTO)
    cache = {
        'expiry': expiry.timestamp(),
        'tenantUsers': users
    }
    updateSO(s, 'createUserCache', 'success', "userCache populated")
    return cache

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
    logs = [create]
    session = {'session': s, 'urlBase': urlBase, 'log': logs}
    return session

def findUserNS(email):
    userNS = ""
    if "#EXT#@" in email:
        userNS = email.split(
            '#EXT#@')[0].replace('.', '-').replace('_', '-').lower()
    else:
        userNS = email.split('@')[0].replace('.', '-').lower()
    return userNS
    
def checkUserNS(email, s):
    userNS = findUserNS(email)
    url = s['urlBase'] + "/api/web/namespaces/{0}".format(userNS)
    try:
        resp = s['session'].get(url)
        if 200 <= resp.status_code <= 299:
            return updateSO(s, 'checkUserNS', 'present', 'NS is present')
        else:
            return updateSO(s, 'checkUserNS', 'absent', 'NS is absent')
    except requests.exceptions.RequestException as e:  
        return updateSO(s, 'checkUserNS', 'error', e)

def checkUser(email, s, c):
    if c['expiry'] < datetime.datetime.now().timestamp():
        createUserCache(s)
    thisUser = next((user for user in c['tenantUsers'] if user['email'].lower() == email.lower()), None)
    if thisUser:
        return updateSO(s, 'checkUser', 'present', 'User {0} is present'.format(email))
    return updateSO(s, 'checkUser', 'absent', 'User {0} is absent'.format(email))
    
def createUserNS(email, s):
    userNS = findUserNS(email)
    url = s['urlBase'] + "/api/web/namespaces"
    nsPayload = {
        'metadata': 
            {
                'annotations': {}, 
                'description': 'automatically generated by tenant admin', 
                'disable': False, 
                'labels': {}, 
                'name': userNS, 
                'namespace': ''
            }, 
        'spec': {}
    }
    try:
        resp = s['session'].post(url, json=nsPayload)
        resp.raise_for_status()
        return updateSO(s, 'createUserNS', 'success', 'NS {0} was created'.format(email))
    except requests.exceptions.RequestException as e:  
        return updateSO(s, 'createUserNS', 'error', e)

def delUserNS(email, s):
    userNS = findUserNS(email)
    url = s['urlBase'] + "/api/web/namespaces/{0}/cascade_delete".format(userNS)
    nsPayload = {
        "name": userNS
    }
    try:
        resp = s['session'].post(url, json=nsPayload)
        resp.raise_for_status()
        return updateSO(s, 'delUserNS', 'success', 'NS {0} deleted'.format(email)) 
    except requests.exceptions.RequestException as e:  
        return updateSO(s, 'delUserNS', 'error', e)

def createUserRoles(email, first_name, last_name, s, createdNS=None, exists=False):
    url = s['urlBase'] + "/api/web/custom/namespaces/system/user_roles"
    userPayload = {
        'email': email, 
        'first_name': first_name, 
        'last_name': last_name, 
        'name': email, 
        'idm_type': 'SSO', 
        'namespace': 'system', 
        'namespace_roles': 
            [
                {'namespace': 'system', 'role': 'ves-io-power-developer-role'}, 
                {'namespace': 'system', 'role': 'f5-demo-infra-write'},
                {'namespace': '*', 'role': 'ves-io-monitor-role'}, 
                {'namespace': 'default', 'role': 'ves-io-power-developer-role'}, 
                {'namespace': 'shared', 'role': 'ves-io-power-developer-role'} 
            ], 
            'type': 'USER'
    }
    if createdNS:
        userPayload['namespace_roles'].append({'namespace': createdNS, 'role': 'ves-io-admin-role'})
    try:
        if exists:
            resp = s['session'].put(url, json=userPayload)
        else:
            resp = s['session'].post(url, json=userPayload)
        resp.raise_for_status()
        return updateSO(s, 'createUserRoles', 'success', 'User {0} and Roles created/updated'.format(email))
    except requests.exceptions.RequestException as e:  
        return updateSO(s, 'createUserRoles', 'error', e)

def delUser(email, s):
    url = s['urlBase'] + "/api/web/custom/namespaces/system/users/cascade_delete"
    userPayload = {
        "email": email,
        "namespace": "system"
    }
    try:
        resp = s['session'].post(url, json=userPayload)
        resp.raise_for_status()
        return updateSO(s, 'delUser', 'success', 'User {0} deleted'.format(email))
    except requests.exceptions.RequestException as e:  
        return updateSO(s, 'delUser', 'error', e)

def cliAdd(token, tenant, email, first_name, last_name, createNS, oRide):
    createdNS = None
    s = createVoltSession(token, tenant)
    c = createUserCache(s)

    #We need to know if the user exists
    userExist = False
    checkUser(email, s, c)                                                                      #Is the user present?
    if s['log'][-1]['status'] == 'present':
        userExist = True
    if oRide:                                                                                   #Handle the override
        if createNS:
            checkUserNS(email,s) 
            if s['log'][-1]['status'] == 'present':                                             #Is the NS present?
                delUserNS(email, s)                                                             #Delete the NS (and everything inside)
            createUserNS(email, s)                                                              #Create the NS
            createdNS = findUserNS(email)                                                       #TBD: More robust -- check for success
        createUserRoles(email, first_name, last_name, s, createdNS, userExist)                  #Create the user with her roles
        return {'status': 'success', 'log': s['log']}
    else:                                                                                       #Standard use case
        if createNS:
            checkUserNS(email,s)
            if s['log'][-1]['status'] == 'present':                                             #Is the NS present?
                return {'status': 'failure', 'reason': 'NS already exists', 'log': s['log']}    #No oRide -- this is fatal
            else:   
                createUserNS(email, s)                                                          #Create the NS
                createdNS = s['log'][-1]['resp']['metadata']['name']                            #TBD: more robust
        if userExist:                                                                           #User is present
            return {'status': 'failure', 'reason': 'User already exists', 'log': s['log']}      #No oRide -- this is fatal
        else:
            createUserRoles(email, first_name, last_name, s, createdNS)                         #Create the user
            return {'status': 'success', 'log': s['logs']}
 

def cliRemove(token, tenant, email):
    s = createVoltSession(token, tenant)
    delUserNS(email, s)
    delUser(email, s)
    return {'status': 'success', 'log': s['log']}

