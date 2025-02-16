from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect

def if_auth(func):
    def wrapper(*args, **kwargs):
        request, *_ = args
        session_key = request.COOKIES.get('sessionid', '')
        if Session.objects.filter(session_key=session_key).exists():
            return HttpResponseRedirect(redirect_to='/admin/dashboard/')
        
        return func(*args, **kwargs)
    
    return wrapper