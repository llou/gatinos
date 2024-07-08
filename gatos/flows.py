from datetime import date
from viewflow.fsm import State
from .models import EstadoGato, Captura


def capturar_permission(flow, user):
    return user.has_perm('gatos.capturar_gato', obj=flow.gato)


def liberar_permission(flow, user):
    return user.has_perm('gatos.liberar_gato', obj=flow.gato)


def morir_permission(flow, user):
    return user.has_perm('gatos.morir_gato', obj=flow.gato)


def resucitar_permission(flow, user):
    return user.has_perm('gatos.resucitar_gato', obj=flow.gato)


class GatoFlow:
    estado = State(EstadoGato, default=EstadoGato.LIBRE)

    def __init__(self, gato):
        self.gato = gato

    @estado.setter()
    def _set_gato_estado(self, value):
        self.gato.estado = value

    @estado.getter()
    def _get_gato_estado(self):
        return self.gato.estado

    @estado.on_success()
    def _on_transittion_success(self, descriptor, source, target):
        self.gato.save()

    @estado.transition(source=EstadoGato.LIBRE, target=EstadoGato.CAPTURADO,
                       permission=capturar_permission)
    def capturar(self):
        captura = Captura(gato=self.gato, fecha_captura=date.today())
        captura.save()

    @estado.transition(source=EstadoGato.CAPTURADO, target=EstadoGato.LIBRE,
                       permission=liberar_permission)
    def liberar(self):
        capturas = self.gato.capturas.filter(fecha_liberacion=None)
        capturas = capturas.order_by("-fecha_captura")
        captura = capturas[0]
        captura.fecha_liberacion = date.today()
        captura.save()

    @estado.transition(source=EstadoGato.LIBRE,
                       target=EstadoGato.DESAPARECIDO)
    def desaparecer(self):
        pass

    @estado.transition(source=EstadoGato.DESAPARECIDO,
                       target=EstadoGato.OLVIDADO)
    def olvidar(self):
        pass

    @estado.transition(source=State.ANY, target=EstadoGato.MUERTO,
                       permission=morir_permission)
    def morir(self):
        self.muerto = True
        self.muerto_fecha = date.today()

    @estado.transition(source=EstadoGato.MUERTO, target=EstadoGato.LIBRE,
                       permission=resucitar_permission)
    def resucitar(self):
        self.muerto = False
        self.muerto_fecha = None

    def __repr__(self):
        c = self.__class__.__name__
        g = self.gato.nombre
        return f"<{c} gato={g}>"
