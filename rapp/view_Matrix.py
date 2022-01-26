"""
Funktionen zum Erstellen des Funktionsmatrix
"""

from rapp.UhR_freies_Team_und_Teamliste import kein_freies_team
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str

from .excel import Excel
from .models import TblOrga, TblUserhatrolle, TblUserIDundName
from .templatetags.gethash import finde
from .view_UserHatRolle_Datenbeschaffung import soll_komplett, UhR_erzeuge_gefilterte_namensliste, \
    hole_userids_zum_namen
from .views import version


def string_aus_liste(liste):
    """
    Erzeugt einen String, der alle Listenelemente der Parameters Kommma-getrennt enthält
    :param liste: Eine Liste mit Strings, bspw. ['abc', 'def']
    :return: String mit den Inhalten, getrennt durch ', ': "abc, def"
    """
    return ", ".join(liste)


def logging(request, rollen_je_username, rollenmenge, usernamen, namen_liste):
    """
    Halbwegs brauchbare Debug-Ausgabe

    :param request:
    :param rollen_je_username:
    :param rollenmenge:
    :param usernamen:
    :param namen_liste:
    :return:
    """
    if request.GET.get('display') == '1':
        print('namen_liste:', namen_liste)
        print('usernamen:', usernamen)

        print('Rollenmenge:')
        for a in rollenmenge:
            print(a)

        print('Rollen_je_username:')
        for a in rollen_je_username:
            print(a, rollen_je_username[a])


def erzeuge_UhR_matrixdaten(request, namen_liste):
    """
    Überschriften-Block:
        Erste Spaltenüberschrift ist "Name" als String, darunter werden die Usernamen liegen, daneben:
            Zeige Teamzugehörigkeit(en), daneben
                Ausgehend von den Userids der Selektion zeige
                    die Liste der Rollen alle nebeneinander als Spaltenüberschriften
    Zeileninhalte:
        Für jeden User (nur die XV-User zeigen auf Rollen, deshalb nehmen wir nur diese)
            zeige den Usernamen sowie in jeder zu dem User passenden Rolle die Art der Verwendung (S/V/A)
                in Kurz- oder Langversion, je nach Flag

    Zunächst benötigen wir für alle userIDs (sind nur die XV-Nummern) aus dem Panel alle Rollen

    :param request: für die Fallunterscheidung spezifisches_team
    :param namen_liste: Die Menge der betrachteten User
    :return: usernamen, rollenmenge als Liste, rollen_je_username, teams_je_username
    """
    usernamen = set()  # Die Namen aller User,  die in der Selektion erfasst werden
    rollenmenge = set()  # Die Menge aller AFs aller spezifizierten User (aus Auswahl-Panel)
    teams_je_username = {}  # Derzeit nur ein Team/UserID, aber multi-Teams müssen vorbereitet werden
    rollen_je_username = {}  # Die Rollen, die zum Namen gehören

    for row in namen_liste:
        index = str(row)
        usernamen.add(index)
        userid, name = index.split(' | ')
        userid = userid[1:]
        teamliste = TblOrga.objects \
            .filter(tbluseridundname__name=row.name,
                    tbluseridundname__userid__iendswith=userid,
                    tbluseridundname__geloescht=False) \
            .exclude(team="Gelöschter User")  # Die als gelöscht markierten User werden nicht mehr angezeigt

        teammenge = set()
        for team in teamliste:
            teammenge.add(str(team))
        teams_je_username[index] = [str(team) for team in teammenge]

        # Erzeuge zunächst die Hashes für die UserIDs. Daran werden nachher die Listen der Rechte gehängt.
        rollen_je_username[index] = set()

        # Fallunterscheidung nach "freies_team" und "spezielles_team"
        if kein_freies_team(request) or soll_komplett(request, row):  # Standardfall
            rollen = TblUserhatrolle.objects.filter(userid=row.userid)
        else:
            spezialteam = TblOrga.objects.get(id=request.GET.get('orga'))
            rollen = TblUserhatrolle.objects \
                .filter(userid=row.userid) \
                .filter(teamspezifisch=spezialteam)

        # Merke die Rollen je Usernamen (also global für alle UserIDs der Identität)
        # sowie die Menge aller gefundenen Rollennamen
        # Achtung: rolle ist nur eine für den User spezifische Linknummer auf das Rollenobjekt.
        for rolle in rollen:
            info = (rolle.rollenname, rolle.schwerpunkt_vertretung)
            rollen_je_username[index].add(info)
            rollenmenge.add(rolle.rollenname)

    def order(a):
        return a.rollenname.lower()  # Liefert das kleingeschriebene Element, nach dem sortiert werden soll
    return (sorted(usernamen), sorted(list(rollenmenge), key=order), rollen_je_username, teams_je_username)


def erzeuge_userIDlisten(erweiterte_namen_liste):
    """
    Liefert die Menge der UserIDen, die zu einem Namen derzeit aktuell vorliegen
    :param namen_liste: Zu welchen Namen sollen die UserIDs gesucht werden?
    :return: Liste der UserIDs je Identität, jeweils als String
    """
    uids_je_username = {}

    for row in erweiterte_namen_liste:
        uids = hole_userids_zum_namen(row)
        uids_je_username[str(row)] = uids
    return uids_je_username


def hole_npu_detail(selektierter_name):
    """
    Hole die Rolle und den Grund für einen angegebenen NPU.
    Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
    Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen

    :param selektierter_name: (userid | name) Zu welchem Namen sollen die NPU-Details gesucht werden?
    :return: tupel (npu_rolle, npu_grund)
    """
    userid, name = str(selektierter_name).split(' | ')
    userid = userid[1:]
    query = TblUserIDundName.objects \
        .filter(name=name) \
        .filter(userid__iendswith=userid) \
        .order_by('-userid') \
        .filter(geloescht=False) \
        .values('npu_rolle', 'npu_grund')
    return [(q['npu_rolle'], q['npu_grund']) for q in query]


def erzeuge_npu_details(namen_liste):
    """
    Hole die Rolle und den Grund für die angegebenen NPUs.

    :param namen_liste: Zu welchen Namen sollen die NPU-Details gesucht werden?
    :return: Liste der tupel (npu_rolle, npu_grund)
    """
    details_je_username = {}

    for row in namen_liste:
        details = hole_npu_detail(row)
        details_je_username[str(row)] = details
    return details_je_username


def panel_UhR_matrix(request):
    """
    Erzeuge eine Verantwortungsmatrix für eine Menge an selektierten Identitäten.
    :param request: GET Request vom Browser
    :return: Gerendertes HTML
    """

    # Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
    (namen_liste, panel_filter) = UhR_erzeuge_gefilterte_namensliste(request)

    if request.method == 'GET':
        (usernamen, rollenmenge, rollen_je_username, teams_je_username) = erzeuge_UhR_matrixdaten(request, namen_liste)
        UserIDen_je_username = erzeuge_userIDlisten(namen_liste)
        npu_details_je_username = erzeuge_npu_details(namen_liste)
    else:
        (usernamen, rollenmenge, rollen_je_username, teams_je_username, UserIDen_je_username, npu_details_je_username) \
            = (set(), set(), set(), {})

    logging(request, rollen_je_username, rollenmenge, usernamen, namen_liste)
    context = {
        'filter': panel_filter,
        'usernamen': usernamen,
        'rollenmenge': rollenmenge,
        'rollen_je_username': rollen_je_username,
        'teams_je_username': teams_je_username,
        'version': version,
        'UserIDen_je_username': UserIDen_je_username,
        'npu_details_je_username': npu_details_je_username,
    }
    return render(request, 'rapp/panel_UhR_matrix.html', context)


def panel_UhR_matrix_csv(request, flag=False):
    """
    Exportfunktion für das Filter-Panel zum Selektieren aus der "User und Rollen"-Tabelle).
    :param request: GET oder POST Request vom Browser
    :param flag: False oder nicht gegeben -> liefere ausführliche Text, 'kompakt' -> liefere nur Anfangsbuchstaben
    :return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
    """
    if request.method != 'GET':
        return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_matrix_csv")

    (namen_liste, _) = UhR_erzeuge_gefilterte_namensliste(request)
    (usernamen, rollenmenge, rollen_je_username, teams_je_username) = erzeuge_UhR_matrixdaten(request, namen_liste)
    UserIDen_je_username = erzeuge_userIDlisten(namen_liste)
    npu_details_je_name = erzeuge_npu_details(namen_liste)

    headline = [smart_str(u'Name')] + [smart_str(u'Teams')] + [smart_str(u'UserIDs')]
    for r in rollenmenge:
        headline += [smart_str(r.rollenname)]
    headline += [smart_str(u'NPU-Rolle')] + [smart_str(u'NPU-Grund')]

    excel = Excel("matrix.csv")
    excel.writerow(headline)

    for user in usernamen:
        line = [user] \
               + [smart_str(string_aus_liste(teams_je_username[user]))] \
               + [smart_str(string_aus_liste(UserIDen_je_username[user]))]
        for rolle in rollenmenge:
            if flag:
                wert = finde(rollen_je_username[user], rolle)
                if wert is None or len(wert) <= 0:
                    line += ['']
                else:
                    line += [smart_str(wert[0])]
            else:
                line += [smart_str(finde(rollen_je_username[user], rolle))]
        line += [smart_str(npu_details_je_name[user][0][0])] + [smart_str(npu_details_je_name[user][0][1])]
        excel.writerow(line)

    return excel.response