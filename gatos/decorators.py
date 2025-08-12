"""
Custom decorators for access control in the gatos app
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Colonia


def colony_access_required(view_func=None, get_colony_id=None):
    """
    Decorator that checks if a user has access to a colony.
    
    Usage:
        @colony_access_required
        def my_view(request, colonia, ...):
            # colonia is the slug
            
        @colony_access_required(get_colony_id=lambda kwargs: kwargs.get('colonia_id'))
        def my_rpc_method(colonia_id, **kwargs):
            # For RPC methods that use colonia_id
    """
    def decorator(func):
        @wraps(func)
        def _wrapped_view(request_or_self, *args, **kwargs):
            # Handle both function-based views and methods
            if hasattr(request_or_self, '__class__'):
                # It's a class-based view
                request = request_or_self.request if hasattr(request_or_self, 'request') else args[0]
                view_kwargs = kwargs
            else:
                # It's a function-based view or RPC method
                request = request_or_self
                view_kwargs = kwargs if kwargs else (args[0] if args else {})
            
            # For RPC methods, request might be in kwargs
            if 'request' in view_kwargs:
                request = view_kwargs['request']
            
            # Get user from request
            user = getattr(request, 'user', None)
            
            if not user or not user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            # Skip check for superusers
            if user.is_superuser:
                return func(request_or_self, *args, **kwargs)
            
            # Get colony identifier
            colony_identifier = None
            
            if get_colony_id:
                # Custom function to get colony ID
                colony_identifier = get_colony_id(view_kwargs)
                if colony_identifier:
                    try:
                        colonia = Colonia.objects.get(id=colony_identifier)
                    except (Colonia.DoesNotExist, ValueError):
                        colonia = None
                else:
                    colonia = None
            elif 'colonia' in view_kwargs:
                # Colony slug in kwargs
                colonia = get_object_or_404(Colonia, slug=view_kwargs['colonia'])
            elif 'colonia_slug' in view_kwargs:
                # Colony slug with different name
                colonia = get_object_or_404(Colonia, slug=view_kwargs['colonia_slug'])
            elif 'colonia_id' in view_kwargs:
                # Colony ID in kwargs
                colonia = get_object_or_404(Colonia, id=view_kwargs['colonia_id'])
            else:
                # Try to get from self (class-based views)
                if hasattr(request_or_self, 'colonia'):
                    colonia = request_or_self.colonia
                else:
                    raise ValueError("Cannot determine colony from request")
            
            # Check access
            if colonia and not colonia.user_has_access(user):
                raise PermissionDenied(f"No tiene acceso a la colonia '{colonia.nombre}'")
            
            return func(request_or_self, *args, **kwargs)
        
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator


def require_colony_permission(permission_name):
    """
    Decorator that checks both colony access and specific permission.
    
    Usage:
        @require_colony_permission('gatos.add_gato')
        def my_view(request, colonia, ...):
            pass
    """
    def decorator(func):
        @wraps(func)
        def _wrapped_view(*args, **kwargs):
            # For RPC methods, all parameters come through kwargs
            # Get request object
            request = kwargs.get('request')
            
            if not request:
                # Try to get from args for regular views
                if args and hasattr(args[0], 'user'):
                    request = args[0]
                elif args and hasattr(args[0], 'request'):
                    request = args[0].request
            
            if not request:
                raise ValueError("Cannot determine request object")
            
            user = getattr(request, 'user', None)
            
            if not user or not user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            # Skip permission check for superusers
            if user.is_superuser:
                return func(*args, **kwargs)
            
            # Check colony access
            colonia = None
            if 'colonia_id' in kwargs:
                try:
                    from .models import Colonia
                    colonia = Colonia.objects.get(id=kwargs['colonia_id'])
                    if not colonia.user_has_access(user):
                        raise PermissionDenied(f"No tiene acceso a la colonia '{colonia.nombre}'")
                except Colonia.DoesNotExist:
                    raise PermissionDenied("Colonia no encontrada")
            
            # Check specific permission
            if not user.has_perm(permission_name):
                raise PermissionDenied(f"Permission '{permission_name}' required")
            
            return func(*args, **kwargs)
        
        return _wrapped_view
    
    return decorator