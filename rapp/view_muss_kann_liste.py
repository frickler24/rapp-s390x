import sys
from django.shortcuts import render
from django.db import connection
from rapp.forms import FormMussKann
from rapp.models import Muss_Kann_Liste


def panel_muss_kann(request):
    """
    Zeige das Formular zum Ermitteln der Rollen, zugehörigen AFen und Verteilung auf die User.
    und reagiere auf die POST-Nachricht entsprechend
    :param request: GET oder POST Request vom Browser - erwartet wird ein Orgasymbol, ggfs. gefolgt von %
    :return: Gerendertes HTML
    """
    meldung = []
    fehlermeldung = []
    muss_kann_liste = None

    form = FormMussKann()
    if request.method == 'POST':
        form = FormMussKann(request.POST)
        if form.is_valid():
            muss_kann_liste = muss_kann_ermitteln(form, meldung, fehlermeldung)

    return render(
        request,
        'rapp/muss_kann_liste.html',
        context={
            'form': form,
            'meldung': meldung,
            'fehlermeldung': fehlermeldung,
            'liste': muss_kann_liste,
        },
    )


def muss_kann_ermitteln(form, meldung, fehlermeldung):
    """
    Hier efolgt das eigentliche Ermitteln:

    :param form:
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: --
    """
    orgasymbol = form.cleaned_data['orgasymbol']
    rufe_stored_proc(orgasymbol, meldung, fehlermeldung)

    # Wenn wir bis hierhin keine Fehler haben, können wir die Tabelle lookformust_erg ermitteln und zurückliefern
    if fehlermeldung == []:
        return Muss_Kann_Liste.objects.all()
    else:
        return None


def rufe_stored_proc(orgasymbol, meldung, fehlermeldung):
    """
    Erledige den Job und gib Meldungen zurück, ob es geklappt zu haben scheint
    :param orgasymbol: Input-Param für die SP
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: --
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("muss_kann_rechte", [orgasymbol])
            meldung.append('Prozedur erfolgreich ausgeführt')
        except:
            e = sys.exc_info()[0]
            fehlermeldung.append('Es trat ein Fehler auf in muss_kann_rechte: {}'.format(e))
            print(e)
            print(sys.exc_info())
        cursor.close()
