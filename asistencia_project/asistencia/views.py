from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout 
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import AsistenciaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *
from datetime import datetime
from django.db.models import *
import json
from django.core.paginator import Paginator

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

    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    # Filtro base: por curso del usuario
    asistencias = Asistencia.objects.filter(estudiante__curso=usuario.curso)

    if fecha_inicio and fecha_fin:
        fecha_inicio_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        asistencias = asistencias.filter(fecha__range=(fecha_inicio_date, fecha_fin_date))

    # Obtener fechas únicas para la tabla
    fechas_unicas = asistencias.values_list("fecha", flat=True).distinct().order_by("-fecha")

    # Asociar profesor a cada fecha
    profesores_por_fecha = [
        (fecha, Asistencia.objects.filter(fecha=fecha, estudiante__curso=usuario.curso).first().profesor)
        for fecha in fechas_unicas
    ]

    # Contar estados
    estados_labels = ["Presente", "Ausente", "Atrasado"]
    estados_data = {estado: 0 for estado in estados_labels}

    estado_counts = asistencias.values("estado").annotate(total=Count("id"))
    for item in estado_counts:
        estados_data[item["estado"].capitalize()] = item["total"]

    # Biblias traídas vs no traídas
    total_biblias = asistencias.aggregate(Sum("cantidad_biblias"))["cantidad_biblias__sum"] or 0
    sin_biblia = asistencias.filter(cantidad_biblias=0).count()

    # Paginar la lista de clases
    paginator = Paginator(profesores_por_fecha, 5)  # 5 clases por página (ajustable)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "usuario": usuario,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estados_labels": json.dumps(estados_labels),
        "estados_data": json.dumps(list(estados_data.values())),
        "biblias_labels": json.dumps(["Traídas", "No Traídas"]),
        "biblias_data": json.dumps([total_biblias, sin_biblia]),
        "profesores_por_fecha": profesores_por_fecha,
        'page_obj': page_obj,
    }

    return render(request, "inicio.html", context)

@login_required
@login_required
def modificar_asistencia_fecha(request, fecha):
    if fecha == "hoy":
        fecha = now().date()

    profesor = request.user

    if profesor.tipo_usuario != 'profesor' or not profesor.curso:
        return redirect('inicio')

    # Obtener todos los usuarios del curso (estudiantes y profesores, incluyendo al generador)
    usuarios = CustomUser.objects.filter(
        curso=profesor.curso
    ).order_by('tipo_usuario', 'nombre', 'apellido')  # Ordenar por tipo y nombre

    # Crear asistencia si no existe (todos como ausente)
    for user in usuarios:
        if not Asistencia.objects.filter(estudiante=user, fecha=fecha).exists():
            Asistencia.objects.create(
                estudiante=user,
                profesor=profesor,
                fecha=fecha,
                estado="ausente",
                cantidad_biblias=0
            )

    # Obtener la lista ordenada de asistencias para mostrar en la tabla
    asistencia_list = Asistencia.objects.filter(
        fecha=fecha,
        estudiante__curso=profesor.curso
    ).select_related('estudiante').order_by(
        'estudiante__tipo_usuario', 'estudiante__nombre', 'estudiante__apellido'
    )

    if request.method == "POST":
        for asistencia in asistencia_list:
            estado = request.POST.get(f"estado_{asistencia.id}", "ausente")
            biblia = request.POST.get(f"biblia_{asistencia.id}", "off") == "on"
            asistencia.estado = estado
            asistencia.cantidad_biblias = 1 if biblia else 0
            asistencia.save()
        return redirect("inicio")

    return render(request, "modificar_asistencia_fecha.html", {
        "asistencia_list": asistencia_list,
        "fecha": fecha
    })


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


@login_required

def crear_estudiante(request):
    if request.user.tipo_usuario != 'profesor':
        return redirect('inicio')  # Solo profesores

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, profesor=request.user)
        if form.is_valid():
            nuevo_usuario = form.save(commit=False)
            nuevo_usuario.curso = request.user.curso  # Asegura que sea su curso
            nuevo_usuario.save()
            return redirect('inicio')
    else:
        form = CustomUserCreationForm(initial={'tipo_usuario': 'oyente'}, profesor=request.user)

    return render(request, 'crear_estudiante.html', {'form': form})


