from celery import shared_task
from django.core.mail import send_mail
from os import getenv

EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')

@shared_task(bind=True, queue='low_priority')
def language_model_train_response_task(self, email: str, message: str):
    try:
        send_mail(
            'Model training error',
            'Hello! Unfortunately, ' \
            f'training your model ended up in error: \'{message}\'. ' \
            'Please, communicate with administrator if error not connect with data validation. ' \
            f'Administartor email: {EMAIL_HOST_USER}',
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    except Exception as e:
        return self.retry(exc=e, countdown=5)

@shared_task(bind=True, queue='high_priority')
def signup_task(self, email: str, fullname: str):
    try:
        send_mail(
            'New user from MyAssistant',
            'Fullname: {}. Email: {}.'.format(fullname, email),
            EMAIL_HOST_USER,
            [EMAIL_HOST_USER],
            fail_silently=False,
        )

    except Exception as e:
        return self.retry(exc=e, countdown=5)