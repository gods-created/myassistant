from django.forms import (
    Form,
    EmailField,
    EmailInput,
    CharField,
    PasswordInput,
    ValidationError
)

from .models import Admin
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import authenticate, login as auth_login

class LoginForm(Form):
    email = EmailField(
        label='Email',
        required=True,
        max_length=250,
        error_messages={
            'required': '\'email\' field is required',
            'max_length': '\'email\' field has to have max. 250 characters',
        },
        widget=EmailInput(
            attrs={
                'type': 'email',
                'class': 'form-control mb-3'
            }
        )
    )

    password = CharField(
        label='Password',
        required=True,
        max_length=250,
        min_length=10,
        error_messages={
            'required': '\'password\' field is required',
            'max_length': '\'password\' field has to have max. 250 characters',
            'min_length': '\'password\' field has to have min. 10 characters',
        },
        widget=PasswordInput(
            attrs={
                'type': 'password',
                'class': 'form-control mb-3'
            }
        )
    )

    def clean(self):
        email, password = self.cleaned_data.get('email'), self.cleaned_data.get('password')
        if not Admin.objects.validate_admin(email, password):
            raise ValidationError('Invalid email or password')
        
    def login(self, request) -> bool:
        email, password = self.cleaned_data.get('email'), self.cleaned_data.get('password')
        user = authenticate(request, email=email, password=password)
        auth_login(request, user)
        return True