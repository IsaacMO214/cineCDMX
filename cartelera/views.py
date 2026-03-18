import requests
import urllib.parse
import datetime
from itertools import chain
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import PeliculaForm, FuncionForm, GeneroForm, UsuarioForm, SalaForm
from .models import Pelicula, Sucursal, Usuario, Funcion, Genero, RolUsuario, EstatusPelicula, Boleto, Sala


def get_data_from_tmdb(tmdb_id):
    if not tmdb_id:
        return None, None, None
    api_key = str(settings.TMDB_API_KEY).strip(' "\'')
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=es-MX"
    try:
        response = requests.get(url, headers={"accept": "application/json"})
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            sinopsis = data.get("overview")
            runtime = data.get("runtime")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            return poster_url, sinopsis, runtime
    except Exception as e:
        print(f"Error conectando a TMDB: {e}")
    return None, None, None


def cartelera_view(request):
    if request.user.is_authenticated and 'usuario_id' not in request.session:
        usuario, _ = Usuario.objects.get_or_create(
            correo=request.user.email,
            defaults={
                'nombre': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                'password': 'NoAplica_SeLogueaPorGoogle',
                'rol': 'CLIENTE',
            }
        )
        request.session['usuario_id'] = usuario.id
        request.session['usuario_nombre'] = usuario.nombre
        request.session['usuario_rol'] = usuario.rol

    if request.session.get('usuario_rol') == 'EMPLEADO':
        return redirect('dashboard_empleado')

    sucursal_id = request.GET.get('sucursal')
    hoy = datetime.date.today()

    peliculas_activas = Pelicula.objects.filter(estatus=EstatusPelicula.ACTIVA)
    peliculas_proximamente = Pelicula.objects.filter(estatus=EstatusPelicula.PROXIMAMENTE)

    if sucursal_id:
        peliculas_activas = peliculas_activas.filter(
            funciones__sala__sucursal_id=sucursal_id,
            funciones__fecha__gte=hoy
        ).distinct()

    peliculas = list(chain(peliculas_activas, peliculas_proximamente))

    for pelicula in peliculas:
        if pelicula.tmdb_id and (not pelicula.imagen_url or not pelicula.sinopsis or not pelicula.duracion_minutos):
            poster_url, sinopsis_api, duracion_api = get_data_from_tmdb(pelicula.tmdb_id)
            needs_save = False
            if poster_url and not pelicula.imagen_url:
                pelicula.imagen_url = poster_url
                needs_save = True
            if sinopsis_api and not pelicula.sinopsis:
                pelicula.sinopsis = sinopsis_api
                needs_save = True
            if duracion_api and not pelicula.duracion_minutos:
                pelicula.duracion_minutos = duracion_api
                needs_save = True
            if needs_save:
                pelicula.save()

    context = {
        'peliculas': peliculas,
        'sucursales': Sucursal.objects.all(),
        'sucursal_seleccionada': sucursal_id,
    }
    return render(request, 'cartelera/cartelera.html', context)


def search_tmdb_view(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'results': []})
    api_key = str(settings.TMDB_API_KEY).strip(' "\'')
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=es-MX&query={urllib.parse.quote(query)}&page=1"
    try:
        response = requests.get(url, headers={"accept": "application/json"})
        if response.status_code == 200:
            return JsonResponse(response.json())
    except Exception as e:
        print(f"Error en buscador TMDB: {e}")
    return JsonResponse({'results': []})

def detalles_tmdb_view(request):
    tmdb_id = request.GET.get('tmdb_id')
    if not tmdb_id:
        return JsonResponse({'runtime': ''})
    _, _, runtime = get_data_from_tmdb(tmdb_id)
    return JsonResponse({'runtime': runtime})

def horarios_disponibles_view(request):
    sala_id = request.GET.get('sala')
    fecha = request.GET.get('fecha')
    
    if not sala_id or not fecha:
        return JsonResponse({'horarios': []})
        
    horarios_posibles = [datetime.time(16, 0), datetime.time(18, 0)]
    
    # Check if any functions already exist on that sala and date
    funciones_existentes = Funcion.objects.filter(sala_id=sala_id, fecha=fecha).values_list('hora_inicio', flat=True)
    
    horarios_disponibles = []
    for h in horarios_posibles:
        if h not in funciones_existentes:
            horarios_disponibles.append({
                'value': h.strftime('%H:%M:%S'),
                'label': h.strftime('%I:%M %p').lstrip('0') + f" ({h.strftime('%H:%M')})"
            })
            
    return JsonResponse({'horarios': horarios_disponibles})


def dashboard_empleado_view(request):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('cartelera')
    
    from .models import Sala, Genero, Usuario, Pelicula, Funcion
    context = {
        'clientes': Usuario.objects.filter(rol='CLIENTE'),
        'salas': Sala.objects.all(),
        'generos': Genero.objects.all().order_by('nombre'),
        'peliculas': Pelicula.objects.all().order_by('titulo'),
        'funciones': Funcion.objects.all().order_by('-fecha', '-hora_inicio'),
    }
    return render(request, 'cartelera/dashboard_empleado.html', context)

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        try:
            usuario = Usuario.objects.get(correo=correo, password=password)
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.rol
            return redirect('cartelera')
        except Usuario.DoesNotExist:
            return render(request, 'cartelera/login.html', {'error': 'El correo o la contraseña son incorrectos.'})
    return render(request, 'cartelera/login.html')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()
    return redirect('cartelera')


def agregar_pelicula_view(request):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    if request.method == 'POST':
        form = PeliculaForm(request.POST)
        if form.is_valid():
            pelicula = form.save()
            if pelicula.tmdb_id:
                poster_url, sinopsis_api, duracion_api = get_data_from_tmdb(pelicula.tmdb_id)
                needs_save = False
                if poster_url and not pelicula.imagen_url:
                    pelicula.imagen_url = poster_url
                    needs_save = True
                if sinopsis_api and not pelicula.sinopsis:
                    pelicula.sinopsis = sinopsis_api
                    needs_save = True
                if duracion_api and not pelicula.duracion_minutos:
                    pelicula.duracion_minutos = duracion_api
                    needs_save = True
                if needs_save:
                    pelicula.save()
            return redirect('dashboard_empleado')
    else:
        form = PeliculaForm()
    return render(request, 'cartelera/agregar_pelicula.html', {'form': form})


def editar_pelicula_view(request, pelicula_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    if request.method == 'POST':
        form = PeliculaForm(request.POST, instance=pelicula)
        if form.is_valid():
            form.save()
            return redirect('detalle_pelicula', pelicula_id=pelicula_id)
    else:
        form = PeliculaForm(instance=pelicula)
    return render(request, 'cartelera/editar_pelicula.html', {'form': form, 'pelicula': pelicula})


def eliminar_pelicula_view(request, pelicula_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    if request.method == 'POST':
        pelicula.delete()
        return redirect('cartelera')
    return redirect('detalle_pelicula', pelicula_id=pelicula_id)


def detalle_pelicula_view(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)
    hoy = datetime.date.today()
    sucursal_id = request.GET.get('sucursal')
    funciones_query = pelicula.funciones.filter(fecha__gte=hoy)
    if sucursal_id:
        funciones_query = funciones_query.filter(sala__sucursal_id=sucursal_id)
    context = {
        'pelicula': pelicula,
        'funciones': funciones_query.order_by('fecha', 'hora_inicio'),
        'sucursales': Sucursal.objects.all(),
        'sucursal_seleccionada': sucursal_id,
    }
    return render(request, 'cartelera/detalle_pelicula.html', context)


def agregar_funcion_view(request):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    if request.method == 'POST':
        form = FuncionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cartelera')
    else:
        form = FuncionForm()
    sucursales = Sucursal.objects.prefetch_related('salas').all()
    salas_por_sucursal = {}
    for suc in sucursales:
        salas_por_sucursal[str(suc.id)] = [{'id': sala.id, 'text': f'Sala {sala.numero}'} for sala in suc.salas.all()]
        
    return render(request, 'cartelera/agregar_funcion.html', {
        'form': form,
        'sucursales': sucursales,
        'salas_json': salas_por_sucursal
    })


def usuarios_view(request):
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'cartelera/usuarios.html', {
        'usuarios': Usuario.objects.all().order_by('rol', 'nombre'),
        'form': form,
        'roles': RolUsuario.choices,
        'sucursales': Sucursal.objects.all(),
    })


def editar_usuario_view(request, usuario_id):
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'cartelera/usuarios.html', {
        'usuarios': Usuario.objects.all().order_by('rol', 'nombre'),
        'form': form,
        'editando': usuario,
        'roles': RolUsuario.choices,
        'sucursales': Sucursal.objects.all(),
    })


def eliminar_usuario_view(request, usuario_id):
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        if usuario.id == request.session.get('usuario_id'):
            return render(request, 'cartelera/usuarios.html', {
                'usuarios': Usuario.objects.all().order_by('rol', 'nombre'),
                'form': UsuarioForm(),
                'error_eliminar': 'No puedes eliminar tu propia cuenta de gerente.',
                'roles': RolUsuario.choices,
                'sucursales': Sucursal.objects.all(),
            })
        usuario.delete()
        return redirect('usuarios')
    return redirect('usuarios')


def generos_view(request):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    if request.method == 'POST':
        form = GeneroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('generos')
    else:
        form = GeneroForm()
    return render(request, 'cartelera/generos.html', {
        'generos': Genero.objects.all().order_by('nombre'),
        'form': form,
    })


def editar_genero_view(request, genero_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    genero = get_object_or_404(Genero, id=genero_id)
    if request.method == 'POST':
        form = GeneroForm(request.POST, instance=genero)
        if form.is_valid():
            form.save()
            return redirect('generos')
    else:
        form = GeneroForm(instance=genero)
    return render(request, 'cartelera/generos.html', {
        'generos': Genero.objects.all().order_by('nombre'),
        'form': form,
        'editando': genero,
    })


def eliminar_genero_view(request, genero_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    genero = get_object_or_404(Genero, id=genero_id)
    if request.method == 'POST':
        if genero.pelicula_set.exists():
            return render(request, 'cartelera/generos.html', {
                'generos': Genero.objects.all().order_by('nombre'),
                'form': GeneroForm(),
                'error_eliminar': f'No se puede eliminar "{genero.nombre}" porque tiene películas asignadas.',
            })
        genero.delete()
        return redirect('generos')
    return redirect('generos')


def salas_view(request):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('salas')
    else:
        form = SalaForm()
    return render(request, 'cartelera/salas.html', {
        'salas': Sala.objects.all().order_by('sucursal__nombre', 'numero'),
        'form': form,
    })


def editar_sala_view(request, sala_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    sala = get_object_or_404(Sala, id=sala_id)
    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            return redirect('salas')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'cartelera/salas.html', {
        'salas': Sala.objects.all().order_by('sucursal__nombre', 'numero'),
        'form': form,
        'editando': sala,
    })


def eliminar_sala_view(request, sala_id):
    if request.session.get('usuario_rol') != 'EMPLEADO':
        return redirect('login')
    sala = get_object_or_404(Sala, id=sala_id)
    if request.method == 'POST':
        if sala.funcion_set.exists():
            return render(request, 'cartelera/salas.html', {
                'salas': Sala.objects.all().order_by('sucursal__nombre', 'numero'),
                'form': SalaForm(),
                'error_eliminar': f'No se puede eliminar la Sala {sala.numero} porque tiene funciones programadas.',
            })
        sala.delete()
        return redirect('salas')
    return redirect('salas')

def comprar_boletos_view(request, funcion_id):
    funcion = get_object_or_404(Funcion, id=funcion_id)
    
    if request.method == 'POST':
        asientos_str = request.POST.get('asientos')
        if asientos_str:
            asientos_list = asientos_str.split(',')
            usuario = None
            if request.session.get('usuario_id'):
                try:
                    usuario = Usuario.objects.get(id=request.session['usuario_id'])
                except Usuario.DoesNotExist:
                    pass
            for asiento in asientos_list:
                Boleto.objects.create(
                    funcion=funcion,
                    asiento=asiento,
                    precio=funcion.pelicula.costo_entrada,
                    usuario=usuario
                )
            return render(request, 'cartelera/compra_exitosa.html', {'funcion': funcion, 'asientos': asientos_list})
            
    asientos_ocupados = funcion.boletos.values_list('asiento', flat=True)
    context = {
        'funcion': funcion,
        'precio_boleto': funcion.pelicula.costo_entrada,
        'asientos_ocupados': list(asientos_ocupados)
    }
    return render(request, 'cartelera/comprar_boletos.html', context)
