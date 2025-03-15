from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("", views.acceso),
    path('acceso', views.acceso, name='acceso'),
    path('inicio', views.inicio, name='inicio'),
    path('modificar_asistencia/<int:asistencia_id>/', views.modificar_asistencia, name='modificar_asistencia'),
    path('admin_panel', login_required(views.admin_panel), name='admin_panel'),  # Nueva URL para el panel de admin
]