from django import forms
from .models import Pelicula, Genero, Usuario, Funcion, Sala


class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Acción, Comedia, Terror...', 'required': 'required', 'minlength': '3', 'maxlength': '50'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if nombre is None: nombre = ''
        nombre = nombre.strip().title()
        if not nombre:
            raise forms.ValidationError("Este campo es obligatorio y no puede estar vacío.")
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del género debe tener al menos 3 caracteres.")
        if not any(c.isalpha() for c in nombre):
            raise forms.ValidationError("El nombre del género debe contener letras.")
        return nombre



class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['numero', 'sucursal', 'capacidad']
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1, 2, 3...', 'required': 'required', 'min': '1'}),
            'sucursal': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '25', 'max': '144', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero is not None and numero <= 0:
            raise forms.ValidationError("El número de sala debe ser mayor a 0.")
        return numero

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad is not None and (capacidad < 25 or capacidad > 144):
            raise forms.ValidationError("La capacidad debe estar entre 25 y 144 asientos.")
        return capacidad

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get('numero')
        sucursal = cleaned_data.get('sucursal')
        if numero and sucursal:
            # Si estamos editando, excluirnos a nosotros mismos
            qs = Sala.objects.filter(numero=numero, sucursal=sucursal)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(f"Ya existe la sala {numero} en la sucursal {sucursal.nombre}.")
        return cleaned_data



class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password', 'rol', 'sucursal']
        labels = {'password': 'Contraseña'}
        widgets = {
            'nombre':   forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'minlength': '3', 'maxlength': '100'}),
            'correo':   forms.EmailInput(attrs={'class': 'form-control', 'required': 'required', 'maxlength': '254'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required', 'minlength': '6'}, render_value=True),
            'rol':      forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'sucursal': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if nombre is None: nombre = ''
        nombre = nombre.strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio y no puede estar vacío.")
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if not any(c.isalpha() for c in nombre):
            raise forms.ValidationError("El nombre debe contener letras.")
        return nombre

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '')
        if correo is None: correo = ''
        correo = correo.strip()
        if not correo:
            raise forms.ValidationError("El correo es obligatorio y no puede estar vacío.")
        return correo

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if password is None: password = ''
        password = password.strip()
        if not password:
            raise forms.ValidationError("La contraseña es obligatoria y no puede constar solo de espacios.")
        if len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        return password



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
            'titulo':          forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'required': 'required'}),
            'tmdb_id':         forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'required': 'required'}),
            'sinopsis':        forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'readonly': 'readonly', 'required': 'required'}),
            'imagen_url':      forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'required': 'required'}),
            'clasificacion':   forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'genero':          forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'idioma':          forms.Select(choices=[('Inglés', 'Inglés'), ('Español Latino', 'Español Latino')], attrs={'class': 'form-control', 'required': 'required'}),
            'duracion_minutos':forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '500', 'required': 'required'}),
            'costo_entrada':   forms.Select(choices=[(32.00, 'Común ($32.00)'), (80.00, 'Estreno ($80.00)')], attrs={'class': 'form-control', 'required': 'required'}),
            'estatus':         forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo', '')
        if titulo is None: titulo = ''
        titulo = titulo.strip()
        if not titulo:
            raise forms.ValidationError("El título es obligatorio y no puede estar vacío.")
        return titulo

    def clean_sinopsis(self):
        sinopsis = self.cleaned_data.get('sinopsis', '')
        if sinopsis is None: sinopsis = ''
        sinopsis = sinopsis.strip()
        if not sinopsis:
            raise forms.ValidationError("La sinopsis es obligatoria y no puede estar vacía.")
        return sinopsis

    def clean_imagen_url(self):
        imagen_url = self.cleaned_data.get('imagen_url', '')
        if imagen_url is None: imagen_url = ''
        imagen_url = imagen_url.strip()
        if not imagen_url:
            raise forms.ValidationError("La URL de la imagen es obligatoria.")
        return imagen_url

    def clean_duracion_minutos(self):
        duracion = self.cleaned_data.get('duracion_minutos')
        if duracion is None:
            raise forms.ValidationError("La duración es obligatoria.")
        if duracion < 1 or duracion > 500:
            raise forms.ValidationError("La duración debe ser un número válido de minutos (1 - 500).")
        return duracion



class FuncionForm(forms.ModelForm):
    HORARIOS_CHOICES = [
        ('', '-- Selecciona fecha y sala primero --'),
        ('16:00:00', '4:00 PM (16:00)'),
        ('18:00:00', '6:00 PM (18:00)'),
    ]
    hora_inicio = forms.ChoiceField(choices=HORARIOS_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = Funcion
        fields = ['pelicula', 'sala', 'fecha', 'hora_inicio']
        widgets = {
            'pelicula':    forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'sala':        forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'fecha':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
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
