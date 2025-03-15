from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required



urlpatterns = [
    path("", views.acceso),
    path('acceso', views.acceso, name='acceso'),
    path('inicio', views.inicio, name='inicio'),
    path('modificar_asistencia/<int:asistencia_id>/', views.modificar_asistencia, name='modificar_asistencia'),
    path('modificar_asistencia_fecha/<str:fecha>/', login_required(views.modificar_asistencia_fecha), name='modificar_asistencia_fecha'),
    path('admin_panel', login_required(views.admin_panel), name='admin_panel'),  # Nueva URL para el panel de admin

     path('exportar_excel/', login_required(views.exportar_asistencias_excel), name='exportar_excel'),
]