from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout 
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AsistenciaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *

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

@login_required
def inicio(request):
    usuario = request.user
    año_actual = timezone.now().year
    fecha_inicio = timezone.datetime(año_actual, 3, 1).date()  # 1 de marzo
    fecha_fin = timezone.datetime(año_actual, 12, 31).date()  # 31 de diciembre

    cursos = Curso.objects.all()
    asistencias_pasadas = []

    if usuario.tipo_usuario == 'estudiante':
        asistencias_pasadas = Asistencia.objects.filter(
            estudiante=usuario,
            fecha__range=(fecha_inicio, fecha_fin))
    elif usuario.tipo_usuario == 'profesor' and usuario.curso:
        asistencias_pasadas = Asistencia.objects.filter(
            estudiante__curso=usuario.curso,
            fecha__range=(fecha_inicio, fecha_fin))

    # Verificar si el usuario es admin
    es_admin = usuario.tipo_usuario == 'admin'

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'asistencias_pasadas': asistencias_pasadas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'es_admin': es_admin,  # Agregar esta variable al contexto
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