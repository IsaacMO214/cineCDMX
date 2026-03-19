from django.db import models


class RolUsuario(models.TextChoices):
    ADMIN    = 'ADMIN',    'Administrador'
    EMPLEADO = 'EMPLEADO', 'Empleado'
    CLIENTE  = 'CLIENTE',  'Cliente'


class ClasificacionPelicula(models.TextChoices):
    AA  = 'AA',  'AA'
    A   = 'A',   'A'
    B   = 'B',   'B'
    B15 = 'B15', 'B15'
    C   = 'C',   'C'


class EstatusPelicula(models.TextChoices):
    ACTIVA       = 'ACTIVA',       'Activa'
    INACTIVA     = 'INACTIVA',     'Inactiva'
    PROXIMAMENTE = 'PROXIMAMENTE', 'Próximamente'


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre   = models.CharField(max_length=100)
    correo   = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    rol      = models.CharField(max_length=20, choices=RolUsuario.choices, default=RolUsuario.CLIENTE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Sala(models.Model):
    numero   = models.IntegerField()
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='salas')
    capacidad = models.IntegerField(default=50)

    def __str__(self):
        return f"Sala {self.numero} - {self.sucursal.nombre}"


class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    titulo            = models.CharField(max_length=200)
    clasificacion     = models.CharField(max_length=5, choices=ClasificacionPelicula.choices)
    genero            = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True)
    idioma            = models.CharField(max_length=50)
    duracion_minutos  = models.IntegerField()
    sinopsis          = models.TextField()
    imagen_url        = models.URLField(max_length=500, blank=True, null=True)
    estatus           = models.CharField(max_length=20, choices=EstatusPelicula.choices, default=EstatusPelicula.ACTIVA)
    costo_entrada     = models.DecimalField(max_digits=6, decimal_places=2)
    tmdb_id           = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.titulo


class Funcion(models.Model):
    pelicula    = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name='funciones')
    sala        = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fecha       = models.DateField()
    hora_inicio = models.TimeField()

    def __str__(self):
        return f"{self.pelicula.titulo} - {self.fecha} {self.hora_inicio} en {self.sala}"

class Boleto(models.Model):
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE, related_name='boletos')
    asiento = models.CharField(max_length=10)
    precio = models.DecimalField(max_digits=6, decimal_places=2, default=32.00)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asiento {self.asiento} - {self.funcion}"
