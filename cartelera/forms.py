from django import forms
from .models import Pelicula, Genero, Usuario, Funcion


class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Acción, Comedia, Terror...'}),
        }


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password', 'rol', 'sucursal']
        labels = {'password': 'Contraseña'}
        widgets = {
            'nombre':   forms.TextInput(attrs={'class': 'form-control'}),
            'correo':   forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True),
            'rol':      forms.Select(attrs={'class': 'form-control'}),
            'sucursal': forms.Select(attrs={'class': 'form-control'}),
        }


class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ['titulo', 'tmdb_id', 'sinopsis', 'imagen_url', 'clasificacion', 'genero', 'idioma', 'duracion_minutos', 'costo_entrada', 'estatus']
        labels = {
            'tmdb_id': 'ID TMDB (Se llena solo)',
            'imagen_url': 'Póster URL (Se llena solo)',
            'duracion_minutos': 'Duración (mins)',
        }
        widgets = {
            'titulo':          forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'tmdb_id':         forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'sinopsis':        forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'readonly': 'readonly'}),
            'imagen_url':      forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'clasificacion':   forms.Select(attrs={'class': 'form-control'}),
            'genero':          forms.Select(attrs={'class': 'form-control'}),
            'idioma':          forms.Select(choices=[('Inglés', 'Inglés'), ('Español Latino', 'Español Latino')], attrs={'class': 'form-control'}),
            'duracion_minutos':forms.NumberInput(attrs={'class': 'form-control', 'max': '240'}),
            'costo_entrada':   forms.Select(choices=[(32.00, 'Común ($32.00)'), (80.00, 'Estreno ($80.00)')], attrs={'class': 'form-control'}),
            'estatus':         forms.Select(attrs={'class': 'form-control'}),
        }


class FuncionForm(forms.ModelForm):
    HORARIOS_CHOICES = [
        ('', '-- Selecciona fecha y sala primero --'),
        ('16:00:00', '4:00 PM (16:00)'),
        ('18:00:00', '6:00 PM (18:00)'),
    ]
    hora_inicio = forms.ChoiceField(choices=HORARIOS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Funcion
        fields = ['pelicula', 'sala', 'fecha', 'hora_inicio']
        widgets = {
            'pelicula':    forms.Select(attrs={'class': 'form-control'}),
            'sala':        forms.Select(attrs={'class': 'form-control'}),
            'fecha':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import datetime
        manana = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        self.fields['fecha'].widget.attrs['min'] = manana

    def clean_fecha(self):
        import datetime
        fecha = self.cleaned_data.get('fecha')
        if fecha:
            if fecha <= datetime.date.today():
                raise forms.ValidationError("La función solo puede ser programada a partir del día de mañana.")
        return fecha

    def clean_hora_inicio(self):
        import datetime
        hora_str = self.cleaned_data.get('hora_inicio')
        if hora_str:
            try:
                hora = datetime.datetime.strptime(hora_str, '%H:%M:%S').time()
            except ValueError:
                raise forms.ValidationError("El horario seleccionado no es válido.")
                
            if hora not in [datetime.time(16, 0), datetime.time(18, 0)]:
                raise forms.ValidationError("Las funciones solo pueden ser a las 4:00 PM (16:00) o a las 6:00 PM (18:00).")
            return hora
        return None

    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        if sala and fecha and hora_inicio:
            if Funcion.objects.filter(sala=sala, fecha=fecha, hora_inicio=hora_inicio).exists():
                raise forms.ValidationError("¡Choque de Horarios! Ya existe una función programada en esa Sala, Fecha y Hora.")
        return cleaned_data
