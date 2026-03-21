from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorador para verificar si el usuario tiene uno de los roles permitidos
    basado en la sesión de Django.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            rol_usuario = request.session.get('usuario_rol')
            
            if rol_usuario in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Si no tiene el rol, redirigir con un mensaje
            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect('cartelera')
            
        return _wrapped_view
    return decorator
