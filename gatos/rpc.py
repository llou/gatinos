from datetime import date
from django.contrib.auth.models import User
from modernrpc.core import rpc_method
from modernrpc.auth.basic import http_basic_auth_permissions_required
from .models import Colonia, Gato, Avistamiento


def get_fecha(fecha):
    return date.fromisoformat(fecha)


@rpc_method
def alternar_comida_usuario(colonia_slug, fecha, username):
    colonia = Colonia.objects.get(slug=colonia_slug)
    fecha = get_fecha(fecha)
    user = User.objects.get(username=username)
    colonia.toggle_comida(user, fecha)
    return "Ok"


@rpc_method
def avistar_gato(colonia_slug, gato_slug, username):
    avtos = Avistamiento.objects.filter(colonia__slug=colonia_slug,
                                        gato__slug=gato_slug,
                                        usuario__username=username)
    if not avtos:
        colonia = Colonia.objects.get(slug=colonia_slug)
        user = User.objects.get(username=username)
        gato = Gato.objects.get(colonia=colonia, slug=gato_slug)
        avto = Avistamiento(colonia=colonia, fecha=date.today(),
                            gato=gato, user=user)
        avto.save()
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
marcar_gato = gato_flow_factory("marcar")
liberar_gato = gato_flow_factory("liberar")
desaparecer_gato = gato_flow_factory("desaparecer")
olvidar_gato = gato_flow_factory("olvidar")
morir_gato = gato_flow_factory("morir")
