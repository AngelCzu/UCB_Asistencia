from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

# Modelo de Curso
class Curso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre
    




# Modelo de Usuario Personalizado
class CustomUser(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
        ('admin', 'Admin'),
        ('oyente', 'Oyente'),
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='estudiante')
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_tipo_usuario_display()})"

# Modelo de Asistencia
class Asistencia(models.Model):
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('atrasado', 'Atrasado'),
    ]
    
    estudiante = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'estudiante'})
    fecha = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    
    
    def __str__(self):
        return f"{self.estudiante.nombre} {self.estudiante.apellido} - {self.fecha} - {self.get_estado_display()}"
