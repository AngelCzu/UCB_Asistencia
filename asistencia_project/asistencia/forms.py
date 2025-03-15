from django import forms
from .models import Asistencia
from django.contrib.auth.forms import UserCreationForm
from .models import *

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['estado']


class CustomUserCreationForm(UserCreationForm):
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    tipo_usuario = forms.ChoiceField(choices=CustomUser.TIPO_USUARIO_CHOICES, required=True)
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'nombre', 'apellido', 'tipo_usuario', 'curso', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ocultar y desactivar los campos de contraseña si el tipo de usuario no es profesor
        if 'tipo_usuario' in self.data and self.data['tipo_usuario'] != 'profesor':
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].widget = forms.HiddenInput()
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        elif self.instance.pk and self.instance.tipo_usuario != 'profesor':
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].widget = forms.HiddenInput()
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        # Establecer la contraseña predeterminada si el usuario no es profesor
        if self.cleaned_data['tipo_usuario'] != 'profesor':
            user.set_password('123456')  # Contraseña predeterminada
        if commit:
            user.save()
        return user