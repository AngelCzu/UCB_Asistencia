from django.urls import path
from . import views


urlpatterns = [
    path("", views.acceso),
    path('acceso', views.acceso, name='acceso'),
    path('inicio', views.inicio, name='inicio'),
    path('modificar_asistencia/<int:asistencia_id>/', views.modificar_asistencia, name='modificar_asistencia'),
]