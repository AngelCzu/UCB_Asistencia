# Comando para generar asistencias automáticamente
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from asistencia.models import *

class Command(BaseCommand):
    help = 'Crea asistencias automáticamente desde marzo hasta diciembre, solo los domingos, para el curso "Corderitos de Jesús 2025" y estudiantes sin curso asignado.'

    def handle(self, *args, **kwargs):
        año_actual = timezone.now().year
        fecha_inicio = datetime.date(año_actual, 3, 1)  # 1 de marzo
        fecha_fin = datetime.date(año_actual, 12, 31)  # 31 de diciembre

        # Obtener el curso "Corderitos de Jesús 2025"
        curso_nombre = "Curso Corderitos de Jesús 2025"
        curso = Curso.objects.filter(nombre=curso_nombre).first()

        # Obtener estudiantes en el curso y los sin curso asignado
        estudiantes = CustomUser.objects.filter(tipo_usuario='estudiante').filter(models.Q(curso=curso) | models.Q(curso__isnull=True))

        if not estudiantes:
            self.stdout.write(self.style.WARNING(f'No hay estudiantes en el curso "{curso_nombre}" ni sin asignar.'))
            return

        # Recorrer cada día desde marzo hasta diciembre
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            if current_date.weekday() == 6:  # Domingo
                for estudiante in estudiantes:
                    if not Asistencia.objects.filter(estudiante=estudiante, fecha=current_date).exists():
                        Asistencia.objects.create(
                            estudiante=estudiante,
                            fecha=current_date,
                            estado='presente',  # Estado predeterminado
                            cantidad_biblias=0  # Valor inicial
                        )
                        self.stdout.write(self.style.SUCCESS(f'Asistencia creada para {estudiante.nombre} el {current_date}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Asistencia ya existe para {estudiante.nombre} el {current_date}'))
            current_date += datetime.timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Proceso de creación de asistencias finalizado.'))
