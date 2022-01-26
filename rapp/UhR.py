# Der Fabric-Verteiler

from rapp.EinzelUhR import EinzelUhr
from rapp.RollenListenUhR import RollenListenUhr
from rapp.NeueListenUhR import NeueListenUhr
from rapp.AFListenUhR import AFListenUhr


# Fabric für das Behandeln von Rollenzuordnungen
class UhR(object):
    def factory(typ):
        if typ == 'einzel':
            return EinzelUhr()
        if typ == 'rolle':
            return RollenListenUhr()
        if typ == 'nur_neue':
            return NeueListenUhr()
        if typ == 'af':
            return AFListenUhr()
        assert 0, "Falsche Factory-Typ in Uhr: " + typ

    factory = staticmethod(factory)
