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
    if not check_login(request.session):
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
    return render(request, 'rest_client/tasks_root.html', {'tasks': formated})


def add_tasks_group(request, pk=None):
    user_id = check_login(request.session)
    if not user_id:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'tasks/', {
            "tasks": {
                "name": request.GET['name'],
                "parent": None if request.GET['parent'] == 'None' else request.GET['parent'],
                "creator": user_id,
                "responsible": request.GET['responsible']
            },
            "isgroup": True
        })
        return redirect('/client/tasks/' + ("" if pk is None else pk))
    employees = rest(GET, 'employees/').json()['employees']
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee['id'], 'short_name': employee['short_name']})
    return render(request, 'rest_client/tasks_new.html', {'employees': employees_list, 'parent': pk})


def tasks(request, pk):
    if not check_login(request.session):
        return redirect('login')
    tasks = rest(GET, 'tasks/' + str(pk))
    j = tasks.json()['tasks'][0]
    if 'delete' in request.GET:
        rest(DELETE, 'tasks/' + str(pk))
        return redirect('/client/tasks/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        rest(PUT, 'tasks/' + str(pk) + '/', {
            "tasks": {
                "name": request.GET['name'],
                "responsible": request.GET['responsible']
            },
            "isgroup": True
        })
        return redirect('/client/tasks/' + str(pk))
    formated = []
    if 'child' in j:
        is_group = True
        for i in j['child']:
            task = {'name': i['name'], 'id': i['id']}
            creator = rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]
            task['creator'] = creator['short_name']
            task['creator_id'] = creator['id']
            responsible = rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0]
            task['responsible'] = responsible['short_name']
            task['responsible_id'] = responsible['id']
            formated.append(task)
            task['is_group'] = True if 'child' in i else False
    else:
        is_group = False
    employees = rest(GET, 'employees/').json()['employees']
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee['id'], 'short_name': employee['short_name']})
    return render(request, 'rest_client/tasks.html',
                  {'tasks': formated, 'parent': ('' if j['parent'] is None else j['parent']),
                   'employees': employees_list, 'name': j['name'], 'responsible': j['responsible'],
                   'is_group': is_group, 'id': j['id']})


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
        if check_login(request.session):
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
    if not check_login(request.session):
        return redirect('login')
    tasks = rest(GET, 'structures/')
    j = tasks.json()
    formated = []
    for i in j['structures']:
        task = {'name': i['name'], 'id': i['id']}
        formated.append(task)
    return render(request, 'rest_client/structures_root.html', {'structures': formated})


def structures(request, pk=None):
    if not check_login(request.session):
        return redirect('login')
    tasks = rest(GET, 'structures/' + str(pk))
    j = tasks.json()['structures'][0]
    if 'delete' in request.GET:
        rest(DELETE, 'structures/' + str(pk))
        return redirect('/client/structures/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        rest(PUT, 'structures/' + str(pk) + '/', {
            "structures": {
                "full_name": request.GET['name'],
                "short_name": request.GET['short_name'],
                "login": request.GET['login'],
                "isadmin": 'isadmin' in request.GET,
                "parent": request.GET['parent'],
                "position": request.GET['position']
            },
            "isgroup": 'child' in j
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
    return render(request, 'rest_client/structures.html',
                  context)


def add_structure_leaf(request, pk):
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
    return render(request, 'rest_client/structures_new.html', context)


def add_structure(request, pk):
    if 'add' in request.GET:
        rest(POST, 'structures/', {'structures': {"name": request.GET['name'],
                                                  "parent": pk, }, 'isgroup': True})
        return redirect('/client/structures/' + str(pk))
    context = {'parent': str(pk), 'is_group': True}
    return render(request, 'rest_client/structures_new.html', context)


def systems_root(request):
    if not check_login(request.session):
        return redirect('login')
    tasks = rest(GET, 'systems/')
    j = tasks.json()
    formated = []
    for i in j['systems']:
        task = {'name': i['name'], 'id': i['id']}
        formated.append(task)
    return render(request, 'rest_client/systems_root.html', {'systems': formated})


def systems(request, pk=None):
    if not check_login(request.session):
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
    return render(request, 'rest_client/systems.html',
                  context)


def add_system_group(request, pk=None):
    if 'add' in request.GET:
        rest(POST, 'systems/', {'systems': {'parent': pk, 'name': request.GET['name']}, 'isgroup': True})
        return redirect('/client/systems/' + str(pk))
    context = {}
    if pk is not None:
        context['parent'] = pk
    return render(request, 'rest_client/systems_new.html', context)


def add_system_leaf(request, pk):
    if 'add' in request.GET:
        rest(POST, 'systems/', {'systems': {'parent': pk, 'name': request.GET['name']}, 'isgroup': False})
        return redirect('/client/systems/' + str(pk))
    context = {}
    if pk is not None:
        context['parent'] = pk
    return render(request, 'rest_client/systems_new.html', context)


def positions_root(request, pk=None):
    if not check_login(request.session):
        return redirect('login')
    resp = rest(GET, 'positions/')
    return render(request, 'rest_client/positions_root.html', {'positions': resp.json()['positions']})


def positions(request, pk):
    if not check_login(request.session):
        return redirect('login')
    if 'delete' in request.GET:
        rest(DELETE, 'positions/' + str(pk))
        return redirect('position_root')
    if 'save' in request.GET:
        rest(PUT, 'positions/' + str(pk) + '/', {'positions': {'name': request.GET['name']}})
    resp = rest(GET, 'positions/' + str(pk)).json()['positions'][0]
    return render(request, 'rest_client/positions.html', {'name': resp['name']})


def positions_add(request):
    if 'add' in request.GET:
        rest(POST, 'positions/', {'positions': {'name': request.GET['name']}})
        return redirect('position_root')
    return render(request, 'rest_client/positions_new.html')


def reset_password(request, pk):
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
    return render(request, 'rest_client/reset_password.html', {'status': status_code, 'origin': pk})


def employees_root(request, pk=None):
    if not check_login(request.session):
        return redirect('login')
    resp = rest(GET, 'employees/').json()['employees']
    employees = []
    for i in resp:
        employee = {'id': i['id'],
                    'name': i['full_name'],
                    'division_id': i['parent'],
                    'position_id': i['position'],
                    }
        if i['parent']:
            employee['division'] = rest(GET, 'structures/' + str(i['parent'])).json()['structures'][0]['name']
        if i['position']:
            employee['position'] = rest(GET, 'positions/' + str(i['position'])).json()['positions'][0]['name']
        employees.append(employee)
    return render(request, 'rest_client/employees_root.html', {'employees': employees})
