import os
import django
import sys

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cine_cdmx.settings')
django.setup()

from cartelera.models import Sucursal, Genero, Pelicula, EstatusPelicula, ClasificacionPelicula, Sala, Funcion
from datetime import date, time

def populate():
    print("Borrando datos anteriores...")
    Funcion.objects.all().delete()
    Sala.objects.all().delete()
    Pelicula.objects.all().delete()
    Genero.objects.all().delete()
    Sucursal.objects.all().delete()

    print("Creando sucursales...")
    s_norte = Sucursal.objects.create(nombre="CDMX Norte")
    s_oriente = Sucursal.objects.create(nombre="CDMX Oriente")
    s_reforma = Sucursal.objects.create(nombre="Reforma")
    s_perisur = Sucursal.objects.create(nombre="Perisur")

    print("Creando salas...")
    sala1 = Sala.objects.create(numero=1, sucursal=s_norte)
    sala2 = Sala.objects.create(numero=2, sucursal=s_perisur)

    print("Creando géneros...")
    g_accion = Genero.objects.create(nombre="Acción / Ciencia Ficción")
    g_misterio = Genero.objects.create(nombre="Suspense / Misterio")
    Genero.objects.create(nombre="Comedia")
    Genero.objects.create(nombre="Terror")
    Genero.objects.create(nombre="Drama")
    Genero.objects.create(nombre="Aventura")
    Genero.objects.create(nombre="Animación")
    Genero.objects.create(nombre="Romance")
    Genero.objects.create(nombre="Fantasía")
    Genero.objects.create(nombre="Documental")

    print("Creando películas...")
    p1 = Pelicula.objects.create(
        titulo="Guardianes de la Galaxia",
        clasificacion=ClasificacionPelicula.B,
        genero=g_accion,
        idioma="Español Latino",
        duracion_minutos=122,
        sinopsis="Un grupo de criminales intergalácticos...",
        estatus=EstatusPelicula.ACTIVA,
        costo_entrada=80.00,
        tmdb_id=118340
    )

    p2 = Pelicula.objects.create(
        titulo="Scream 7",
        clasificacion=ClasificacionPelicula.B15,
        genero=g_misterio,
        idioma="Subtitulada",
        duracion_minutos=138,
        sinopsis="El experto en simbología Robert Langdon...",
        estatus=EstatusPelicula.ACTIVA,
        costo_entrada=85.00,
        tmdb_id=1159559
    )

    print("Creando funciones...")
    Funcion.objects.create(pelicula=p1, sala=sala1, fecha=date.today(), hora_inicio=time(14, 0))
    Funcion.objects.create(pelicula=p1, sala=sala1, fecha=date.today(), hora_inicio=time(16, 30))
    Funcion.objects.create(pelicula=p2, sala=sala2, fecha=date.today(), hora_inicio=time(19, 15))

    print("¡Base de datos poblada exitosamente!")

if __name__ == '__main__':
    populate()
