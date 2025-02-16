from django.shortcuts import render
from .forms import LoginForm
from django.http import HttpResponseRedirect
from json import loads, dumps
from django.contrib.auth.decorators import login_required
from decorators import if_auth
from oauth2_provider.models import Application

@if_auth
def login_page(request) -> render:
    context = {
        'form': LoginForm
    }

    if request.COOKIES.get('errors'):
        errors = loads(request.COOKIES.get('errors'))
        context['errors'] = [errors[key][0]['message'] for key in errors.keys()]

    response = render(
        request=request,
        template_name='login_page.html',
        context=context
    )

    response.delete_cookie('errors')
    return response

@if_auth
def login_process(request) -> HttpResponseRedirect:
    post_data = request.POST
    form = LoginForm(post_data)
    if not form.is_valid():
        errors = dumps(form.errors.get_json_data())
        response = HttpResponseRedirect(redirect_to='/admin/login/')
        response.set_cookie('errors', errors, max_age=15)
        return response
    
    form.login(request)
    return HttpResponseRedirect(redirect_to='/admin/dashboard/')

@login_required(login_url='/admin/login/')
def dashboard_page(request) -> render:
    user = request.user
    application = Application.objects.filter(user=user).only(
        'client_id',
        'client_secret'
    ).first()

    return render(
        request=request,
        template_name='dashboard_page.html',
        context={
            'user': user,
            'application': application
        }
    )

@login_required(login_url='/admin/login/')
def create_application(request) -> HttpResponseRedirect:
    user = request.user
    Application.objects.get_or_create(
        user=user, 
        authorization_grant_type='client-credentials',
        client_type='confidential',
        hash_client_secret=False
    )

    return HttpResponseRedirect(redirect_to='/admin/dashboard/')