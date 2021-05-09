from django.urls import path;

from api import views;

urlpatterns = [
    path('transform', views.transform, name='transform'),
    path('cut', views.cut, name='cut'),
    path('model', views.model, name='model')
]
