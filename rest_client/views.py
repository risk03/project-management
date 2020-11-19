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
    return render(request, 'rest_client/projects.html', {'tasks': formated})


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


def add_project(request):
    user_id = check_login(request.session)
    if not user_id:
        return redirect('login')
    if 'add' in request.GET:
        rest(POST, 'tasks/', {
            "tasks": {
                "name": request.GET['name'],
                "parent": None,
                "creator": user_id,
                "responsible": request.GET['responsible']
            },
            "isgroup": True
        })
        return redirect('projects')
    employees = rest(GET, 'employees/').json()['employees']
    employees_list = []
    for employee in employees:
        employees_list.append({'id': employee['id'], 'short_name': employee['short_name']})
    return render(request, 'rest_client/projects_new.html', {'employees': employees_list})


def tasks(request, pk):
    if not check_login(request.session):
        return redirect('login')

    tasks = rest(GET, 'tasks/' + str(pk))
    j = tasks.json()['tasks'][0]
    if 'delete' in request.GET:
        rest('DELETE', 'tasks/' + str(pk))
        return redirect('/client/tasks/' + ('' if j['parent'] is None else j['parent']))
    formated = []
    if 'child' in j:
        for i in j['child']:
            task = {'name': i['name'], 'id': i['id']}
            creator = rest(GET, 'structures/' + str(i['creator'])).json()['structures'][0]
            task['creator'] = creator['short_name']
            task['creator_id'] = creator['id']
            responsible = rest(GET, 'structures/' + str(i['responsible'])).json()['structures'][0]
            task['responsible'] = responsible['short_name']
            task['responsible_id'] = responsible['id']
            formated.append(task)
    return render(request, 'rest_client/tasks.html',
                  {'tasks': formated, 'parent': ('' if j['parent'] is None else j['parent'])})
