from datetime import date
from modernrpc.core import rpc_method
from modernrpc.auth.basic import http_basic_auth_permissions_required
from modernrpc.auth.basic import http_basic_auth_login_required
from .models import Colonia, Gato


@rpc_method(name="alternar_comida_usuario")
def alternar_comida_usuario(colonia_slug, ano, mes, dia, **kwargs):
    request = kwargs['request']
    user = request.user
    colonia = Colonia.objects.get(slug=colonia_slug)
    fecha = date(ano, mes, dia)
    colonia.toggle_comida(fecha, user)
    print(fecha, user, colonia)
    return {}


@http_basic_auth_login_required
@rpc_method(name="avistar_gato")
def avistar_gato(colonia_slug, gato_slug, **kwargs):
    request = kwargs['request']
    gato = Gato.objects.get(slug=gato_slug)
    user = request.user
    gato.toggle_avistamiento(date.today(), user)
    return {}


@http_basic_auth_login_required
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
marcar_gato = gato_flow_factory("marcar")
liberar_gato = gato_flow_factory("liberar")
desaparecer_gato = gato_flow_factory("desaparecer")
olvidar_gato = gato_flow_factory("olvidar")
morir_gato = gato_flow_factory("morir")
