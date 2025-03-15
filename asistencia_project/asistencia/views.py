from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout 
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AsistenciaForm


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
    # Obtener el usuario actual
    usuario = request.user

    # Obtener el rango de tiempo (marzo a diciembre del año actual)
    año_actual = timezone.now().year
    fecha_inicio = timezone.datetime(año_actual, 3, 1).date()  # 1 de marzo
    fecha_fin = timezone.datetime(año_actual, 12, 31).date()  # 31 de diciembre

    # Obtener los cursos
    cursos = Curso.objects.all()

    # Obtener las asistencias pasadas del usuario (si es estudiante)
    asistencias_pasadas = []
    if usuario.tipo_usuario == 'estudiante':
        asistencias_pasadas = Asistencia.objects.filter(
            estudiante=usuario,
            fecha__range=(fecha_inicio, fecha_fin))
    elif usuario.tipo_usuario == 'profesor':
        # Si es profesor, mostrar asistencias de todos los estudiantes en su curso
        if usuario.curso:
            asistencias_pasadas = Asistencia.objects.filter(
                estudiante__curso=usuario.curso,
                fecha__range=(fecha_inicio, fecha_fin))

    context = {
        'usuario': usuario,
        'cursos': cursos,
        'asistencias_pasadas': asistencias_pasadas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
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