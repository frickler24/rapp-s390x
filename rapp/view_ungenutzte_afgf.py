import sys
from django.http.response import HttpResponse

from django.shortcuts import render
from django.db import connection


def panel_ungenutzte_afgf(request):
    """
    Zeige die Liste ungenutzter AF/GF-Kombinationen;
    Eine AF/GF-Kombination ist dann ungenutzt, wenn kein Element aus RolleHatAF einen Verweis auf die Kombination hat.
    :param request: wird Ignoriert
    :return: Gerendertes HTML
    """

    if request.method != 'GET':
        return HttpResponse("Fehlerhafter Aufruf in panel_ungenutzte_afgf")

    antwort, fehler = hole_daten()
    return render(
        request, 'rapp/ungenutzte_afgf.html', context={
            'antwort': antwort,
            'fehler': fehler,
        },
    )


def hole_daten():
    """
    Ausführen der Stored Procedure ungenutzteAFGF
    :return: Das Antwort-Array und gegebenenfalls Fehlerinformationen
    """
    antwort = {}
    fehler = None

    with connection.cursor() as cursor:
        try:
            cursor.callproc("ungenutzteAFGF")
            tmp = cursor.fetchall()
            for line in tmp:
                antwort[line[0]] = (line[1], line[2])
        except:
            e = sys.exc_info()[0]
            fehler = 'Error in Stored Procedure ungenutzteAFGF: {}'.format(e)
            print(fehler)
    cursor.close()
    return antwort, fehler
