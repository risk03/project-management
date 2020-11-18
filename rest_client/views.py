import requests
from django.shortcuts import render, redirect

# Create your views here.
from requests.auth import HTTPBasicAuth
from .configuration import rest_password, rest_user, rest_service

def position(request, pk=None):
    resp = requests.get(rest_service + 'positions/', auth=HTTPBasicAuth(rest_user, rest_password))
    return render(request, 'rest_client/positions.html', {'positions':resp.json()['positions']})

def projects(request, pk=None):
    if pk:
        tasks = requests.get(rest_service + 'tasks/' + str(pk), auth=HTTPBasicAuth(rest_user, rest_password))
    else:
        tasks = requests.get(rest_service + 'tasks/', auth=HTTPBasicAuth(rest_user, rest_password))
    j = tasks.json()
    formated = []
    for i in j['tasks']:
        task = {'name': i['name'], 'id': i['id']}
        creator = requests.get(rest_service+'structures/'+ str(i['creator']),  auth=HTTPBasicAuth(rest_user, rest_password)).json()['structures'][0]
        task['creator'] = creator['full_name']
        task['creator_id'] = creator['id']
        responsible = requests.get(rest_service+'structures/'+ str(i['responsible']),  auth=HTTPBasicAuth(rest_user, rest_password)).json()['structures'][0]
        task['responsible'] = responsible['full_name']
        task['responsible_id'] = responsible['id']
        formated.append(task)
    return render(request, 'rest_client/tasks_root.html', {'tasks':formated})

def login(request):
    if "user" in request.session:
        return redirect('tasks')
    try:
        log = request.GET['login']
        pas = request.GET['password']
        request.session["user"] = log
        return render(request, 'rest_client/login.html')
    except KeyError:
        return render(request, 'rest_client/login.html')