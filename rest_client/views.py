import requests
from django.shortcuts import render

# Create your views here.
from requests.auth import HTTPBasicAuth


def vote(request):
    resp = requests.get('https://www.nbrb.by/api/exrates/currencies', auth=HTTPBasicAuth('rest_client', 'qwop'))
    return render(request, 'positions.html')