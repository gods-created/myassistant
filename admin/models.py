from django.db.models import (
    EmailField,
    CharField,
    Index
)

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from .managers import AdminManager

class Admin(AbstractUser):
    groups=None 
    user_permissions=None
    username=None
    first_name=None
    last_name=None
    last_login=None

    REQUIRED_FIELDS = []
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    email = EmailField(
        null=False,
        blank=False,
        max_length=250,
        unique=True
    )

    password = CharField(
        null=False,
        blank=False,
        max_length=250,
    )

    fullname = CharField(
        null=False,
        blank=True,
        max_length=250,
        default=''
    )

    calculate_model = CharField(
        null=True,
        blank=False,
        max_length=250,
        default=None
    )

    lm_model = CharField(
        null=True,
        blank=False,
        max_length=250,
        default=None
    )

    objects = AdminManager()

    class Meta:
        app_label='admin'
        db_table='admins'
        ordering=['id', 'email', 'date_joined', 'is_active', 'fullname']
        indexes=[
            Index(fields=['email', 'password'])
        ]

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        return super().save(*args, **kwargs)
