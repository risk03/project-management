import requests
from django.shortcuts import render, redirect
# Create your views here.
from requests.auth import HTTPBasicAuth

from .configuration import rest_password, rest_user, rest_service

GET = 'get'
POST = 'post'


def rest(method, url, json=None):
    return requests.request(method, rest_service + url, auth=HTTPBasicAuth(rest_user, rest_password), json=json)


def check_login(session):
    if not ('login' in session and 'password' in session):
        return None
    login = session['login']
    password = session['password']
    resp = rest('GET', 'login/', {'login': login, 'password': password})
    if resp.status_code != 200:
        return None
    j = resp.json()
    if 'id' in j:
        return j['id']
    else:
        return None


def position(request, pk=None):
    if not check_login(request.session):
        return redirect('login')
    resp = rest(GET, 'positions/')
    return render(request, 'rest_client/positions.html', {'positions': resp.json()['positions']})


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
        rest('DELETE', 'tasks/' + str(pk))
        return redirect('/client/tasks/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        rest('put', 'tasks/' + str(pk) + '/', {
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
        rest('DELETE', 'structures/' + str(pk))
        return redirect('/client/structures/' + ('' if j['parent'] is None else str(j['parent'])))
    if 'save' in request.GET:
        rest('put', 'structures/' + str(pk) + '/', {
            "structures": {
                "name": request.GET['name'],
                "responsible": request.GET['responsible']
            },
            "isgroup": True
        })
        return redirect('/client/structures/' + str(pk))
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
        context['position'] = rest('get', 'positions/' + str(j['position'])).json()['positions'][0]['name']
        context['parent'] = rest('get', 'structures/' + str(j['parent'])).json()['structures'][0]['name']
        positions = []
        for i in rest('get', 'positions/').json()['positions']:
            positions.append({'id': i['id'], 'name': i['name']})
        context['positions'] = positions
        parents = []
        for i in rest('get', 'divisions/').json()['divisions']:
            parents.append({'id': i['id'], 'name': i['name']})
        context['parents'] = parents
    return render(request, 'rest_client/structures.html',
                  context)


def add_structure(request):
    return None


def add_employee(request):
    return None
