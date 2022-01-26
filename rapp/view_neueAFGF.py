# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect, HttpResponse

# Imports für die Selektions-Views panel, selektion u.a.
from django.shortcuts import render, redirect
from django.db import connection

import csv
import sys


# Zeige das Selektionspanel
def zeige_neue_afgf(request):
    """
    Finde alle AF/GF-Kombinationen, die aktuell nicht in tbl_AFListe abgebildet sind.
    Die Liste wird mit selektierten Checkboxen angezeigt.

    :param request: GET Request vom Browser
    :return: Gerendertes HTML
    """
    assert request.method != 'POST', 'Irgendwas ist im panel_UhR über POST angekommen'
    assert request.method == 'GET', 'Irgendwas ist im panel_UhR nicht über GET angekommen: ' + request.method

    liste = hole_liste()
    if len(liste) > 0:
        liste = list(liste)

    context = {
        'meineTabelle': liste,
        'gesamtzahl': len(liste),
        'AFGFzahl': len(hole_kurzeliste())
    }
    return render(request, 'rapp/neueAFGF_list.html', context)


def from_teil():
    return """
        FROM `tblGesamt`
        INNER JOIN tblUserIDundName
            ON tblGesamt.userid_und_name_id = tblUserIDundName.id
        LEFT JOIN tblUEbersichtAF_GFs
            ON tblGesamt.enthalten_in_af = tblUEbersichtAF_GFs.name_af_neu
            AND tblGesamt.gf = tblUEbersichtAF_GFs.name_gf_neu
    """


def bedingung():
    return """
        WHERE NOT tblGesamt.geloescht
            AND NOT tblUserIDundName.geloescht
            AND NOT tblGesamt.enthalten_in_af = "ka"
            AND tblUEbersichtAF_GFs.name_af_neu is null
            -- AND tblUserIDundName.zi_organisation = "AI-BA"
    """


def baue_sql(anfang, ende):
    """
    :param anfang: Das Select oder Insert oder was auch immer vor dem FROM-Teil
    :param ende: Das Order oder Group by oder nichts
    :return: das vollständige SQL
    """
    return anfang + from_teil() + bedingung() + ende


def hole_liste():
    """
    Hole die betreffenden AF/GF-Kombinationen mit Usernamen und IserIDs. django kann kein wirkliches group by...
        :return: Liste der Namen gefundener AF/GF-Kombinationen, alphabetisch sortiert
    """
    anfang = """
        -- Finde alle AF/GF für jeder UserID/Name aus tblGesamt, die es in der UebersichtAFGFs noch nicht gibt
        SELECT tblUserIDundName.name,tblUserIDundName.userid,
                tblGesamt.enthalten_in_af, tblGesamt.gf, tblGesamt.gf_beschreibung
    """

    ende = """
        GROUP BY tblUserIDundName.name,tblUserIDundName.userid, tblGesamt.enthalten_in_af, tblGesamt.gf;
    """
    sql = baue_sql(anfang, ende)

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql)
            liste = cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print('Fehler in hole_liste(): {}'.format(e))
            return None
        cursor.close()

    return liste


def hole_kurzeliste():
    """
    Hole die betreffenden AF/GF-Kombinationen. django kann kein wirkliches group by...
        :return: Liste der Namen gefundener AF/GF-Kombinationen, alphabetisch sortiert
    """
    anfang = """
        -- Finde alle AF/GF für jeder UserID/Name aus tblGesamt, die es in der UebersichtAFGFs noch nicht gibt
        SELECT tblGesamt.enthalten_in_af, tblGesamt.gf, tblGesamt.gf_beschreibung
    """
    ende = """
        GROUP BY tblGesamt.enthalten_in_af, tblGesamt.gf;
    """
    sql = baue_sql(anfang, ende)

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql)
            liste = cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print('Fehler in hole_kurzeliste(): {}'.format(e))
            return None
        cursor.close()

    return liste


def neue_afgf_download(request):
    """
    Exportfunktion für das Panel zum Selektieren neue AF/GF-Kombinationen.
    :param request: GET Request vom Browser
    :return: Gerendertes HTML
    """
    liste = list(hole_liste())

    response = HttpResponse(content_type="text/tsv")
    response['Content-Disposition'] = 'attachment; filename="neue_AFGF.csv"'
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)

    writer = csv.writer(response, csv.excel, delimiter='\t', quotechar='"')
    writer.writerow([
        'Name', 'UserID',
        'AF',
        'GF', 'GF-Beschreibung'
    ])

    for obj in liste:
        zeile = []
        for i in range(0, 5):
            zeile.append(obj[i])
        # print(zeile)
        writer.writerow(zeile)

    return response


def neueAFGF_setzen(request):
    """
    Setze alle bislang unbekannten AF/GF-Kombinationen in tbl_UebersiuchtAFGFs.
    Anschließend wird die tbl_AFListe aktualisiert über die Stored Procedure
    :param request: GET-Para,eter - wird ignoriert
    :return: Selbst nichts, aber den Returnwert der am Ende aufgerufenen Suchfunktion.
            Diese sollte keine Unbekannten AF/GF-Kombinationen mehr aufzeigen.
    """
    anfang = """
        INSERT INTO `tblUEbersichtAF_GFs`
            (`name_gf_neu`, `name_af_neu`, `kommentar`, `zielperson`, geloescht, `modelliert`)

            SELECT     `gf` as name_gf_neu,
                `enthalten_in_af` as name_af_neu,
                'Automatisch ergänzt' as kommentar,
                'Alle' as zielperson,
                0 as geloescht,
                now() as modelliert
    """
    ende = """
        GROUP BY tblGesamt.enthalten_in_af, tblGesamt.gf

        ON DUPLICATE KEY UPDATE
            `modelliert` = now(),
            geloescht = 0;    
    """
    sql = baue_sql(anfang, ende)

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql)
        except:
            e = sys.exc_info()[0]
            fehler = 'Error in neueAFGF_setzen(): {}'.format(e)
            return fehler
        cursor.close()

    with connection.cursor() as cursor:
        try:
            cursor.callproc("erzeuge_af_liste")  # diese SProc benötigt die Orga nicht als Parameter
        except:
            e = sys.exc_info()[0]
            fehler = 'Fehler in findeNeueAFGF(): {}'.format(e)
            print('Fehler Beim Erstellen der AFListe, StoredProc erzeuge_af_liste', fehler)
            return fehler
        cursor.close()

    return zeige_neue_afgf(request)
