import requests
from django.shortcuts import render

# Create your views here.
from requests.auth import HTTPBasicAuth
from .configuration import rest_password, rest_user, rest_service

def position(request):
    resp = requests.get(rest_service + 'positions/', auth=HTTPBasicAuth(rest_user, rest_password))
    return render(request, 'rest_client/positions.html', {'positions':resp.json()['positions']})