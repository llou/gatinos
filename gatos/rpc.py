from datetime import date, datetime
from modernrpc.core import rpc_method
from modernrpc.auth.basic import http_basic_auth_permissions_required
from modernrpc.auth.basic import http_basic_auth_login_required
from .models import Colonia, Gato, CodigoCalendarioComidas, AsignacionComida


@rpc_method(name="alternar_comida_usuario")
def alternar_comida_usuario(colonia_slug, ano, mes, dia, **kwargs):
    request = kwargs['request']
    user = request.user
    colonia = Colonia.objects.get(slug=colonia_slug)
    fecha = date(ano, mes, dia)
    colonia.toggle_comida(fecha, user)
    return {}


@http_basic_auth_login_required
@rpc_method(name="toggle_feeding_date")
def toggle_feeding_date(date_str, colonia_id, current_color=None, **kwargs):
    """Toggle feeding date for colony calendar - compatible with Vue component"""
    request = kwargs.get('request')
    if not request or not request.user.is_authenticated:
        return {"error": "Authentication required"}
    
    try:
        # Parse date string (YYYY-MM-DD format)
        fecha = datetime.strptime(date_str, "%Y-%m-%d").date()
        colonia = Colonia.objects.get(id=colonia_id)
        
        # Check if user has permission
        if not request.user.has_perm('gatos.alimentar_colonia'):
            return {"error": "Permission denied"}
        
        # Toggle the feeding assignment
        colonia.toggle_comida(fecha, request.user)
        
        # Check if date is now assigned
        asignacion = AsignacionComida.objects.filter(
            colonia=colonia,
            fecha=fecha,
            usuario=request.user
        ).first()
        
        # Return appropriate color based on assignment
        if asignacion:
            return {"color": "green", "assigned": True}
        else:
            return {"color": None, "assigned": False}
            
    except Colonia.DoesNotExist:
        return {"error": "Colony not found"}
    except Exception as e:
        return {"error": str(e)}


@rpc_method(name="get_feeding_dates")
def get_feeding_dates(colonia_id, start_date=None, end_date=None, **kwargs):
    """Get feeding dates for a colony to display on calendar"""
    try:
        colonia = Colonia.objects.get(id=colonia_id)
        
        # Query feeding assignments
        query = AsignacionComida.objects.filter(colonia=colonia)
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(fecha__gte=start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(fecha__lte=end)
        
        # Group by date and return with color based on user
        dates = []
        for asignacion in query:
            dates.append({
                "date": asignacion.fecha.strftime("%Y-%m-%d"),
                "color": "green" if asignacion.usuario else "blue",
                "user": asignacion.usuario.username if asignacion.usuario else None
            })
        
        return {"dates": dates}
        
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
