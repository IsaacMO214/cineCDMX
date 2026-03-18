from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Usuario, RolUsuario

@receiver(user_signed_up)
def crear_usuario_cine_desde_google(request, user, **kwargs):
    """
    Este es el 'Espía' (Signal).
    Cada vez que django-allauth loguea o registra exitosamente a alguien por Google,
    dispara este evento. Aquí tomamos sus datos y lo insertamos silenciosamente
    en nuestra tabla personalizada 'Usuario' para que tenga Rol y Sucursal.
    """
    
    # Intentamos obtener o crear el usuario en nuestra propia BD
    usuario_cine, creado = Usuario.objects.get_or_create(
        correo=user.email,
        defaults={
            'nombre': f"{user.first_name} {user.last_name}".strip() or user.username,
            'password': 'NoAplica_SeLogueaPorGoogle',
            'rol': RolUsuario.CLIENTE,
            # 'sucursal': null por defecto, o la sucursal predeterminada si tuvieras una.
        }
    )
    
    # Hack: Le "inyectamos" las variables de sesión tal como lo hicimos en el login manual
    # para que las pantallas de Django sepan identificar su Rol y su Nombre.
    if request:
        request.session['usuario_id'] = usuario_cine.id
        request.session['usuario_nombre'] = usuario_cine.nombre
        request.session['usuario_rol'] = usuario_cine.rol
