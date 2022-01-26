import sys

from django.shortcuts import render

from .forms import FormUmbenennen
from .models import TblRollen
from django.db import connection


def panel_rolle_umbenennen(request):
    """
    Zeige das Formular zum Umbenennen von Rollen und reagiere auf die POST-Nachricht entsprechend
    :param request: GET oder POST Request vom Browser
    :return: Gerendertes HTML
    """
    meldung = list()
    fehlermeldung = []

    form = FormUmbenennen()
    if request.method == 'POST':
        form = FormUmbenennen(request.POST)
        if form.is_valid():
            af_umbenennen(form, meldung, fehlermeldung)

    return render(
        request,
        'rapp/rolle_umbenennen.html',
        context={
            'form': form,
            'meldung': meldung,
            'fehlermeldung': fehlermeldung,
        },
    )


def af_umbenennen(form, meldung, fehlermeldung):
    """
    Hier efolgt das eigentliche Umbenennen: Zunächst wird geprüft, ob der alte Name existiert und der neue Name nicht.
    Falls die Vorbedingungen OK sind, wird das Umbenennen über eine Stored Procedure ausgeführt
    und anschließend das Ergbenis geprüft.

    :param form:
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: --
    """
    alter_name = form.cleaned_data['alter_name']
    neuer_name = form.cleaned_data['neuer_name']

    # Schau nach, ob nur der alte Name existiert
    altok = TblRollen.objects.filter(rollenname=alter_name).count() == 1
    neuok = TblRollen.objects.filter(rollenname=neuer_name).count() == 0
    if not neuok or not altok:
        name_falsch(alter_name, neuer_name, altok, neuok, fehlermeldung)
    else:
        rufe_stored_proc(alter_name, neuer_name, meldung, fehlermeldung)
        kontrolliere_ergebnis(alter_name, neuer_name, meldung, fehlermeldung)


def name_falsch(alter_name, neuer_name, altok, neuok, fehlermeldung):
    """
    Da ist mindestens einer der beiden Namen falsch, die Fehlermeldungen werden geeignet aufbereitet

    :param alter_name: Der sollte noch existieren
    :param neuer_name: Der sollte noch nicht existieren
    :param altok: Flag: Ist er wirklich  da?
    :param neuok: Flag: Ist er wirklich nicht da?
    :param fehlermeldung: Da steht dann drin, was passiert ist
    :return: --
    """
    if not altok:
        fehlermeldung.append("Der bestehende Rollenname '{}' existiert nicht.".format(alter_name))
    if not neuok:
        fehlermeldung.append("Der neue Rollenname '{}' existiert bereits.".format(neuer_name))


def rufe_stored_proc(alter_name, neuer_name, meldung, fehlermeldung):
    """
    Erledige den Job und gib Meldungen zurück, ob es geklappt zu haben scheint
    :param alter_name: Input-Param für die SP
    :param neuer_name: Input-Param für die SP
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return: --
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("rolle_umbenennen", [alter_name, neuer_name])
            meldung.append('Prozedur ausgeführt')
        except:
            e = sys.exc_info()[0]
            fehlermeldung.append('Error in Rollen_umbenennen: {}'.format(e))
            print(e)
            print(sys.exc_info())
        cursor.close()


def kontrolliere_ergebnis(alter_name, neuer_name, meldung, fehlermeldung):
    """
    Schau nach, ob nun der alte Name nicht mehr existiert und der neue Name existiert

    :param alter_name: Der sollte nun nicht mehr existieren
    :param neuer_name: Der sollte nun  existieren
    :param meldung: Hier sammeln sich Erfolgsmeldungen fürs UI
    :param fehlermeldung: Hier sammeln sich Fehlermeldungen fürs UI
    :return:
    """
    altok = TblRollen.objects.filter(rollenname=alter_name).count() == 0
    neuok = TblRollen.objects.filter(rollenname=neuer_name).count() == 1
    if not neuok or not altok:
        falsches_ergebnis(alter_name, neuer_name, altok, neuok, fehlermeldung)
    else:
        meldung.append('Habe folgende Umbenennung durchgeführt:')


def falsches_ergebnis(alter_name, neuer_name, altok, neuok, fehlermeldung):
    """
    Da hat wohl was nicht geklappt, die Fehlermeldungen werden entsprechend aufbereitet fürs UI

    :param alter_name: Der sollte nun nicht mehr existieren
    :param neuer_name: Der sollte nun  existieren
    :param altok: Flag: Ist er wirklich nicht da?
    :param neuok: Flag: Ist er wirklich da?
    :param fehlermeldung: Da steht dann drin, was passiert ist
    :return: --
    """
    if not altok:
        fehlermeldung \
            .append("Der bestehende Rollenname '{}' existiert immer noch."
                    .format(alter_name))
    if not neuok:
        fehlermeldung \
            .append("Der neue Rollenname '{}' existiert nach Umbenennen doch nicht."
                    .format(neuer_name))
