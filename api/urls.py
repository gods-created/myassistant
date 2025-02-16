from django.urls import path
from .views import (
    docs,
    signup,
    auth, 
    clustering,
    calculate_fit,
    calculate_predict,
    lm_train,
    lm_generate,
    lm_list
)

app_name = 'api'

urlpatterns = [
    path('docs/', docs, name='audocsth'),
    path('signup/', signup, name='signup'),
    path('auth/', auth, name='auth'),
    path('clustering/', clustering, name='clustering'),
    path('calculate/fit/', calculate_fit, name='calculate_fit'),
    path('calculate/predict/', calculate_predict, name='calculate_predict'),
    path('lm/train/', lm_train, name='lm_train'),
    path('lm/generate/', lm_generate, name='lm_generate'),
    path('lm/list/', lm_list, name='lm_list'),
]