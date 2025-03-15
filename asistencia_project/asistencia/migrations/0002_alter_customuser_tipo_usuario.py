# Generated by Django 5.1.7 on 2025-03-15 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='tipo_usuario',
            field=models.CharField(choices=[('profesor', 'Profesor'), ('estudiante', 'Estudiante'), ('admin', 'admin')], default='estudiante', max_length=10),
        ),
    ]
