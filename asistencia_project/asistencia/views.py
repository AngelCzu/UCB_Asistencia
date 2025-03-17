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
import json
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

    if usuario.tipo_usuario == 'profesor' and usuario.curso:
        clases = Asistencia.objects.filter(estudiante__curso=usuario.curso).order_by('-fecha')
    else:
        clases = []

    context = {
        'usuario': usuario,
        'clases': clases,
    }

    return render(request, 'inicio.html', context)





@login_required
def modificar_asistencia(request, asistencia_id):
    asistencia = get_object_or_404(Asistencia, id=asistencia_id)

    if request.method == 'POST':
        form = AsistenciaForm(request.POST, instance=asistencia)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = AsistenciaForm(instance=asistencia)

    context = {
        'form': form,
        'asistencia': asistencia,
    }

    return render(request, 'modificar_asistencia.html', context)


@login_required
def modificar_asistencia_fecha(request, fecha):
    if fecha == "hoy":
        fecha_obj = timezone.now().date()
    else:
        fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()

    profesor = request.user

    if profesor.tipo_usuario != 'profesor' or not profesor.curso:
        return redirect('inicio')

    estudiantes = CustomUser.objects.filter(tipo_usuario='estudiante', curso=profesor.curso)

    asistencias = []
    for estudiante in estudiantes:
        asistencia, created = Asistencia.objects.get_or_create(
            estudiante=estudiante,
            fecha=fecha_obj,
            profesor=profesor,  # Se asigna el profesor que genera la asistencia
            defaults={'estado': 'ausente', 'cantidad_biblias': 0}
        )
        asistencias.append(asistencia)

    if request.method == 'POST':
        for asistencia in asistencias:
            estado = request.POST.get(f"estado_{asistencia.id}")
            biblia = request.POST.get(f"biblia_{asistencia.id}", "off") == "on"
            asistencia.estado = estado
            asistencia.cantidad_biblias = 1 if biblia else 0
            asistencia.save()
    
   

        return redirect('inicio')

     # Crear un formulario para cada asistencia
    forms = [AsistenciaForm(prefix=str(asistencia.id), instance=asistencia) for asistencia in asistencias]

    context = {
        'fecha': fecha_obj,
        'asistencias': asistencias,
        'forms': forms,
    }

    return render(request, 'modificar_asistencia_fecha.html', context)



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





