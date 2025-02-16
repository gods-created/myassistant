from django.urls import path
from .views import login_page, dashboard_page, login_process, create_application
from django.contrib.auth.views import LogoutView

app_name = 'admin'

urlpatterns = [
    path('login/', login_page, name='login_page'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('logout_process/', LogoutView.as_view(next_page='/admin/login/'), name='logout_process'),
    path('login_process/', login_process, name='login_process'),
    path('create_application/', create_application, name='create_application')
]