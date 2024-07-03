from viewflow.fsm import State
from .models import EstadoGato


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
        self.report.save()

    @estado.transition(source=EstadoGato.LIBRE, target=EstadoGato.MARCADO)
    def marcar(self):
        pass

    @estado.transition(source=EstadoGato.MARCADO, target=EstadoGato.LIBRE)
    def desmarcar(self):
        pass

    @estado.transition(source=EstadoGato.MARCADO, target=EstadoGato.CAPTURADO)
    def capturar(self):
        pass

    @estado.transition(source=EstadoGato.CAPTURADO, target=EstadoGato.LIBRE)
    def liberar(self):
        pass

    @estado.transition(EstadoGato.LIBRE, target=EstadoGato.DESAPARECIDO)
    def desaparecer(self):
        pass

    @estado.transition(EstadoGato.DESAPARECIDO, target=EstadoGato.OLVIDADO)
    def olvidar(self):
        pass

    @estado.transition(State.ANY, target=EstadoGato.MUERTO)
    def morir(self):
        pass
