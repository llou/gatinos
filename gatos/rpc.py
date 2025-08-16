from datetime import date, datetime
from modernrpc.core import rpc_method
from modernrpc.auth.basic import http_basic_auth_permissions_required
from modernrpc.auth.basic import http_basic_auth_login_required
from .models import Colonia, Gato, CodigoCalendarioComidas, AsignacionComida
from .decorators import colony_access_required, require_colony_permission


@rpc_method(name="alternar_comida_usuario")
def alternar_comida_usuario(colonia_slug, ano, mes, dia, **kwargs):
    request = kwargs['request']
    user = request.user
    colonia = Colonia.objects.get(slug=colonia_slug)
    
    # Check if user has access to this colony
    if not colonia.user_has_access(user):
        return {"error": "No tiene acceso a esta colonia"}
    
    fecha = date(ano, mes, dia)
    colonia.toggle_comida(fecha, user)
    return {}


@http_basic_auth_login_required
@rpc_method(name="set_feeding_assignment")
def set_feeding_assignment(date_str, colonia_id, user_id=None, **kwargs):
    """Set feeding assignment for a specific date
    
    Args:
        date_str: Date in YYYY-MM-DD format
        colonia_id: Colony ID
        user_id: User ID to assign (None or 0 to unassign)
    """
    request = kwargs.get('request')
    if not request or not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Parse date string (YYYY-MM-DD format)
        fecha = datetime.strptime(date_str, "%Y-%m-%d").date()
        colonia = Colonia.objects.get(id=colonia_id)
        
        # Check if user has access to this colony
        if not colonia.user_has_access(request.user):
            return {"error": "No tiene acceso a esta colonia"}
        
        # Check if user has permission to feed
        if not request.user.has_perm('gatos.alimentar_colonia'):
            return {"error": "Permission denied"}
        
        # Check if user is admin
        is_admin = request.user.is_superuser or request.user.is_staff
        
        # Get current assignment for this date
        current_assignment = AsignacionComida.objects.filter(
            colonia=colonia,
            fecha=fecha
        ).first()
        
        # For normal users, they can only assign/unassign themselves
        if not is_admin:
            # Check if there's an existing assignment by another user
            if current_assignment and current_assignment.usuario_id != request.user.id:
                # Cannot modify another user's assignment
                return {"error": "No puede modificar la asignación de otro usuario"}
            
            # If user_id is provided and it's not the current user, deny
            if user_id and user_id != request.user.id:
                return {"error": "No puede asignar a otro usuario"}
            
            # Default to toggling current user
            if user_id is None:
                if current_assignment and current_assignment.usuario_id == request.user.id:
                    user_id = 0  # Unassign
                else:
                    user_id = request.user.id  # Assign self
        
        # Delete current assignment
        AsignacionComida.objects.filter(colonia=colonia, fecha=fecha).delete()
        
        # Create new assignment if user_id is provided and not 0
        if user_id: 
            try:
                target_user = User.objects.get(id=user_id)
                AsignacionComida.objects.create(
                    colonia=colonia,
                    fecha=fecha,
                    usuario=target_user
                )
                return {
                    "assigned": True,
                    "user_id": target_user.id,
                    "username": target_user.username,
                    "full_name": f"{target_user.first_name} {target_user.last_name}".strip() or target_user.username
                }
            except User.DoesNotExist:
                return {"error": "Usuario no encontrado"}
        else:
            # No assignment
            return {
                "assigned": False,
                "user_id": None,
                "username": None,
                "full_name": None
            }
            
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Exception as e:
        return {"error": str(e)}


@http_basic_auth_login_required
@rpc_method(name="toggle_feeding_date")
def toggle_feeding_date(date_str, colonia_id, **kwargs):
    """Simple toggle for backward compatibility - just toggles current user"""
    return set_feeding_assignment(date_str, colonia_id, None, **kwargs)


@rpc_method(name="get_colony_feeding_users")
def get_colony_feeding_users(colonia_id, **kwargs):
    """Get list of users who can be assigned to feed in a colony"""
    request = kwargs.get('request')
    
    try:
        colonia = Colonia.objects.get(id=colonia_id)
        
        # Check if user has access to this colony
        if request and hasattr(request, 'user') and not colonia.user_has_access(request.user):
            return {"error": "No tiene acceso a esta colonia"}
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active users with feeding permission
        available_users = []
        seen_ids = set()
        
        for u in User.objects.filter(is_active=True):
            if u.has_perm('gatos.alimentar_colonia') and u.id not in seen_ids:
                available_users.append({
                    'id': u.id,
                    'username': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'full_name': f"{u.first_name} {u.last_name}".strip() or u.username
                })
                seen_ids.add(u.id)
        
        # Check if current user is admin
        is_admin = False
        current_user_id = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_admin = request.user.is_superuser or request.user.is_staff
            current_user_id = request.user.id
            
            # If admin user doesn't have feeding permission, add them to the list
            if is_admin and current_user_id not in seen_ids:
                available_users.append({
                    'id': current_user_id,
                    'username': request.user.username,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                })
                seen_ids.add(current_user_id)
        
        # Sort by ID for consistent ordering
        available_users.sort(key=lambda x: x['id'])
        
        return {
            "users": available_users,
            "is_admin": is_admin,
            "current_user_id": current_user_id
        }
        
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Exception as e:
        return {"error": str(e)}


@rpc_method(name="get_feeding_dates")
def get_feeding_dates(colonia_id, start_date=None, end_date=None, **kwargs):
    """Get feeding dates for a colony to display on calendar"""
    request = kwargs.get('request')
    
    try:
        colonia = Colonia.objects.get(id=colonia_id)
        
        # Check if user has access to this colony (if request is provided)
        if request and request.user and not colonia.user_has_access(request.user):
            return {"error": "No tiene acceso a esta colonia"}
        
        # Get current user for comparison
        current_user = request.user if request and hasattr(request, 'user') else None
        
        # Query feeding assignments
        query = AsignacionComida.objects.filter(colonia=colonia)
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(fecha__gte=start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(fecha__lte=end)
        
        # Group by date and return user info (colors determined on frontend)
        dates = []
        for asignacion in query:
            dates.append({
                "date": asignacion.fecha.strftime("%Y-%m-%d"),
                "user_id": asignacion.usuario.id if asignacion.usuario else None,
                "username": asignacion.usuario.username if asignacion.usuario else None,
                "full_name": f"{asignacion.usuario.first_name} {asignacion.usuario.last_name}".strip() or asignacion.usuario.username if asignacion.usuario else None
            })
        
        # Check if current user is admin (only superuser or staff)
        is_admin = False
        if current_user and current_user.is_authenticated:
            is_admin = current_user.is_superuser or current_user.is_staff
        
        return {"dates": dates, "is_admin": is_admin}
        
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Exception as e:
        return {"error": str(e)}


@http_basic_auth_login_required
@rpc_method(name="avistar_gato")
def avistar_gato(colonia_slug, gato_slug, **kwargs):
    request = kwargs['request']
    gato = Gato.objects.get(slug=gato_slug)
    user = request.user
    gato.toggle_avistamiento(date.today(), user)
    return {}


@http_basic_auth_login_required
@rpc_method(name="nuevo_codigo_qr")
def nuevo_codigo_qr(**kwargs):
    request = kwargs['request']
    CodigoCalendarioComidas.objects.filter(user=request.user).delete()
    nc = CodigoCalendarioComidas(user=request.user)
    nc.save()
    return "Ok"


@http_basic_auth_login_required
@rpc_method(name="borrar_codigo_qr")
def borrar_codigo_qr(**kwargs):
    request = kwargs['request']
    CodigoCalendarioComidas.objects.filter(user=request.user).delete()
    return "Ok"


@rpc_method(name="get_colony_activity")
def get_colony_activity(colonia_slug, **kwargs):
    """Get activity data for a colony to display in activity chart"""
    try:
        colonia = Colonia.objects.get(slug=colonia_slug)
        
        # Check if user has access to this colony if request is provided
        request = kwargs.get('request')
        if request and hasattr(request, 'user') and not colonia.user_has_access(request.user):
            return {"error": "No tiene acceso a esta colonia"}
        
        # Get activity dates for the colony
        activity_dates = colonia.get_actividad()
        dates = [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in activity_dates]
        
        return {"dates": dates, "colony_name": colonia.nombre}
        
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Exception as e:
        return {"error": str(e)}


@rpc_method(name="get_cat_activity")
def get_cat_activity(colonia_slug, gato_slug, **kwargs):
    """Get activity data for a cat to display in activity chart"""
    try:
        colonia = Colonia.objects.get(slug=colonia_slug)
        gato = Gato.objects.get(slug=gato_slug, colonia=colonia)
        
        # Check if user has access to this colony if request is provided
        request = kwargs.get('request')
        if request and hasattr(request, 'user') and not colonia.user_has_access(request.user):
            return {"error": "No tiene acceso a esta colonia"}
        
        # Get activity dates for the cat
        activity_dates = gato.get_actividad()
        dates = [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in activity_dates]
        
        return {"dates": dates, "cat_name": gato.nombre}
        
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Gato.DoesNotExist:
        return {"error": "Cat not found"}
    except Exception as e:
        return {"error": str(e)}


def gato_flow_factory(action_name):
    rpc_name = f"gato.{action_name}"
    perm_name = f"gatos.gato_{action_name}"
    func_name = f"{action_name}_gato"

    @rpc_method(name=rpc_name)
    @http_basic_auth_permissions_required(permissions=[perm_name])
    def function(colonia_slug, gato_slug):

        colonia = Colonia.objects.get(slug=colonia_slug)
        gato = Gato.objects.get(colonia=colonia, slug=gato_slug)
        flow = gato.get_flow()
        return getattr(flow, action_name)()

    function.__name__ = func_name
    function.__doc__ = ""
    return function


capturar_gato = gato_flow_factory("capturar")
liberar_gato = gato_flow_factory("liberar")
desaparecer_gato = gato_flow_factory("desaparecer")
olvidar_gato = gato_flow_factory("olvidar")
morir_gato = gato_flow_factory("morir")
