from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import OAuth2CustomAuthentication
from .serializers import (
    AuthSerializer,
    ClusteringSerializer,
    CalculateSerializer,
    SignupSerializer,
    LMSerializer,
)
from django.http import FileResponse, HttpResponse
from os.path import exists
from django.conf import settings
from json import loads

def docs(request) -> FileResponse:
    dir = '{}/static/assets/files/myassistant_api.docx'.format(settings.BASE_DIR)
    if exists(dir):
        return FileResponse(open(dir, mode='rb'), as_attachment=True, filename='myassistant_api.docx')
    
    return HttpResponse('Sorry. File didn\'t find.')

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def auth(request) -> Response:
    data = request.data
    serializer = AuthSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    access_token, expires = serializer.auth()
    return Response(
        status=status.HTTP_201_CREATED,
        data={
            'access_token': access_token,
            'expires': expires
        }
    )

@api_view(['POST'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def clustering(request) -> Response:
    data = request.data
    serializer = ClusteringSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    repsonse = serializer.clustering(serializer.validated_data)
    return Response(
        status=status.HTTP_200_OK,
        data={
            'data': repsonse
        }
    )

@api_view(['POST'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def calculate_fit(request):
    data = request.data
    user = request.user

    data['email'] = user.email

    serializer = CalculateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    result, message = serializer.calculate_fit(serializer.validated_data)
    if not result:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'error': message}
        )
    
    return Response(
        status=status.HTTP_201_CREATED,
        data={'message': message}
    )

@api_view(['POST'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def calculate_predict(request):
    data = request.data
    user = request.user

    data['email'] = user.email

    serializer = CalculateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    response = serializer.calculate_predict(serializer.validated_data)
    return Response(
        status=status.HTTP_200_OK,
        data={
            'data': response
        }
    )

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup(request) -> Response:
    data = loads(request.body)
    serializer = SignupSerializer(data=data)
    if serializer.is_valid():
        response = serializer.signup(serializer.validated_data)
    else:
        errors = serializer.errors
        print(errors)
        message, *_ = [errors[key][0] for key in errors.keys()]
        response = {
            'status': 'error',
            'message': message
        }

    return Response(
        status=status.HTTP_200_OK,
        data=response
    )

@api_view(['GET'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def lm_list(request):
    lm_model = request.user.lm_model

    return Response(
        status=status.HTTP_200_OK,
        data={
            'lm_model': 'ready' if lm_model else 'no model'
        }
    )

@api_view(['POST'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def lm_train(request) -> Response:
    data = request.data
    data['email'] = request.user.email
    serializer = LMSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.lm_train(serializer.validated_data)

    return Response(
        status=status.HTTP_201_CREATED,
        data={
            'message': 'Model training started.'
        }
    )

@api_view(['POST'])
@authentication_classes([OAuth2CustomAuthentication])
@permission_classes([IsAuthenticated])
def lm_generate(request) -> Response:
    data = request.data
    data['email'] = request.user.email
    serializer = LMSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    response, message = serializer.lm_generate(serializer.validated_data)
    return Response(
        status=status.HTTP_200_OK if response else status.HTTP_400_BAD_REQUEST,
        data={
            'message': message
        }
    )