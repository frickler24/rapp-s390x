# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, zipfile
from io import BytesIO

from django.db import connection
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone


def latex_header():
    s = """\\documentclass[a4paper,landscape,12pt]{letter}
    \\usepackage[paper=a4paper,height=18cm,left=25mm,right=20mm,width=22cm]{geometry}
    \\usepackage[ngerman]{babel} % Deutsche Einstellungen Syntaxcheck
    \\usepackage[utf8]{inputenc} % Eingabe-Encoding
    \\usepackage[T1]{fontenc}    % Ausgaben mit vollen Fonts
    \\usepackage{csquotes}
    %\\usepackage{pdflscape}
    \\usepackage{longtable}
    \\usepackage{xcolor}

    
    \\parindent0cm
    \\pagestyle{headings}
    
    \\title{\\textbf{Betreff:} Rechtezuordnung als Direct Connect}
    \\date{\\today}
    
    \\address{G\\_BA-Rezertifizierung\\\\ZI-AI-BA}
    
    \\begin{document}
    \\pagestyle{headings}
    
    """
    return s + "\n"


def hole_identitaeten():
    """
    Hole nur erst mal die Namen der betroffenen User.
        :return: Liste der Namen betroffener User, alphabetisch sortiert
    """
    sql = """
        SELECT     rapp_direktverbindungen.identitaet
            FROM rapp_direktverbindungen
                INNER JOIN rapp_modellierung
                ON rapp_direktverbindungen.entitlement = rapp_modellierung.entitlement
                -- WHERE COALESCE(rapp_direktverbindungen.nicht_anmailen, '') != 'x'
                -- WHERE rapp_direktverbindungen.identitaet LIKE 'Peter%'
                -- WHERE account_name not like "%xv86%" AND account_name not like "J98TB%"
        GROUP BY rapp_direktverbindungen.identitaet
        ORDER BY rapp_direktverbindungen.identitaet ASC;
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql)
            liste = cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print('Fehler in hole_identitaeten(): {}'.format(e))
            return None
        cursor.close()

    return liste


def hole_userids(name):
    sql = """
        -- Hole nur erst mal die Accounts (UserIDs) zu einem Namen
        SELECT     rapp_direktverbindungen.account_name
            FROM rapp_direktverbindungen
                INNER JOIN rapp_modellierung
                ON rapp_direktverbindungen.entitlement = rapp_modellierung.entitlement
                -- WHERE COALESCE(rapp_direktverbindungen.nicht_anmailen, '') != 'x'
            WHERE identitaet = %s
        GROUP BY rapp_direktverbindungen.account_name
        ORDER BY rapp_direktverbindungen.account_name DESC;
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql, name)
            liste = cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print('Error in hole_userids(): {}'.format(e))
            return None
        cursor.close()

    return liste


def latex_adresse(userid):
    userid = userid.lower()
    s = "\\begin{letter}{"
    s += "{}@ruv.de".format(userid)
    if userid[1] != "v" or userid.startswith("xv86"):  # Technischer User
        s += "\\space\\space\\space\\space\\space\\space\\space\\space\\space\\bfseries\\colorbox{red}{Achtung, Technischer User}"
    s += "\\hfill \\break"
    s += "}"
    return s + "\n"


def latex_anrede(name):
    s = """\\begin{normalsize}
    \\opening{\\textbf{Betreff:} Rechtezuordnung als \\emph{Direct Connect}}
    \\begin{normalsize} \\hfill
    \\end{normalsize}

    \\begin{normalsize}
        Guten Tag, 
    """
    s += "{},".format(name)
    s += """ \\hfill \\break
    \\end{normalsize}
    \\end{normalsize}
    """
    return s + "\n"


def latex_einleitungstext():
    s = """\\begin{normalsize}
    Ihnen sind derzeit eines oder mehrere Rechte als sogenannte \\emph{Direct Connects} zugeordnet.
    
    Diese Zuordnung wird zum 01.06.2019 im Rahmen der aktuellen Rezertifizierung der Berechtigungen gelöscht.
    
    Falls Sie die unten aufgeführte Berechtigung nicht für Ihre Aufgaben benötigen, 
    brauchen Sie nichts weiter zu veranlassen.
    
    Anderenfalls wenden Sie sich bitte rechtzeitig an Ihre IT-Betreuer 
    und lassen Sie sich die bestgeeignete der unten angegebenen Arbeitsplatzfunktionen zuordnen.
    \\end{normalsize}
    """
    return s + "\n"


def hole_daten(name):
    sql = """
        SELECT     rapp_direktverbindungen.entitlement,
                rapp_direktverbindungen.applikation,
                rapp_direktverbindungen.identitaet,
                rapp_direktverbindungen.account_name,
                rapp_modellierung.af,
                rapp_modellierung.neue_beschreibung as `neue_beschreibung_der_af`,
                rapp_modellierung.beschreibung_der_af as `alte_beschreibung_der_af`
        
            FROM `rapp_direktverbindungen`
                INNER JOIN rapp_modellierung
                ON rapp_direktverbindungen.entitlement = rapp_modellierung.entitlement
            -- WHERE COALESCE(rapp_direktverbindungen.nicht_anmailen, '') != 'x'
                WHERE identitaet = %s
        GROUP BY rapp_modellierung.af
        ORDER BY rapp_direktverbindungen.entitlement;
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(sql, name)
            liste = cursor.fetchall()
        except:
            e = sys.exc_info()[0]
            print('Error in hole_daten(): {}'.format(e))
            return None
        cursor.close()

    return liste


def erzeuge_tf_menge(datenzeilen):
    """
    Erzeugt aus den Datenzeile eine Menge der TFs und liefert sie als String zurück.
    Die einzelnen Elemente der Menge werden durch \\ voneinander getrennt (LaTex: Neue Zeile)
    :param datenzeilen:
    :return:
    """
    tfs = {zeile[0] for zeile in datenzeilen}
    s = "".join(escape_element(tf) + "\\\\" for tf in sorted(list(tfs)))
    return s + "\n"


def latex_tf_liste(datenzeilen):
    s = """\\begin{normalsize}
    Nachfolgend die Liste der Ihnen direkt zugeordneten technischen Funktionen (TF):

    \\begin{longtable}{l}
        Entitlement (TF) \\\\ \\hline
        \\endfirsthead
        \\multicolumn{1}{@{}l}{\\ldots Fortsetzung}\\\\\\hline
        Entitlement (TF) \\\\ \\hline
        \\endhead % all the lines above this will be repeated on every page
        \\multicolumn{1}{r@{}}{Fortsetzung \\ldots}\\\\
        \\endfoot
        \\hline
        \\endlastfoot
    """
    s += erzeuge_tf_menge(datenzeilen)
    s += """    \\end{longtable}
    \\end{normalsize}
    """
    return s + "\n"


def latex_tabellenkopf():
    s = """\\begin{normalsize}
    Zum besseren Bewerten der Handlungsoptionen zeigt die nachfolgende Tabelle 
    die heute bereits modellierten Arbeitsplatzfunktionen (AF)
    zu den oben aufgeführten \emph{Direct Connects}:
    \\end{normalsize}
    \\begin{tiny}
    \\begin{longtable}{|p{35mm}|p{15mm}|p{25mm}|p{10mm}|p{40mm}|p{50mm}|p{50mm}|}
        \\hline
        Entitlement (TF) 
        & Applikation 
        & Identität 
        & Account-Name 
        & AF 
        & Neue Beschreibung der AF 
        & Alte Beschreibung der AF\\\\ \\hline
        \\endfirsthead
        \\multicolumn{7}{@{}l}{\\ldots Fortsetzung}\\\\\\hline
        Entitlement (TF) & Applikation & Identität & Account-Name & AF & Neue Beschreibung der AF & Alte Beschreibung der AF\\\\ \\hline
        \\endhead % all the lines above this will be repeated on every page
        \\hline \\multicolumn{7}{r@{}}{Fortsetzung \\ldots}\\\\
        \\endfoot
        \\hline
        \\endlastfoot
    """
    return s + "\n"


def escape_element(element):
    """
    Ein paar Sonderzeichen versteht LaTeX falsch in Tabellen, deshalb müssen sie hier escpaped werden.
    Außerdem gibt es einen Standardstring, der durch einen anderen ersetzt werden soll.

    :param element: Ein Element aus der Datenbank (String) mit möglicherweise irritierenden Zeichen
    :return: String mit sauber escape-ten Zeichen
    """
    if element == "[Bitte hier „kurz & bündig“ und für „Dritte verständlich“ die Berechtigung beschreiben! Fokus: WAS kann man mit der Berechtigung machen?]":
        return "Noch nicht bearbeitet"
    return element \
        .replace('\\', '\\\\') \
        .replace('#', '\\#') \
        .replace('&', '\\&') \
        .replace('_', '\\_')


def hole_af_varianten(datenzeilen):
    """
    Erzeugt aus den Datenzeile eine Menge der AF-Varianten mit Zusatzinformationen und liefert sie als String zurück.
    Die einzelnen elemente einer Zeile werden durch & voneinander getrennt (Tabellentrenner in LaTeX)
    Die einzelnen Zeilen werden durch \\ voneinander getrennt (LaTeX: Neue Zeile).
    Da die Zeilen keine Kopien enthalten können, ist der Filter über eine Menge nicht erforderlich.
    :param datenzeilen:
    :return:
    """
    s = ""
    for zeile in datenzeilen:
        first = True
        for element in zeile:
            if first:
                first = False
                s += escape_element(element)
            else:
                s += " & " + escape_element(element)
        s += " \\\\\n"
    return s + "\n"


def latex_tabellenende():
    s = """\hline
        \end{longtable}
        \end{tiny}
    """
    return s + "\n"


def latex_nachsatz():
    s = """\\begin{minipage}{\\textwidth}
            Bei Fragen zu technischen Hintergründen können Sie 
            oder Ihre IT-Betreuer sich an den Gruppenbriefkasten 
            G\\_BA-Rezertifizierung
            wenden.\\\\
            \\linebreak
            Beste Grüße\\\\
            Lutz Eichler
    \\end{minipage}
    \\end{letter}
    """
    return s + "\n"


def latex_abspann():
    s = "\\end{document}"
    return s + "\n"


def hole_userid(name):
    account = hole_userids(name)[0]  # Geliefert wird immer eine Liste mit Listen: (('XV00563',), ('BV00563',))
    if (account[0][1].lower() != "v"):
        return account[0].lower()
    else:
        return ('x' + account[0][1:]).lower()


def serienbrief(request):
    """
    Exportfunktion für das Erstellen eines einzelnen LaTeX-Dokkuments mit allen Briefen
    :param request: GET oder POST Request vom Browser
    :return: Gerendertes HTML mit den LaTeX-Daten oder eine Fehlermeldung
    """
    if request.method != 'GET':
        return HttpResponse("Fehlerhafte LaTeX-Generierung in view_serienbrief")

    text = latex_header()
    brief = text

    namen = hole_identitaeten()
    for name in namen:
        userid = hole_userid(name)

        brief += latex_adresse(userid)
        brief += latex_anrede(name[0])  # Geliefert wird auch hier immer eine Liste mit Listen
        brief += latex_einleitungstext()

        datenzeilen = hole_daten(name)
        brief += latex_tf_liste(datenzeilen)
        brief += latex_tabellenkopf()
        brief += hole_af_varianten(datenzeilen)
        brief += latex_tabellenende()
        brief += latex_nachsatz()

    brief += latex_abspann()

    filename = "Serienbriefe.tex"
    response = HttpResponse(brief, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


def gib_dateiname(name, userid):
    name_ohne_space = name.replace(" ", "-")
    return "Rezertifizierung_{0}_{1}_{2}" \
            .format(name_ohne_space, userid, timezone.now()) \
            .replace(".", "-") \
            .replace(":", "-") \
            .replace(" ", "_") \
        + ".tex"


def einzelbrief(request):
    """
    Exportfunktion für das Erstellen eines LaTeX-Dokkuments mit allen einzelnen Briefen.
    Die einzelnen Dokumente sind mit einer bestimmten Headerzeile voneinander getrennt

    :param request: GET oder POST Request vom Browser
    :return: Gerendertes HTML mit den LaTeX-Daten oder eine Fehlermeldung
    """
    if request.method != 'GET':
        return HttpResponse("Fehlerhafte LaTeX-Generierung in view_einzelbrief")

    # Die Daten werden in einzelnen Dateien via zip-File zurückgeliefert
    in_memory_data = BytesIO()
    in_memory_zip = zipfile.ZipFile(in_memory_data, "w", zipfile.ZIP_DEFLATED, False)
    in_memory_zip.debug = 3

    # Die Liste der anzusprechenden Personen (Technische User sind excludiert)
    namen = hole_identitaeten()

    for name in namen:
        userid = hole_userid(name)

        brief = latex_header()  # Für jeden Namen wird eine neue Datei angelegt
        brief += latex_adresse(userid)
        brief += latex_anrede(name[0])  # Geliefert wird auch hier immer eine Liste mit Listen
        brief += latex_einleitungstext()

        datenzeilen = hole_daten(name)
        brief += latex_tf_liste(datenzeilen)

        brief += latex_tabellenkopf()
        brief += hole_af_varianten(datenzeilen)
        brief += latex_tabellenende()

        brief += latex_nachsatz()
        brief += latex_abspann()

        # Schreibe die Daten, die sich in Brief angesammelt haben, in eine Datei im ZIP-File
        filename_in_zip = gib_dateiname(name[0], userid)
        in_memory_zip.writestr(filename_in_zip, brief)

    in_memory_zip.close()  # Die Daten stehen nun weiterhin in in_memory_data zur Verfügung

    filename = "Einzelbriefe.zip"
    response = HttpResponse(in_memory_data.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response
