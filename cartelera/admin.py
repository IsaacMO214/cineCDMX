from django.contrib import admin
from .models import Pelicula, Sucursal, Sala, Genero, Funcion, Usuario

admin.site.register(Pelicula)
admin.site.register(Sucursal)
admin.site.register(Sala)
admin.site.register(Genero)
admin.site.register(Funcion)
admin.site.register(Usuario)
