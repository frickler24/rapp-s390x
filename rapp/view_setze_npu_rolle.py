import sys

from django.shortcuts import render

from .forms import FormNPUSetzen
from .models import Setze_NPU_namen_status
from django.db import connection


def panel_setze_npu_rolle(request):
    """
    Zeige das Formular zum Setzen der NPU-Rollen.
    Da keien Parameter abgefragt werden, das Setzen der Rollen aber einige Skeunden dauert.
    zeigen wir nur einen Los -geht's - Button und dann das Ergebnis.
    :param request: GET oder POST Request vom Browser
    :return: Gerendertes HTML
    """
    fehlermeldung = []
    meldung = None

    form = FormNPUSetzen()
    if request.method == 'POST':
        form = FormNPUSetzen(request.POST)
        if form.is_valid():
            meldung = setze_npu_rolle(fehlermeldung)

            print("panel_setze_npu_rolle:", len(fehlermeldung), fehlermeldung, meldung)
            if meldung:
                for e in meldung:
                    print(e)
            e = Setze_NPU_namen_status.objects.count()
            print(e)

    return render(
        request,
        'rapp/setze_npu_rollen.html',
        context={
            'form': form,
            'meldung': meldung,
            'fehlermeldung': fehlermeldung,
        },
    )


def setze_npu_rolle(fehlermeldung):
    """
    Die Stored Procedure wird aufgerufen.
    Das erwartete Ergebnis ist die Statistik, die von der SP geliefert wird.
    Fehlercodes sollten nicht auftreten - das weist dann auf gravierende Problem in der DB hin

    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: meldung - Das Ergebnis der Strored Procedure oder None im Fehlerfall
    """
    rufe_stored_proc(fehlermeldung)
    if len(fehlermeldung) == 0:
        return Setze_NPU_namen_status.objects.all()
    else:
        return None



def rufe_stored_proc(fehlermeldung):
    """
    Erledige den Job und gib Meldungen zurück, ob es geklappt zu haben scheint
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: --
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("rollen_fuer_NPU", [])
        except:
            e = sys.exc_info()[0]
            fehlermeldung.append('Error in Rollen_umbenennen: {}'.format(e))
            print(e)
            print(sys.exc_info())
        cursor.close()
