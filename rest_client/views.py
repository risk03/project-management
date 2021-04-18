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
    login_1 = session['login']
    password = session['password']
    resp = rest(GET, 'login/', {'login': login_1, 'password': password})
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
    j = rest(GET, 'tasks/').json()
    formated = []
    for i in j['tasks']:
        tasks_common(i, formated)
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
    systems_1 = []
    for system in rest(GET, 'systemparts/').json()['systemparts']:
        systems_1.append({'id': system['id'], 'name': system['name']})
    context['is_group'] = True
    context['systems'] = systems_1
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/tasks_new.html', context)


def tasks(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    j = rest(GET, 'tasks/' + str(pk)).json()['tasks'][0]
    project_id = j['project']
    if 'delete' in request.GET:
        rest(DELETE, 'tasks/' + str(pk))
        return redirect('/client/tasks/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        fields = ["name", "start", "end", "parent", "responsible", "system", "status", "real_early_start",
                  "real_late_start", "real_early_end", "real_late_end"]
        save = {}
        for field in fields:
            if field in request.GET:
                save[field] = request.GET[field] if request.GET[field] != '' else None
        save["duration"] = "{} {}:00:00".format(request.GET['durationD'] if 'durationD' in request.GET else '0',
                                                request.GET['durationH'] if 'durationH' in request.GET else '0')
        save["next"] = []
        for a in request.GET.getlist('next'):
            save["next"].append(int(a))
        save["prev"] = []
        for a in request.GET.getlist('prev'):
            save["prev"].append(int(a))
        print(save)
        res = rest(PUT, 'tasks/' + str(pk) + '/', {
            "tasks": save,
            "isgroup": 'child' in j
        })
        print(res)
        rest(GET, 'tasks/gettime/' + str(j['project']) + '/')
        return redirect('/client/tasks/' + str(pk))
    context = {'task': j}
    if 'child' in j:
        tasks_1 = []
        for i in j['child']:
            task = tasks_common(i, tasks_1)
            task['is_group'] = True if 'child' in i else False
        context['tasks'] = tasks_1
        context['is_group'] = True
    else:
        context['is_group'] = False
        context['status'] = j['status']
        context['start'] = (datetime.datetime.strptime(j['start'], '%Y-%m-%dT%H:%M:%SZ').replace(
            microsecond=0).strftime('%Y-%m-%dT%H:%M') if j['start'] else None)
        context['end'] = (datetime.datetime.strptime(j['end'], '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0).strftime(
            '%Y-%m-%dT%H:%M') if j['end'] else None)
        systems_1 = []
        for system in rest(GET, 'systemparts/').json()['systemparts']:
            systems_1.append({'id': system['id'], 'name': system['name']})
        context['systems'] = systems_1
        context['system_id'] = j['system']
        artefacts = []
        for i in rest(GET, 'artefacts/of/' + str(pk)).json()['artefacts']:
            artefacts.append({'id': i['id'], 'title': i['title']})
        context['artefacts'] = artefacts
        context['nexts'] = []
        context['prevs'] = []
        resp = rest(GET, 'project_leaves/' + str(project_id))
        resp = resp.json()
        for t in resp['tasks']:
            context['nexts'].append({'id': t['id'], 'name': t['id']})
            context['prevs'].append({'id': t['id'], 'name': t['id']})
        for i in context['nexts']:
            if i['id'] in j['next']:
                i['selected'] = 1
        for i in context['prevs']:
            if i['id'] in j['prev']:
                i['selected'] = 1
        duration = j['duration']
        context['durationD'] = duration[:duration.index(' ')]
        context['durationH'] = duration[duration.index(' ') + 1:duration.index(':')]
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


def tasks_common(i, tasks_1):
    task = {'name': i['name'], 'id': i['id']}
    creator = rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]
    task['creator'] = creator['short_name']
    task['creator_id'] = creator['id']
    responsible = rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0]
    task['responsible'] = responsible['short_name']
    task['responsible_id'] = responsible['id']
    tasks_1.append(task)
    return task


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
        user_id = check_login(request.session)
        if user_id:
            request.session['is_admin'] = rest(GET, 'structures/' + str(user_id)).json()['structures'][0]['isadmin']
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


# noinspection PyUnusedLocal
def structures_root(request, pk=None):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks_1 = rest(GET, 'structures/')
    j = tasks_1.json()
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
    tasks_1 = rest(GET, 'structures/' + str(pk))
    j = tasks_1.json()['structures'][0]
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
            structures_1 = {'id': i['id']}
            if 'child' in i:
                structures_1['is_group'] = True
                structures_1['name'] = i['name']
            else:
                structures_1['is_group'] = False
                structures_1['name'] = i['full_name']
            formated.append(structures_1)
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
        positions_1 = []
        for i in rest(GET, 'positions/').json()['positions']:
            positions_1.append({'id': i['id'], 'name': i['name']})
        context['positions'] = positions_1
        parents = []
        for i in rest(GET, 'divisions/').json()['divisions']:
            parents.append({'id': i['id'], 'name': i['name']})
        context['parents'] = parents
        tasks_1 = []
        for i in rest(GET, 'tasks/of/struct/' + str(pk)).json()['tasks']:
            tasks_1.append({'id': i['id'], 'name': i['name'], 'creator_id': i['creator'], 'status': i['status'],
                            'creator': rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0][
                                'short_name'],
                            'start': (datetime.datetime.strptime(i['start'], '%Y-%m-%dT%H:%M:%SZ') if i[
                                'start'] else datetime.datetime.now())
                            })
        context['tasks'] = sorted(tasks_1, key=lambda x: x['start'], reverse=True)
        for i in context['tasks']:
            i['start'] = i['start'].strftime('%Y-%m-%dT%H:%M')
    context['adminmode'] = request.session['is_admin']
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    context['pk'] = pk
    return render(request, 'rest_client/structures.html',
                  context)


# noinspection PyUnusedLocal
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
    positions_1 = []
    for position in rest(GET, 'positions/').json()['positions']:
        positions_1.append({'id': str(position['id']), 'name': position['name']})
    positions_1.sort(key=lambda x: x['name'])
    context = {'divisions': divisions, 'parent': str(pk), 'positions': positions_1, 'is_group': False}
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
    context = {'parent': str(pk), 'is_group': True, 'userid': userid,
               'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']}
    return render(request, 'rest_client/structures_new.html', context)


def systems_root(request):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    tasks_1 = rest(GET, 'systems/')
    j = tasks_1.json()
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
    tasks_1 = rest(GET, 'systems/' + str(pk))
    j = tasks_1.json()['systems'][0]
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
            systems_1 = {'id': i['id'], 'name': i['name']}
            if 'child' in i:
                systems_1['is_group'] = True
            else:
                systems_1['is_group'] = False
            formated.append(systems_1)
    else:
        is_group = False
    context = {'systems': formated, 'parent_id': ('' if j['parent'] is None else j['parent']),
               'name': (j['name'] if 'name' in j else j['full_name']), 'is_group': is_group, 'id': j['id'], }
    if not is_group:
        parents = []
        for i in rest(GET, 'systemgroups/').json()['systemgroups']:
            parents.append({'id': i['id'], 'name': i['name']})
        context['parents'] = parents
        tasks_1 = []
        for i in rest(GET, 'tasks/of/sys/' + str(pk)).json()['tasks']:
            tasks_1.append({'id': i['id'], 'name': i['name'], 'creator_id': i['creator'], 'status': i['status'],
                            'creator': rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0][
                                'short_name'],
                            'responsible_id': i['responsible'],
                            'responsible': rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0][
                                'short_name'],
                            'start': datetime.datetime.strptime(i['start'], '%Y-%m-%dT%H:%M:%SZ')})
        context['tasks'] = sorted(tasks_1, key=lambda x: x['start'], reverse=True)
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
    return add_system_common(pk, request, userid)


def add_system_common(pk, request, userid):
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
    add_system_common(pk, request, userid)


# noinspection PyUnusedLocal
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
    context = {'userid': userid,
               'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']}
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


# noinspection PyUnusedLocal
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
        save = {
            "tasks": {
                "name": request.GET['name'],
                "start": request.GET["start"] if request.GET["start"] != '' else None,
                "end": request.GET["end"] if request.GET["end"] != '' else None,
                "parent": pk,
                "creator": userid,
                "responsible": int(request.GET['responsible']),
                "system": int(request.GET['system']),
                "status": request.GET['status'],
                "real_early_start": request.GET["real_early_start"] if request.GET["real_early_start"] != '' else None,
                "real_late_start": request.GET["real_late_start"] if request.GET["real_late_start"] != '' else None,
                "real_early_end": request.GET["real_early_end"] if request.GET["real_early_end"] != '' else None,
                "real_late_end": request.GET["real_late_end"] if request.GET["real_late_start"] != '' else None,
                "duration": "{} {}:00:00".format(request.GET['durationD'] if 'durationD' in request.GET else '0',
                                                request.GET['durationH'] if 'durationH' in request.GET else '0')
            },
            "isgroup": False
        }
        res = rest(POST, 'tasks/', save)
        project = rest(GET, 'tasks/' + str(request.GET['parent'])).json()['tasks'][0]['project']
        rest(GET, 'tasks/gettime/' + str(project) + '/')
        return redirect('/client/tasks/' + ("" if pk is None else str(pk)))
    context = {}
    systems_1 = []
    for system in rest(GET, 'systemparts/').json()['systemparts']:
        systems_1.append({'id': system['id'], 'name': system['name']})
    context['systems'] = systems_1
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


def get_child(task, out_list):
    if 'child' in task:
        for i in task['child']:
            get_child(i, out_list)
    else:
        out_list.append(task)
        if not task['start']:
            out_list = [x for x in [task['real_early_start'], task['prop_early_start']] if x is not None]
            task['start'] = max(out_list) if out_list else None
        if not task['end']:
            out_list = [x for x in [task['real_early_end'], task['prop_early_end']] if x is not None]
            task['end'] = max(out_list) if out_list else None
        task['prev_list'] = task['prev']
        task['prev'] = ','.join([str(x) for x in task['prev']])
        task['next_list'] = task['next']
        if task['tlj'] and task['tej']:
            reserve = (datetime.datetime.strptime(task['tlj'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0) - datetime.datetime.strptime(task['tej'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0))
            task['reserve'] = reserve.days
        task['is_critical'] = task['tlj'] == task['tej']


def task_details(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    context = {}
    tasks_1 = []
    r = rest(GET, 'tasks/' + str(pk)).json()['tasks'][0]
    get_child(r, tasks_1)
    start = None
    end = None
    for task in [x for x in tasks_1 if not x['prev']]:
        if not start or datetime.datetime.strptime(task['prop_early_start'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0) < datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0):
            start = task['prop_early_start']
    context['start'] = str(start)
    for task in [x for x in tasks_1 if not x['next']]:
        if not end or datetime.datetime.strptime(task['prop_late_end'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0) > datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0):
            end = task['prop_late_end']
    context['end'] = str(end)
    context['taskslen'] = max([x['id'] for x in tasks_1]) + 1
    for i in range(len(tasks_1)):
        tasks_1[i]['local_id'] = i + 1
    context['last_local_id'] = len(tasks_1) + 1
    context['tasks'] = tasks_1
    context['id'] = r['id']
    context['name'] = r['name']
    context['is_group'] = 'child' in r
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
    context = {'title': j['title'], 'description': j['description'], 'parent_id': j['task']}
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
        return redirect('/client/tasks/' + str(pk))
    context = {'pk': pk, 'userid': userid,
               'username': rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']}
    return render(request, 'rest_client/artefact_new.html', context)

def test(request, pk):
    userid = check_login(request.session)
    if not userid:
        return redirect('login')
    context = {}
    tasks_1 = []
    r = rest(GET, 'tasks/' + str(pk)).json()['tasks'][0]
    get_child(r, tasks_1)
    start = None
    end = None
    for task in [x for x in tasks_1 if not x['prev']]:
        if not start or datetime.datetime.strptime(task['prop_early_start'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0) < datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0):
            start = task['prop_early_start']
    context['start'] = str(start)
    for task in [x for x in tasks_1 if not x['next']]:
        if not end or datetime.datetime.strptime(task['prop_late_end'], '%Y-%m-%dT%H:%M:%SZ').replace(
                microsecond=0) > datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0):
            end = task['prop_late_end']
    context['end'] = str(end)
    context['taskslen'] = max([x['id'] for x in tasks_1]) + 1
    for i in range(len(tasks_1)):
        tasks_1[i]['local_id'] = i + 1
    context['last_local_id'] = len(tasks_1) + 1
    context['tasks'] = tasks_1
    context['id'] = r['id']
    context['name'] = r['name']
    context['is_group'] = 'child' in r
    context['userid'] = userid
    context['username'] = rest(GET, 'structures/' + str(userid)).json()['structures'][0]['short_name']
    return render(request, 'rest_client/test.html', context)