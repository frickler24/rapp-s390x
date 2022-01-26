from django.shortcuts import render

from .models import TblRollen
from .models import TblUserhatrolle


def panel_ungenutzte_rollen(request):
    """
    Zeige die Liste ungenutzter Rollen;
    Eine Rolle ist dann ungenutzt, wenn kein Element aus UserHatRolle einen Verweis auf den Rollennamen hat.
    :param request: wird Ignoriert
    :return: Gerendertes HTML
    """
    meldung = []

    genutzte_rollen = TblUserhatrolle.objects.values('rollenname').distinct()
    liste = TblRollen.objects.exclude(rollenname__in=genutzte_rollen)

    statistik(meldung, genutzte_rollen, liste)

    return render(
        request,
        'rapp/ungenutzte_rollen.html',
        context={
            'liste': liste,
            'meldung': meldung,
        },
    )


def statistik(meldung, genutzte_rollen, liste):
    """
    Ein bisschen statistische Information über den Nutzungsgrad der Rollen

    :param meldung: Hier werden die Informationen hieingepackt
    :param genutzte_rollen: Anzahl
    :param liste: Liste ungenutzter Rollen
    :return: Die Inhalte in meldung werden geändert
    """
    num_rollen_insgesamt = TblRollen.objects.all().count()
    num_genutzte_rollen = genutzte_rollen.count()
    num_ungenutzte_rollen = liste.count()
    meldung.append("Anzahl Rollen gesamt: {}, Anzahl genutzte Rollen: {}, Anzahl ungenutzter Rollen: {}"
                   .format(num_rollen_insgesamt, num_genutzte_rollen, num_ungenutzte_rollen))
