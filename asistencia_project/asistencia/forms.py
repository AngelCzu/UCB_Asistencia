from django import forms
from .models import Asistencia, CustomUser, Curso
from django.contrib.auth.forms import UserCreationForm

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['estado']

class CustomUserCreationForm(UserCreationForm):
    SEXO_CHOICES = [
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer'),
    ]
    
    TIPO_USUARIO_CHOICES = [
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
        ('admin', 'Admin'),
        ('oyente', 'Oyente'),
    ]
    
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    sexo = forms.ChoiceField(
        choices=SEXO_CHOICES, 
        widget=forms.RadioSelect(),  # Usa botones de opción
        required=True
    )
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_CHOICES, 
        widget=forms.RadioSelect(),  # Usa botones de opción
        required=True
    )
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'nombre', 'apellido', 'sexo', 'tipo_usuario', 'curso', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        profesor = kwargs.pop('profesor', None)
        super().__init__(*args, **kwargs)

        # Ocultar campos de contraseña y dejarlos como no obligatorios
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password2'].widget = forms.HiddenInput()
        self.fields['password1'].required = False
        self.fields['password2'].required = False

        # Mostrar el curso pero desactivado (solo lectura)
        if profesor:
            self.fields['curso'].initial = profesor.curso
            self.fields['curso'].widget.attrs['readonly'] = True
            self.fields['curso'].disabled = True  # Impide modificación en HTML

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password('123456')  # Contraseña por defecto
        if commit:
            user.save()
        return user

