from rest_framework.serializers import (
    Serializer,
    CharField,
    ValidationError,
    IntegerField,
    SerializerMethodField,
    ListField,
    DictField,
    EmailField,
    ChoiceField,
)

from django.db.models import Q
from oauth2_provider.models import Application, AccessToken
from django.utils.timezone import now, timedelta
from .services import (
    data_clustering,
    calculate_model_fit,
    calculate_model_predict,
    RegressionTypes,
    language_model_generate,
    language_model_train
)
from admin.models import Admin
from typing import Union
from .celery import signup_task
from threading import Thread
import secrets

class LMSerializer(Serializer):
    email = EmailField(
        required=True,
        max_length=250,
        allow_blank=False,
        error_messages={
            'allow_blank': '\'email\' field can\'t to be empty',
            'required': '\'email\' field is required',
            'max_length': '\'email\' field has max 250 characters',
        }
    )

    data = ListField(
        required=False,
        min_length=5,
        child=DictField(),
        error_messages={
            'required': '\'data\' field is required',
            'min_length': 'The min. item count in \'data\' is 5',
        }
    )

    income = CharField(
        required=False
    )

    def validate(self, attrs):
        email, data = attrs.get('email'), attrs.get('data')
        if not Admin.objects.filter(email=email).exists():
            raise ValidationError(detail={'email': ['Customer with so email doesn\'t exist']})
        
        return attrs 
    
    def lm_train(self, validated_data) -> None:
        data = validated_data.get('data')
        if not data:
            raise ValidationError(detail={'data': ['\'data\' field is required']})

        data = [item for item in data if {'income', 'outcome'}.issubset(item)]
        if not data:
            raise ValidationError(detail={'data': ['All items in \'data\' is invalid']})
        
        data = [item for item in data if item['income'] and item['outcome']]

        if len(data) < 5:
            raise ValidationError(detail={'data': ['The min. item count in \'data\' is 5']})

        th = Thread(target=language_model_train, args=(validated_data.get('email'), data, ), daemon=False)
        th.start()

        return None
    
    def lm_generate(self, validated_data) -> tuple:
        income = validated_data.get('income')
        if not income:
            raise ValidationError(detail={'income': ['\'income\' field is required']})
        
        return language_model_generate(validated_data.get('email'), income)

class SignupSerializer(Serializer):
    email = EmailField(
        required=True,
        max_length=250,
        allow_blank=False,
        error_messages={
            'allow_blank': '\'email\' field can\'t to be empty',
            'required': '\'email\' field is required',
            'max_length': '\'email\' field has max 250 characters',
        }
    )

    fullname = CharField(
        required=True,
        max_length=250,
        allow_blank=False,
        error_messages={
            'allow_blank': '\'fullname\' field can\'t to be empty',
            'required': '\'fullname\' field is required',
            'max_length': '\'fullname\' field has max 250 characters',
        }
    )

    def validate_email(self, email):
        if Admin.objects.filter(email=email).exists():
            raise ValidationError(detail='Customer with so email already exists')

        return email
    
    def signup(self, validated_data):
        email, fullname = validated_data.get('email'), validated_data.get('fullname', '')
        signup_task.apply_async(
            (email, fullname),
            queue='high_priority'
        )

        return {
            'status': 'success',
            'message': 'Application for registration is accepted. Wait for notification to the e-mail address you specified.'
        }

class CalculateSerializer(Serializer):
    email = EmailField(
        required=True,
        max_length=250,
        error_messages={
            'required': '\'email\' field is required',
            'max_length': '\'email\' field has max 250 characters',
        }
    )

    model_type = ChoiceField(
        required=False,
        choices=[(item.name, item.value) for item in RegressionTypes]
    )

    data = ListField(
        required=True,
        child=ListField(),
        min_length=5,
        error_messages={
            'required': '\'data\' field is required',
            'min_length': 'The min. item count in \'data\' is 5',
        }
    )

    def calculate_predict(self, validated_data) -> Union[str, list]:
        calculate_model_predict_response = calculate_model_predict(**validated_data)
        return calculate_model_predict_response

    def calculate_fit(self, validated_data) -> tuple:
        calculate_model_fit_response = calculate_model_fit(**validated_data)
        return calculate_model_fit_response

class ClusteringSerializer(Serializer):
    data = ListField(
        required=True,
        child=DictField(),
        min_length=5,
        error_messages={
            'required': '\'data\' field is required',
            'min_length': 'The min. item count in \'data\' is 5',
        }
    )

    n_clusters = IntegerField(
        required=False,
        min_value=2,
        error_messages={
            'min_value': 'The min. value for \'n_clusters\' is 2',
        }
    )
    
    def clustering(self, validated_data) -> Union[str, list]:
        response = data_clustering(**validated_data)
        return response

class AuthSerializer(Serializer):
    client_id = CharField(
        required=True,
        error_messages={
            'required': '\'client_id\' field is required'
        }
    )

    client_secret = CharField(
        required=True,
        error_messages={
            'required': '\'client_secret\' field is required',
        }
    )

    access_token = SerializerMethodField()

    def get_access_token(self):
        pass

    def validate(self, attrs):
        client_id, client_secret = attrs.get('client_id'), attrs.get('client_secret')
        application = Application.objects.filter(Q(client_id=client_id) & Q(client_secret=client_secret)).first()
        if not application:
            raise ValidationError(detail={'fields': ['Invalid \'client_id\' or \'client_secret\'']})
        
        access_token = AccessToken.objects.create(
            token=secrets.token_urlsafe(43),
            user=application.user, 
            application=application, 
            scope='read write',
            expires=now() + timedelta(days=7)
        )

        self.access_token = access_token
        return attrs 
    
    def auth(self) -> tuple:
        return (self.access_token.token, self.access_token.expires)
