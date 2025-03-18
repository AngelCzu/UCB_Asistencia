from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout 
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AsistenciaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *
import datetime
from django.utils.timezone import now
from django.http import HttpResponse



# Create your views here.
@csrf_exempt
def acceso(request):  # Cambia el nombre de la vista a "acceso"
    context = {}
    
    if request.method == 'POST':
        # Verifica que los campos del formulario estén presentes
        if 'inputUsuario' in request.POST and 'inputContrasena' in request.POST:
            usuario = request.POST.get('inputUsuario')
            clave = request.POST.get('inputContrasena')
            
            # Autentica al usuario
            user = authenticate(request, username=usuario, password=clave)
            
            if user is not None:
                # Si las credenciales son válidas, inicia sesión
                auth_login(request, user)  # Usa auth_login en lugar de login
                return redirect('/inicio')
            else:
                # Si las credenciales son inválidas, muestra un mensaje de error
                context['error'] = 'Credenciales inválidas. Intente nuevamente.'
    
    # Renderiza la plantilla de login (tanto para GET como para POST con errores)
    return render(request, 'login.html', context)





# Función auxiliar para obtener el color según el porcentaje de asistencia
def get_color_porcentaje(porcentaje):
    if porcentaje < 50:
        return 'red'
    elif 50 <= porcentaje <= 75:
        return 'yellow'
    else:
        return 'green'

@login_required
def inicio(request):
    usuario = request.user
    fecha_actual = now().date()

    if usuario.tipo_usuario == 'profesor' and usuario.curso:
        # Obtener todas las fechas únicas de las asistencias, excluyendo la fecha actual
        fechas_unicas = Asistencia.objects.filter(
            estudiante__curso=usuario.curso,
            fecha__lt=fecha_actual  # Excluir la fecha actual
        ).values_list('fecha', flat=True).distinct().order_by('-fecha')

        # Clase actual
        clase_actual = Asistencia.objects.filter(
            estudiante__curso=usuario.curso,
            fecha=fecha_actual
        ).first()

        # Calcular el total de asistencias, atrasos y ausencias para todas las clases
        asistencias_totales = Asistencia.objects.filter(estudiante__curso=usuario.curso)
        total = asistencias_totales.count()
        presentes = asistencias_totales.filter(estado='presente').count()
        atrasados = asistencias_totales.filter(estado='atrasado').count()
        ausentes = asistencias_totales.filter(estado='ausente').count()

        porcentaje_presentes = (presentes / total) * 100 if total > 0 else 0
        porcentaje_atrasados = (atrasados / total) * 100 if total > 0 else 0
        porcentaje_ausentes = (ausentes / total) * 100 if total > 0 else 0

        datos_grafico = {
            'presentes': round(porcentaje_presentes, 2),
            'atrasados': round(porcentaje_atrasados, 2),
            'ausentes': round(porcentaje_ausentes, 2),
        }
    else:
        fechas_unicas = []
        clase_actual = None
        datos_grafico = None

    context = {
        'usuario': usuario,
        'fechas_unicas': fechas_unicas,
        'clase_actual': clase_actual,
        'fecha_actual': fecha_actual,
        'datos_grafico': datos_grafico
    }

    return render(request, 'inicio.html', context)


@login_required
def modificar_asistencia_fecha(request, fecha):
    if fecha == "hoy":
        fecha = now().date()  # Convertir "hoy" en la fecha actual

    profesor = request.user  # Se asume que el usuario autenticado es un profesor
    
    if profesor.tipo_usuario != 'profesor' or not profesor.curso:
        return redirect('inicio')  # Redirigir si el usuario no es profesor

    # Obtener estudiantes y profesores del curso del profesor (excepto el profesor que generó la clase)
    estudiantes = CustomUser.objects.filter(tipo_usuario='estudiante', curso=profesor.curso)
    profesores = CustomUser.objects.filter(tipo_usuario='profesor', curso=profesor.curso).exclude(id=profesor.id)

    # Crear registros de asistencia para estudiantes si no existen
    for estudiante in estudiantes:
        Asistencia.objects.get_or_create(
            estudiante=estudiante,
            profesor=profesor,
            fecha=fecha,
            defaults={"estado": "ausente", "cantidad_biblias": 0}
        )

    # Crear registros de asistencia para profesores si no existen (estado predeterminado: presente)
    for prof in profesores:
        Asistencia.objects.get_or_create(
            estudiante=prof,
            profesor=profesor,
            fecha=fecha,
            defaults={"estado": "presente", "cantidad_biblias": 0}
        )

    # Obtener lista actualizada de asistencias (estudiantes y profesores)
    asistencia_list = Asistencia.objects.filter(fecha=fecha, estudiante__curso=profesor.curso)

    if request.method == "POST":
        for asistencia in asistencia_list:
            estado = request.POST.get(f"estado_{asistencia.id}", "ausente")
            biblia = request.POST.get(f"biblia_{asistencia.id}", "off") == "on"
            asistencia.estado = estado
            asistencia.cantidad_biblias = 1 if biblia else 0
            asistencia.save()
        return redirect("inicio")

    return render(request, "modificar_asistencia_fecha.html", {"asistencia_list": asistencia_list, "fecha": fecha})


# Función para verificar si el usuario es admin
def es_admin(user):
    return user.tipo_usuario == 'admin'


@login_required
@user_passes_test(es_admin, login_url='/acceso')  # Solo usuarios admin pueden acceder
def admin_panel(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')  # Redirige al panel de admin después de crear el usuario
    else:
        form = CustomUserCreationForm()

    # Obtener todos los usuarios para mostrarlos en el panel
    usuarios = CustomUser.objects.all()
    context = {
        'form': form,
        'usuarios': usuarios,
    }
    return render(request, 'admin_panel.html', context)





