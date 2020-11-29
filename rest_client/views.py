import datetime
import hashlib
import random

import requests
from django.shortcuts import render, redirect
# Create your views here.
from requests.auth import HTTPBasicAuth

from .configuration import rest_password, rest_user, rest_service

ALPHABET = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

GET = 'get'
POST = 'post'
DELETE = 'delete'
PUT = 'put'


def rest(method, url, json=None):
    return requests.request(method, rest_service + url, auth=HTTPBasicAuth(rest_user, rest_password), json=json)


def check_login(session):
    if not ('login' in session and 'password' in session):
        return None
    login = session['login']
    password = session['password']
    resp = rest(GET, 'login/', {'login': login, 'password': password})
    if resp.status_code != 200:
        return None
    j = resp.json()
    if 'id' in j:
        return j['id']
    else:
        return None


def projects(request):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'tasks/')
    j = tasks.json()
    formated = []
    for i in j['tasks']:
        task = {'name': i['name'], 'id': i['id']}
        creator = rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]
        task['creator'] = creator['short_name']
        task['creator_id'] = creator['id']
        responsible = rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0]
        task['responsible'] = responsible['short_name']
        task['responsible_id'] = responsible['id']
        formated.append(task)
    return render(request, 'rest_client/tasks_root.html', {'tasks': formated, 'userid': userid, 'username':
        rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def add_tasks_group(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'tasks/', {
            "tasks": {
                "name": request.GET['name'],
                "parent": pk,
                "creator": userid,
                "responsible": request.GET['responsible'],
                "system": (request.GET['system'] if 'system' in request.GET else None)
            },
            "isgroup": True
        })
        return redirect('/client/tasks/' + ("" if pk is None else str(pk)))
    employees = rest(GET, 'employees/').json()['employees']
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee['id'], 'short_name': employee['short_name']})
    context = {'employees': employees_list}
    if pk:
        context['parent'] = pk
    systems = []
    for system in rest(GET, 'systemparts/').json()['systemparts']:
        systems.append({'id': system['id'], 'name': system['name']})
    context['is_group'] = True
    context['systems'] = systems
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/tasks_new.html', context)


def tasks(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'tasks/' + str(pk))
    j = tasks.json()['tasks'][0]
    if 'delete' in request.GET:
        rest(DELETE, 'tasks/' + str(pk))
        return redirect('/client/tasks/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        fields = ["name", "start", "end", "parent", "responsible", "system", "status"]
        save = {}
        for field in fields:
            if field in request.GET:
                save[field] = request.GET[field]
        rest(PUT, 'tasks/' + str(pk) + '/', {
            "tasks": save,
            "isgroup": 'child' in j
        })
        return redirect('/client/tasks/' + str(pk))
    context = {}
    if 'child' in j:
        tasks = []
        for i in j['child']:
            task = {'name': i['name'], 'id': i['id']}
            creator = rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]
            task['creator'] = creator['short_name']
            task['creator_id'] = creator['id']
            responsible = rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0]
            task['responsible'] = responsible['short_name']
            task['responsible_id'] = responsible['id']
            tasks.append(task)
            task['is_group'] = True if 'child' in i else False
        context['tasks'] = tasks
        context['is_group'] = True
    else:
        context['is_group'] = False
        context['status'] = j['status']
        context['start'] = datetime.datetime.strptime(j['start'], '%Y-%m-%dT%H:%M:%SZ').replace(
            microsecond=0).strftime('%Y-%m-%dT%H:%M')
        context['end'] = datetime.datetime.strptime(j['end'], '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0).strftime(
            '%Y-%m-%dT%H:%M')
        systems = []
        for system in rest(GET, 'systemparts/').json()['systemparts']:
            systems.append({'id': system['id'], 'name': system['name']})
        context['systems'] = systems
        context['system_id'] = j['system']
        artefacts = []
        for i in rest(GET, 'artefacts/of/' + str(pk)).json()['artefacts']:
            artefacts.append({'id': i['id'], 'title': i['title']})
        context['artefacts'] = artefacts
    employees = []
    for employee in rest(GET, 'employees/').json()['employees']:
        employees.append({'id': employee['id'], 'short_name': employee['short_name']})
    taskgroups = []
    for taskgroup in rest(GET, 'taskgroups/').json()['taskgroups']:
        taskgroups.append({'id': taskgroup['id'], 'name': taskgroup['name']})
    context['taskgroups'] = taskgroups
    context['employees'] = employees
    context['name'] = j['name']
    context['creator_id'] = j['creator']
    context['creator'] = rest(GET, 'structures/' + str(j['creator'])).json()['structures'][0]['short_name']
    context['id'] = j['id']
    context['responsible_id'] = j['responsible']
    if j['parent']:
        context['parent'] = j['parent']
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/tasks.html', context)


def login(request):
    if 'login' in request.session and 'password' in request.session:
        if check_login(request.session):
            return redirect('projects')
        else:
            del request.session['login']
            del request.session['password']
    try:
        request.session['login'] = request.GET['login']
        request.session['password'] = request.GET['password']
        id = check_login(request.session)
        if id:
            request.session['is_admin'] = rest(GET, 'structures/' + str(id)).json()['structures'][0]['isadmin']
            return redirect('projects')
        else:
            return render(request, 'rest_client/login.html', {'failed': True})
    except KeyError:
        pass
    return render(request, 'rest_client/login.html', {'failed': False})


def logout(request):
    del request.session['login']
    del request.session['password']
    return redirect('login')


def structures_root(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'structures/')
    j = tasks.json()
    formated = []
    for i in j['structures']:
        task = {'name': i['name'], 'id': i['id']}
        formated.append(task)
    return render(request, 'rest_client/structures_root.html',
                  {'structures': formated, 'adminmode': request.session['is_admin'], 'userid': userid,
                   'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def structures(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'structures/' + str(pk))
    j = tasks.json()['structures'][0]
    if 'delete' in request.GET:
        rest(DELETE, 'structures/' + str(pk))
        return redirect('/client/structures/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        if 'child' in j:
            rest(PUT, 'structures/' + str(pk) + '/', {
                "structures": {
                    "name": request.GET['name'],
                },
                "isgroup": True
            })
        else:
            rest(PUT, 'structures/' + str(pk) + '/', {
                "structures": {
                    "full_name": request.GET['name'],
                    "short_name": request.GET['short_name'],
                    "login": request.GET['login'],
                    "isadmin": 'isadmin' in request.GET,
                    "parent": request.GET['parent'],
                    "position": request.GET['position']
                },
                "isgroup": False
            })
            return redirect('/client/structures/' + str(pk))
    if 'reset_password' in request.GET:
        return redirect('/client/structures/reset_password/' + str(pk))
    formated = []
    if 'child' in j:
        is_group = True
        for i in j['child']:
            structures = {'id': i['id']}
            if 'child' in i:
                structures['is_group'] = True
                structures['name'] = i['name']
            else:
                structures['is_group'] = False
                structures['name'] = i['short_name']
            formated.append(structures)
    else:
        is_group = False
    context = {'structures': formated, 'parent_id': ('' if j['parent'] is None else j['parent']),
               'name': (j['name'] if 'name' in j else j['full_name']), 'is_group': is_group, 'id': j['id'], }
    if not is_group:
        context['short_name'] = j['short_name']
        context['is_admin'] = j['isadmin']
        context['login'] = j['login']
        context['position_id'] = j['position']
        if j['position']:
            context['position'] = rest(GET, 'positions/' + str(j['position'])).json()['positions'][0]['name']
        if j['parent']:
            context['parent'] = rest(GET, 'structures/' + str(j['parent'])).json()['structures'][0]['name']
        positions = []
        for i in rest(GET, 'positions/').json()['positions']:
            positions.append({'id': i['id'], 'name': i['name']})
        context['positions'] = positions
        parents = []
        for i in rest(GET, 'divisions/').json()['divisions']:
            parents.append({'id': i['id'], 'name': i['name']})
        context['parents'] = parents
        tasks = []
        for i in rest(GET, 'tasks/of/struct/' + str(pk)).json()['tasks']:
            tasks.append({'id': i['id'], 'name': i['name'], 'creator_id': i['creator'], 'status': i['status'],
                          'creator': rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]['short_name'],
                          'start': datetime.datetime.strptime(i['start'], '%Y-%m-%dT%H:%M:%SZ')})
        context['tasks'] = sorted(tasks, key=lambda x: x['start'], reverse=True)
        for i in context['tasks']:
            i['start'] = i['start'].strftime('%Y-%m-%dT%H:%M')
    context['adminmode'] = request.session['is_admin']
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    context['pk'] = pk
    return render(request, 'rest_client/structures.html',
                  context)


def add_structure_leaf(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    status_code = None
    if 'add' in request.GET:
        if request.GET['password1'] == request.GET['password2']:
            salt = ''.join([random.choice(ALPHABET) for x in range(32)])
            password = hashlib.md5((request.GET['password1'] + salt).encode('utf-8')).hexdigest()
            response = rest(POST, 'structures/', {'structures': {"full_name": request.GET['name'],
                                                                 "short_name": request.GET['short_name'],
                                                                 "login": request.GET['login'],
                                                                 "salt": salt,
                                                                 "hash": password,
                                                                 "isadmin": 'isadmin' in request.GET,
                                                                 "parent": request.GET['parent'],
                                                                 "position": request.GET['position']},
                                                  'isgroup': False})
            status_code = response.status_code
            if status_code == 200:
                return redirect('/client/structures/' + str(pk))
        else:
            status_code = -1
    divisions = []
    for division in rest(GET, 'divisions/').json()['divisions']:
        divisions.append({'id': str(division['id']), 'name': division['name']})
    divisions.sort(key=lambda x: x['name'])
    positions = []
    for position in rest(GET, 'positions/').json()['positions']:
        positions.append({'id': str(position['id']), 'name': position['name']})
    positions.sort(key=lambda x: x['name'])
    context = {'divisions': divisions, 'parent': str(pk), 'positions': positions, 'is_group': False}
    fields = ['name', 'short_name', 'position', 'parent', 'isadmin', 'login', 'password1', 'password2']
    for field in fields:
        if field in request.GET:
            context[field] = request.GET[field]
    if status_code:
        context['status'] = status_code
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/structures_new.html', context)


def add_structure(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'structures/', {'structures': {"name": request.GET['name'],
                                                  "parent": pk, }, 'isgroup': True})
        return redirect('/client/structures/' + (str(pk) if pk else ''))
    context = {'parent': str(pk), 'is_group': True}
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/structures_new.html', context)


def systems_root(request):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'systems/')
    j = tasks.json()
    formated = []
    for i in j['systems']:
        task = {'name': i['name'], 'id': i['id']}
        formated.append(task)
    return render(request, 'rest_client/systems_root.html',
                  {'systems': formated, 'adminmode': request.session['is_admin'], 'userid': userid,
                   'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def systems(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks = rest(GET, 'systems/' + str(pk))
    j = tasks.json()['systems'][0]
    if 'delete' in request.GET:
        rest(DELETE, 'systems/' + str(pk))
        return redirect('/client/systems/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        rest(PUT, 'systems/' + str(pk) + '/', {
            "systems": {
                "name": request.GET['name'],
            },
            "isgroup": 'child' in j
        })
        return redirect('/client/systems/' + str(pk))
    formated = []
    if 'child' in j:
        is_group = True
        for i in j['child']:
            systems = {'id': i['id']}
            systems['name'] = i['name']
            if 'child' in i:
                systems['is_group'] = True
            else:
                systems['is_group'] = False
            formated.append(systems)
    else:
        is_group = False
    context = {'systems': formated, 'parent_id': ('' if j['parent'] is None else j['parent']),
               'name': (j['name'] if 'name' in j else j['full_name']), 'is_group': is_group, 'id': j['id'], }
    if not is_group:
        parents = []
        for i in rest(GET, 'systemgroups/').json()['systemgroups']:
            parents.append({'id': i['id'], 'name': i['name']})
        context['parents'] = parents
        tasks = []
        for i in rest(GET, 'tasks/of/sys/' + str(pk)).json()['tasks']:
            tasks.append({'id': i['id'], 'name': i['name'], 'creator_id': i['creator'], 'status': i['status'],
                          'creator': rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]['short_name'],
                          'responsible_id': i['responsible'],
                          'responsible': rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0][
                              'short_name'],
                          'start': datetime.datetime.strptime(i['start'], '%Y-%m-%dT%H:%M:%SZ')})
        context['tasks'] = sorted(tasks, key=lambda x: x['start'], reverse=True)
        for i in context['tasks']:
            i['start'] = i['start'].strftime('%Y-%m-%dT%H:%M')
    context['adminmode'] = request.session['is_admin']
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/systems.html',
                  context)


def add_system_group(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'systems/', {'systems': {'parent': pk, 'name': request.GET['name']}, 'isgroup': True})
        return redirect('/client/systems/' + (str(pk) if pk else ''))
    context = {}
    if pk is not None:
        context['parent'] = pk
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/systems_new.html', context)


def add_system_leaf(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'systems/', {'systems': {'parent': pk, 'name': request.GET['name']}, 'isgroup': False})
        return redirect('/client/systems/' + str(pk))
    context = {}
    if pk is not None:
        context['parent'] = pk
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/systems_new.html', context)


def positions_root(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    resp = rest(GET, 'positions/')
    return render(request, 'rest_client/positions_root.html',
                  {'positions': resp.json()['positions'], 'adminmode': request.session['is_admin'], 'userid': userid,
                   'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def positions(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'delete' in request.GET:
        rest(DELETE, 'positions/' + str(pk))
        return redirect('position_root')
    if 'save' in request.GET:
        rest(PUT, 'positions/' + str(pk) + '/', {'positions': {'name': request.GET['name']}})
    resp = rest(GET, 'positions/' + str(pk)).json()['positions'][0]
    return render(request, 'rest_client/positions.html',
                  {'name': resp['name'], 'adminmode': request.session['is_admin'], 'userid': userid,
                   'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def positions_add(request):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'positions/', {'positions': {'name': request.GET['name']}})
        return redirect('position_root')
    context = {}
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/positions_new.html', context)


def reset_password(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    status_code = None
    if 'reset' in request.GET:
        if request.GET['password1'] == request.GET['password2']:
            employee = rest(GET, 'structures/' + str(pk)).json()['structures'][0]
            password = hashlib.md5((request.GET['password1'] + employee['salt']).encode('utf-8')).hexdigest()
            response = rest(PUT, 'structures/' + str(pk) + '/', {'structures': {"hash": password}, 'isgroup': False})
            status_code = response.status_code
            if status_code == 200:
                return redirect('/client/structures/' + str(pk))
        else:
            status_code = -1
    return render(request, 'rest_client/reset_password.html', {'status': status_code, 'origin': pk, 'userid': userid,
                                                               'username':
                                                                   rest(GET, 'structures/' + str(userid)).json()[
                                                                       'structures'][0]['short_name']})


def employees_root(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    resp = rest(GET, 'employees/').json()['employees']
    employees = []
    for i in resp:
        employee = {'id': i['id'],
                    'name': i['full_name'],
                    'division_id': i['parent'],
                    'position_id': i['position'],
                    'admin': i['isadmin']
                    }
        if i['parent']:
            employee['division'] = rest(GET, 'structures/' + str(i['parent'])).json()['structures'][0]['name']
        if i['position']:
            employee['position'] = rest(GET, 'positions/' + str(i['position'])).json()['positions'][0]['name']
        employees.append(employee)
    return render(request, 'rest_client/employees_root.html', {'employees': employees, 'userid': userid, 'username':
        rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']})


def add_tasks_leaf(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'tasks/', {
            "tasks": {
                "name": request.GET['name'],
                "start": request.GET['start'],
                "end": request.GET['end'],
                "parent": pk,
                "creator": userid,
                "responsible": request.GET['responsible'],
                "system": request.GET['system'],
                "status": request.GET['status']
            },
            "isgroup": False
        })
        return redirect('/client/tasks/' + ("" if pk is None else str(pk)))
    context = {}
    systems = []
    for system in rest(GET, 'systemparts/').json()['systemparts']:
        systems.append({'id': system['id'], 'name': system['name']})
    context['systems'] = systems
    employees = []
    for employee in rest(GET, 'employees/').json()['employees']:
        employees.append({'id': employee['id'], 'short_name': employee['short_name']})
    context['employees'] = employees
    taskgroups = []
    for taskgroup in rest(GET, 'taskgroups/').json()['taskgroups']:
        taskgroups.append({'id': taskgroup['id'], 'name': taskgroup['name']})
    context['taskgroups'] = taskgroups
    context['parent'] = pk
    context['is_group'] = False
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/tasks_new.html', context)


def get_child(task, l):
    if 'child' in task:
        for i in task['child']:
            get_child(i, l)
    else:
        l.append({'id': task['id'], 'name': task['name'], 'start': task['start'], 'end': task['end'],
                  'status': task['status']})


def task_details(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    context = {}
    tasks = []
    r = rest(GET, 'tasks/' + str(pk)).json()['tasks'][0]
    get_child(r, tasks)
    context['tasks'] = tasks
    context['id'] = r['id']
    context['name'] = r['name']
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/task_detail.html', context)


def artefact(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    j = rest(GET, 'artefacts/' + str(pk)).json()['artefacts'][0]
    if 'save' in request.GET:
        rest(PUT, 'artefacts/' + str(pk) + '/', {'artefacts': {"title": request.GET['title'],
                                                               "description": request.GET['description']}})
        return redirect('/client/artefacts/' + str(pk))
    if 'delete' in request.GET:
        rest(DELETE, 'artefacts/' + str(pk))
        return redirect('/client/tasks/' + str(j['task']))
    context = {}
    context['title'] = j['title']
    context['description'] = j['description']
    context['parent_id'] = j['task']
    task = rest(GET, 'tasks/' + str(j['task'])).json()['tasks'][0]
    context['responsible_id'] = task['responsible']
    context['creator_id'] = task['creator']
    context['pk'] = pk
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/artefact.html', context)


def artefact_add(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'artefacts/',
             {'artefacts': {'title': request.GET['title'], 'description': request.GET['description'], 'task': pk}})
        return redirect('/client/tasks/'+ str(pk))
    context = {}
    context['pk'] = pk
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/artefact_new.html', context)
