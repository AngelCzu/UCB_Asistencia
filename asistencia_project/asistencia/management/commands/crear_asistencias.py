from django.core.management.base import BaseCommand
from django.utils import timezone
from asistencia.models import Asistencia, CustomUser, Curso
import datetime

class Command(BaseCommand):
    help = 'Crea asistencias automáticamente desde marzo hasta diciembre, solo los domingos.'

    def handle(self, *args, **kwargs):
        año_actual = timezone.now().year
        fecha_inicio = datetime.date(año_actual, 3, 1)  # 1 de marzo
        fecha_fin = datetime.date(año_actual, 12, 31)  # 31 de diciembre

        # Obtener todos los estudiantes
        estudiantes = CustomUser.objects.filter(tipo_usuario='estudiante')

        # Recorrer cada día desde marzo hasta diciembre
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # Verificar si el día es domingo
            if current_date.weekday() == 6:  # Domingo es 6 en Python (lunes=0, domingo=6)
                # Crear asistencias para todos los estudiantes en este día
                for estudiante in estudiantes:
                    # Verificar si ya existe una asistencia para este estudiante en esta fecha
                    if not Asistencia.objects.filter(estudiante=estudiante, fecha=current_date).exists():
                        Asistencia.objects.create(
                            estudiante=estudiante,
                            fecha=current_date,
                            estado='presente'  # Estado predeterminado
                        )
                        self.stdout.write(self.style.SUCCESS(f'Asistencia creada para {estudiante.nombre} el {current_date}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Asistencia ya existe para {estudiante.nombre} el {current_date}'))
            # Avanzar al siguiente día
            current_date += datetime.timedelta(days=1)