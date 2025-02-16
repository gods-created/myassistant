from django.http import HttpResponseRedirect
from django.urls import resolve
from ipware import get_client_ip
from os import getenv

class SilkCustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        match = resolve(request.path)
        if match.app_name != 'silk':
            return response
        
        client_ip, *_ = get_client_ip(request)
        if client_ip != getenv('SUPERADMINISTRATOR_IP', ''):
            return HttpResponseRedirect(redirect_to='/admin/login/')
        
        return response
