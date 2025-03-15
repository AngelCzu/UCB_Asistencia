# asistencia/management/commands/crear_cursos.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from asistencia.models import Curso

class Command(BaseCommand):
    help = 'Crea los cursos para el año actual (marzo a diciembre).'

    def handle(self, *args, **kwargs):
        año_actual = timezone.now().year
        cursos_existentes = Curso.objects.filter(nombre__icontains=str(año_actual)).exists()

        if not cursos_existentes:
            cursos = [
                f"Clase Berea {año_actual}",
                f"Curso Corderitos de Jesús {año_actual}",
                f"Curso Embajadores del Rey {año_actual}",
                f"Curso de Nehemías {año_actual}",
                f"Curso de Timoteo {año_actual}",
            ]
            for curso_nombre in cursos:
                Curso.objects.create(nombre=curso_nombre)
                self.stdout.write(self.style.SUCCESS(f'Curso creado: {curso_nombre}'))
        else:
            self.stdout.write(self.style.WARNING('Los cursos ya existen para este año.'))