import requests
from django.shortcuts import render, redirect
# Create your views here.
from requests.auth import HTTPBasicAuth

from .configuration import rest_password, rest_user, rest_service


def check_login(session):
    if not ('login' in session and 'password' in session):
        return None
    login = session['login']
    password = session['password']
    resp = requests.get(rest_service + 'login/', auth=HTTPBasicAuth(rest_user, rest_password),
                        json={'login': login, 'password': password})
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
    resp = requests.get(rest_service + 'positions/', auth=HTTPBasicAuth(rest_user, rest_password))
    return render(request, 'rest_client/positions.html', {'positions': resp.json()['positions']})


def projects(request, pk=None):
    if not check_login(request.session):
        return redirect('login')
    if pk:
        tasks = requests.get(rest_service + 'tasks/' + str(pk), auth=HTTPBasicAuth(rest_user, rest_password))
    else:
        tasks = requests.get(rest_service + 'tasks/', auth=HTTPBasicAuth(rest_user, rest_password))
    j = tasks.json()
    formated = []
    for i in j['tasks']:
        task = {'name': i['name'], 'id': i['id']}
        creator = requests.get(rest_service + 'structures/' + str(i['creator']),
                               auth=HTTPBasicAuth(rest_user, rest_password)).json()['structures'][0]
        task['creator'] = creator['full_name']
        task['creator_id'] = creator['id']
        responsible = requests.get(rest_service + 'structures/' + str(i['responsible']),
                                   auth=HTTPBasicAuth(rest_user, rest_password)).json()['structures'][0]
        task['responsible'] = responsible['full_name']
        task['responsible_id'] = responsible['id']
        formated.append(task)
    return render(request, 'rest_client/tasks_root.html', {'tasks': formated})


def login(request):
    if 'login' in request.session and 'password' in request.session:
        if check_login(request.session):
            return redirect('tasks')
        else:
            del request.session['login']
            del request.session['password']
    try:
        request.session['login'] = request.GET['login']
        request.session['password'] = request.GET['password']
        if check_login(request.session):
            return redirect('tasks')
        else:
            return render(request, 'rest_client/login.html', {'failed': True})
    except KeyError:
        pass
    return render(request, 'rest_client/login.html', {'failed': False})


def logout(request):
    del request.session['login']
    del request.session['password']
    return redirect('login')