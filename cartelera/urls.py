from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.cartelera_view, name='cartelera'),
    path('dashboard/', views.dashboard_empleado_view, name='dashboard_empleado'),
    path('pelicula/<int:pelicula_id>/', views.detalle_pelicula_view, name='detalle_pelicula'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agregar/', views.agregar_pelicula_view, name='agregar_pelicula'),
    path('agregar-funcion/', views.agregar_funcion_view, name='agregar_funcion'),
    path('funcion/<int:funcion_id>/comprar/', views.comprar_boletos_view, name='comprar_boletos'),
    path('pelicula/<int:pelicula_id>/editar/', views.editar_pelicula_view, name='editar_pelicula'),
    path('pelicula/<int:pelicula_id>/eliminar/', views.eliminar_pelicula_view, name='eliminar_pelicula'),
    path('api/buscar_tmdb/', views.search_tmdb_view, name='search_tmdb_api'),
    path('api/detalles_tmdb/', views.detalles_tmdb_view, name='detalles_tmdb_api'),
    path('api/horarios_disponibles/', views.horarios_disponibles_view, name='horarios_disponibles_api'),
    path('generos/', views.generos_view, name='generos'),
    path('generos/<int:genero_id>/editar/', views.editar_genero_view, name='editar_genero'),
    path('generos/<int:genero_id>/eliminar/', views.eliminar_genero_view, name='eliminar_genero'),
    path('salas/', views.salas_view, name='salas'),
    path('salas/<int:sala_id>/editar/', views.editar_sala_view, name='editar_sala'),
    path('salas/<int:sala_id>/eliminar/', views.eliminar_sala_view, name='eliminar_sala'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('usuarios/<int:usuario_id>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('usuarios/<int:usuario_id>/eliminar/', views.eliminar_usuario_view, name='eliminar_usuario'),
    
    # Rutas secretas de AllAuth
    path('accounts/', include('allauth.urls')),
]
