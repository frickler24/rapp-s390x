# Die beiden nachfolgenden Funktionen dienen nur dem Aufruf der eigentlichen Konzept-Funktion
from copy import deepcopy
import re
import sys
from django.db import connection
from rapp.models import ACLGruppen, RACF_Rechte, TblAfliste, TblDb2, TblGesamt, TblOrga, TblRollehataf, TblRollen, TblUebersichtAfGfs, TblUserIDundName, TblUserhatrolle
from django.utils import timezone
from rapp.UhR_freies_Team_und_Teamliste import kein_freies_team
from django.http import HttpResponse
from django.shortcuts import render
from rapp.xhtml2 import render_to_pdf
from rapp.views import version
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_erzeuge_gefilterte_namensliste, liefere_af_zu_rolle, soll_komplett


def panel_UhR_konzept_pdf(request):
    return erzeuge_UhR_konzept(request, False)


def panel_UhR_konzept(request):
    return erzeuge_UhR_konzept(request, True)


def erzeuge_UhR_konzept(request, ansicht):
    """
    Erzeuge das Berechtigungskonzept für eine Menge an selektierten Identitäten.

    :param request: GET Request vom Browser
    :param ansicht: Flag, ob die Daten als HTML zur Ansicht oder als PDF zum Download geliefert werden sollen
    :return: Gerendertes HTML
    """

    def log(request, rollenMenge, userids, usernamen):
        if request.GET.get('display') == '1':
            print('rollenMenge')
            print(rollenMenge)

            print('userids')
            for a in userids:
                print(a)

            print('usernamen')
            for a in usernamen:
                print(a)

    # Erst mal die relevanten User-Listen holen - sie sind abhängig von Filtereinstellungen
    namen_liste, panel_filter = UhR_erzeuge_gefilterte_namensliste(request)

    if request.method == 'GET':
        rollenMenge, userids, usernamen = UhR_verdichte_daten(request, namen_liste)
    else:
        rollenMenge, userids, usernamen = [], [], []

    log(request, rollenMenge, userids, usernamen)
    af_kritikalitaet = liefere_af_kritikalitaet(rollenMenge)

    winnoe = None
    tf_liste = None
    aftf_dict = None
    db2_liste = None
    racf_liste = None
    winacl_Liste = None

    # episch = 0: Liefere nur das generierte Konzept
    # episch = 1: Liefere zusätzlich die TF-Liste
    # episch = 9: Liefere alles, was in der DB zu finden ist
    episch = int(request.GET.get('episch', 0))
    if episch >= 1:
        aftf_dict = liefere_tf_liste(rollenMenge, userids)
        tf_liste = kurze_tf_liste(aftf_dict)

    if episch == 9:
        racf_liste = liefere_racf_zu_tfs(tf_liste)
        db2_liste = liefere_db2_liste(tf_liste)
        (winacl_Liste, winnoe) = liefere_win_lw_Liste(tf_liste)

    context = {
        'filter': panel_filter,
        'rollenMenge': rollenMenge,
        'aftf_dict': aftf_dict,
        'af_kritikalitaet': af_kritikalitaet,
        'racf_liste': racf_liste,
        'db2_liste': db2_liste,
        'winacl_liste': winacl_Liste,
        'winnoe': winnoe,
        'version': version,
        'ueberschrift': erzeuge_ueberschrift(request),
        'episch': episch,
    }
    if ansicht:
        return render(request, 'rapp/panel_UhR_konzept.html', context)

    pdf = render_to_pdf('rapp/panel_UhR_konzept_pdf.html', context)
    if pdf:
        return erzeuge_pdf_header(request, pdf)
    return HttpResponse("Fehlerhafte PDF-Generierung in erzeuge_UhR_konzept")


def erzeuge_pdf_header(request, pdf):
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = erzeuge_pdf_namen(request)
    content = "inline; filename={}".format(filename)
    download = request.GET.get("download")
    if download:
        content = "attachment; filename={}".format(filename)
    response['Content-Disposition'] = content
    return response


def erzeuge_pdf_namen(request):
    zeit = str(timezone.now())[:10]
    return 'Rollenkonzept_{}_{}.pdf'.format(zeit, request.GET.get('gruppe', ''))


def UhR_verdichte_daten(request, panel_liste):
    """
    Es gibt zunächst Fallunterscheidungen zu den Einträgen in der panel_liste:
    - Wenn kein Team gewählt wurde oder das gewählte Team kein "freies_team" ist
      oder es ein freies_team ist und der User-Name mit 'komplett' angegeben ist
        nimm die Standardbeaarbeitung
    - Wenn es sich um ein "freies_team" handelt und der User-Name nicht mit 'komplett' angegeben ist,
        wird die Spezialbehandlung durchgeführt
    """
    userids = set()
    usernamen = set()
    rollenmenge = set()

    for row in panel_liste:
        if row.userid[:2].lower() == "xv":
            # print('\n\nBehandle', row.name)
            if kein_freies_team(request) or soll_komplett(request, row):
                (rollenmenge, usernamen, userids) = verdichte_standardfall(rollenmenge, row, userids, usernamen)
            else:
                # print('\nUhR_verdichte_daten: Start rollenmenge =', rollenmenge)
                (rollenmenge, usernamen, userids) = \
                    verdichte_spezialfall(rollenmenge, row, userids, usernamen, request)
                # print('\nUhR_verdichte_daten: ergebnis rollenmenge =', rollenmenge)

    def order(a):
        return a.rollenname.lower()  # Liefert das kleingeschriebene Element, nach dem sortiert werden soll

    return sorted(list(rollenmenge), key=order), userids, usernamen


def erzeuge_ueberschrift(request):

    def representsInt(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    name = request.GET.get('name', '')
    teamnr = request.GET.get('orga', '')

    team = TblOrga.objects.get(id=teamnr).team if representsInt(teamnr) else ''

    gruppe = request.GET.get('gruppe', '')
    if gruppe[-2:] == '--':  # Sonderzeichen für nicht-rekursive Auflösung von Organisationen
        gruppe = gruppe[:-2]

    retval = ''
    if name != '':
        retval = name
    if team != '':
        if retval != '':
            retval += ', Team '
        retval += team
    if gruppe != '':
        if retval != '':
            retval += ', '
        retval += gruppe
    return retval


def kurze_tf_liste(aftf_dict):
    """
    Liefert zu einem AFTF_Dict die Menge der enthaltenen TFen

    Aus historischen Gründen erhalten wir dieselben TFen in verschiedenen
    Case-Schreibweisen.
    Beispiel:
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=gruppen,DC=RUV,DC=DE
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=Gruppen,DC=RUV,DC=DE
    Deshalb suchen wir zunächst nach dem einzufügenden Element in Klein-Schreibweise
    und fügen es nur dann dem Ergbnis hinzu, wenn es noch nicht existiert.

    :param aftf_dict: Ein Dictionary AF->TF, zu denen die TF-Menge geliefert werden soll
    :return: Die TF-Liste
    """

    tfInAF = []
    for af in aftf_dict.values():
        for tf in af:
            if element_noch_nicht_vorhanden(tfInAF, tf['tf']):
                tfInAF.append(tf)
    return tfInAF


def liefere_af_kritikalitaet(rollenMenge):
    """
    Für die Menge der gegebenen Rollen liefere die Liste der jeweils höchsten TF-Kritikalitäten.
    Achtung: Bei veralteten Daten in der Gesamt-Tabelle kann es sein, dass diese Informationen
    ebenfalls nicht mehr korrekt sind. Deshalb erfolgt eine Filterung nach UserIDen,
    um ausschließlich aktuelle Werte in der Gesamt-Tabelle zu selektieren.

    :param rollenMenge: Hierüber wird die Liste der AFen ermmittelt, die adressiert werden sollen
    :return: Das Dict der AF => Höchste_Kritikalität_der_TF_in_der_AF laut dem IIQ-Feld
    """
    
    af_menge = liefere_af_menge(rollenMenge)
    krit_liste = TblGesamt.objects \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(geloescht=True) \
        .filter(enthalten_in_af__in=af_menge) \
        .order_by('enthalten_in_af', '-letzte_aenderung') \
        .values('enthalten_in_af',
                'hoechste_kritikalitaet_tf_in_af',
                'letzte_aenderung',
                )

    # Merke den jeweils jüngsten Eintrag je AF, ignoriere Case
    hoechste_kritikalitaet_tf_in_af = {}
    letzter_eintrag = ''

    for krit in krit_liste:
         if krit['enthalten_in_af'].lower() != letzter_eintrag:
            hoechste_kritikalitaet_tf_in_af[str(krit['enthalten_in_af']).lower()] \
                = str(krit['hoechste_kritikalitaet_tf_in_af']).lower()
            letzter_eintrag = str(krit['enthalten_in_af']).lower()

    return hoechste_kritikalitaet_tf_in_af


def liefere_racf_zu_tfs(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden RACF-Profile

    :param tf_menge: Die Menge der TFen, zu denen die RACF-Profile geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """
    suchmenge = { t['tf'] for t in tf_menge }
    return RACF_Rechte.objects \
        .filter(group__in=suchmenge) \
        .order_by('group', 'profil') \
        .values()


def liefere_db2_liste(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden Db2-Grantees

    :param tf_menge: Die Menge der TFen, zu denen die Db2-Grantee geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """
    suchmenge = {t['tf'] for t in tf_menge}
    return TblDb2.objects \
        .filter(grantee__in=suchmenge) \
        .order_by('grantee', 'source', 'table') \
        .values()


def liefere_win_lw_Liste(tf_menge):
    """
    Liefert zu einer TF-Menge die Menge der dazugehörenden ACL-Einträge.
    Die ACL-Tabelle enthält nur den eigentlichen Namen im Active Directory.
    Die TF beschreibt jedoch den LDAP-Namen.
    Deshalb muss der eigentliche AD-Name aus den TFs extrahiert werden,
    bevor die DB-Abfrage erfolgen kann

    Da die ersten Zeichen in der AD-Notation nicht unbedingt mmit den TFen übereinstimmen,
    können wir erstnach mit dem ersten '_' beginnend vergleichen.
    Da es kein in-like gibt, muss die Suche zunächst manuell geschehen.

    Gleichzeitig wird die Liste der ACLs erstellt, für die keine Informationen gefunden wurden

    :param tf_menge: Die Menge der TFen, zu denen die Db2-Grantee geliefert werden sollen.
                     Es handelt sich um ein Queryset mit mehreren Elementen je Index,
                     deshalb das Umsortieren am Anfang.
    :return: Die RACF-Profile als Hash (racf[TF] = RACF-Info
    """

    suchmenge = set()
    winacl = ACLGruppen.objects.order_by('tf', 'server', 'pfad').values()
    rest = []

    for t in tf_menge:
        if 'CN=' in t['tf']:
            ad = re.search("^CN=\w+?(_[\w-]+?),", t['tf'])
            if ad is None:
                s = 'ACHTUNG: regexp konnte nicht mehr gefunden werden in Eintrag ' + t['tf']
                rest.add(s)
                continue
            for acl in winacl:
                if ad[1] in acl['tf']:
                    suchmenge.add(acl['tf'])
                    break
            rest.add(t['tf'])

    retval = ACLGruppen.objects \
        .filter(tf__in=suchmenge) \
        .order_by('tf', 'server', 'pfad') \
        .distinct() \
        .values()

    return retval, rest


def liefere_tf_liste(rollenMenge, userids):
    """
    Liefet zu einer Menge an Rollen die zugehörenden TFen.
    Dies geschieht zunächst über die Ermittlung der Arbeitsplatzfunktionen,
    die für die angegebenen Rollen definiert sind.
    In der Anzeige müssen die jeweiligen TFs zu ihren AFs dargestellt werden können,
    das ist besonders bei redundant modellierten TFen relevant.
    :param userids: Menge der UserIDs, zu denen gesucht werden soll
    :param rollenMenge:
    :return: Menge der den Rollen zugeordneten TFen als Dict aftfDict[AF] = TF_Querysyset
    """
    af_menge = liefere_af_menge(rollenMenge)
    return liefere_tf_zu_afs(af_menge, userids)


def liefere_tf_zu_afs(af_menge, userids):
    """
    Liefert zu einer AF-Liste die Menge der dazugehörenden TFen

    Aus historischen Gründen erhalten wir dieselben TFen in verschiedenen
    Case-Schreibweisen.
    Beispiel:
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=gruppen,DC=RUV,DC=DE
        CN=A_CONNECTDIRECT,OU=Sicherheitsgruppen,OU=Gruppen,DC=RUV,DC=DE
    Deshalb suchen wir nach dem einzufügenden Element nur in Klein-Schreibweise
    und fügen es nur dann dem Ergbnis in Original-Schreibweise hinzu, wenn es noch nicht existiert.
    Damit wir die jeweils jüngste Schreibweise zurückliefern,
    erfolgt in der Query bereits eine Sortierung nach dem Datum des Auffindens.

    :param af_menge: Die Mmegne der AFen, zu denen die TF-Menge geliefert werden soll
    :param userids: Die Liste der Userids zum feineren Slektieren der Einträge in der Gesamttabelle
    :return: Menge der den Rollen zugeordneten TFen als Dict aftfDict[AF] => TF_Querysyset
    """

    tf_liste = TblGesamt.objects \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(geloescht=True) \
        .exclude(tf='Kein Name') \
        .exclude(tf='TF existiert nicht mehr') \
        .filter(enthalten_in_af__in=af_menge) \
        .filter(userid_name__userid__in=userids) \
        .order_by('-gefunden', '-wiedergefunden') \
        .values('enthalten_in_af',
                'af_beschreibung',
                'tf',
                'tf_beschreibung',
                'tf_kritikalitaet',
                'tf_eigentuemer_org',
                'plattform__tf_technische_plattform',
                'direct_connect',
                'hoechste_kritikalitaet_tf_in_af'
                )

    retvalDict = {}
    afset = {af['enthalten_in_af'] for af in tf_liste}
    for af in afset:
        tfInAF = []

        for tf in tf_liste:
            # Betrachte nur die TFe für die aktuelle AF
            if tf['enthalten_in_af'] != af:
                continue
            # leider ist tf nicht "set-fähig"
            if element_noch_nicht_vorhanden(tfInAF, tf['tf']):
                tfInAF.append(tf)
        retvalDict[af] = tfInAF
            # print('ratvalDict = {}'.format(retvalDict))
    return retvalDict


def verdichte_spezialfall(rollenmenge, row, userids, usernamen, request):
    """
    - Wenn es sich um ein "freies_team" handelt und der User-Name nicht mit 'komplett' angegeben ist
            - wird zunächst die in der übergebenen Rolle angegebene Liste bearbeitet:
            - wenn eine Rolle namens "Weitere <Gruppenbezeichnung des Users>" existiert,
                werden alle AFen daraus entfernt, sonst wird die Rolle erzeugt und dem User zugewiesen
            - Alle AFen des Users, die nicht bereits über rollenmenge adressiert sind, werden der neuen Rolle hinzugefügt
            - Die neu konfigurierte Rolle wird der Rollenmenge hinzugefügt

    :param request: Der ursprüngliche HTTP-Request
    :param rollenmenge: Die bislang zusammengestellten Rollen
    :param row: Der aktuelle User
    :param userids: Die bislang behandelten UserIDs
    :param usernamen:
    :return: alle erweiterten Mengen: rollenmenge, usernamen, userids
    """
    usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
    userids.add(row.userid)
    userHatRollen = TblUserhatrolle.objects.filter(userid__userid=row.userid).order_by('rollenname')

    assert request.GET.get('orga') is not None
    spezialteam = TblOrga.objects.get(id=request.GET.get('orga'))
    erlaubte_rollenqs = TblUserhatrolle.objects \
        .filter(userid__name=row.name) \
        .filter(teamspezifisch=spezialteam)

    erlaubte_rollen = set()
    for e in erlaubte_rollenqs:
        # print('erlaubte Rollen hat gefunden:', e.rollenname)
        erlaubte_rollen.add(e.rollenname)
        rollenmenge.add(e.rollenname)

    # print('verdichte_spezialfall: Rollenmenge nach Ergänzung erlaubte Rollen =', rollenmenge)

    restrolle = erzeuge_restrolle(row.userid, erlaubte_rollen, spezialteam)
    # print('Restrolle =', restrolle)

    rollenmenge.add(restrolle)
    # print('verdichte_spezialfall: Ergebnis Rollenmenge =', rollenmenge)

    return rollenmenge, usernamen, userids


def verdichte_standardfall(rollenmenge, row, userids, usernamen):
    """
     Ausgehend von den Userids der Selektion zeige
      für den angebenen XV-User (nur die XV-User zeigen auf Rollen, deshalb nehmen wir nur diese)
        alle Rollen mit allen Details
          einschließlich aller darin befindlicher AFen mit ihren formalen Zuweisungen (Soll-Bild)
            verdichtet auf Mengenbasis
              (keine Doppelnennungen von Rollen,
              aber ggfs. Mehrfachnennungen von AFen,
              wenn sie in disjunkten Rollen mehrfach erscheinen)

    :param rollenmenge: Die bislang zusammengestellten Rollen
    :param row: Der aktuelle User
    :param userids: Die bislang behandelten UserIDs
    :param usernamen:
    :return: alle erweiterten Mengen: rollenmenge, usernamen, userids
    """
    usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
    userids.add(row.userid)
    userHatRollen = TblUserhatrolle.objects.filter(userid__userid=row.userid).order_by('rollenname')
    for e in userHatRollen:
        rollenmenge.add(e.rollenname)
    return rollenmenge, usernamen, userids


def element_noch_nicht_vorhanden(liste, element):
    """
    Suche nach Einträgen in der übergebenen Liste,
    die - außer in der Klein-/Großschreibung - identisch mmit dem Suchstring sind

    :param liste: Die bereits vorhandene Liste
    :param element: Der Suchstring
    :return: True, wenn das Element noch nicht vorhanden ist, sonst False
    """
    suche = element.lower()
    return all(e['tf'].lower() != suche for e in liste)


# Funktionen zum Erstellen des Berechtigungskonzepts
def alte_oder_neue_restrolle(tempname, userid, team):
    """
    Zunächst wird für den User gesucht, ob er bereits über eine "Weitere <Abteilungskürzel>"-Rolle verfügt.
    Falls ja, werden alle daran hängenden AF-Einträge in Tbl_RolleHatAF gelöscht
    :param tempname: Der ausgedachte Name der neuen oder alten Rolle
    :param userid:
    :param team: Die Referenz auf das Spezialteam. Wird benötigt zum Anlegen der UserHatRolle-Beziehung
    :return: Die alte und bereinigte oder die neu angelegte Rolle
    """

    weitereRolle = TblUserhatrolle.objects \
        .filter(userid__userid=userid) \
        .filter(rollenname=tempname)

    if weitereRolle.exists():
        afs_an_rolle = TblRollehataf.objects.filter(rollenname=tempname)
        afs_an_rolle.delete()

        # Ist die Teamspezfisch-Markierung schon mit dem UserHatRolle-Eintrag verknüpft?
        uhr = TblUserhatrolle.objects.filter(
            userid=TblUserIDundName.objects.get(userid=userid),
            rollenname=tempname,
        )
        # ToDo: Sonderfall * in der Spezifikationsliste in team.freies_team
        if uhr.count() > 0:
            # dann ist die Rolle bereits mit dem User verknüpft
            # Sicherheitshalber wird das Team-Spezifikum eingetragen, falls noch ein anderer Wert drin steht
            uhr = deepcopy(uhr[0])  # Sonst ist kein Update möglich - warum auch immer...
            if uhr.teamspezifisch != team:
                uhr.teamspezifisch = team
                uhr.save(force_update=True)
        else:  # Nein, muss noch verknüpft werden
            uhr = TblUserhatrolle.objects.create(
                userid=TblUserIDundName.objects.get(userid=userid),
                rollenname=tempname,
                schwerpunkt_vertretung='Schwerpunkt',
                bemerkung='Organisationsspezifische AFen',
                teamspezifisch=team,
                letzte_aenderung=timezone.now(),
            )
            uhr.save()
    else:
        # In diesem Fall gibt es die Rolle "Weitere <Abteilung>" noch gar nicht
        print('Rolle und Verknüpfung müssen komplett neu erstellt werden')
        rolle = TblRollen.objects.create(
            rollenname=tempname,
            system='Diverse',
            rollenbeschreibung='Organisationsspezifische AFen',
        )
        uhr = TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid=userid),
            rollenname=rolle,
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Organisationsspezifische AFen',
            teamspezifisch=team,
            letzte_aenderung=timezone.now(),
        )
        rolle.save()
        uhr.save()

    return TblRollen.objects.get(rollenname=tempname)


def erzeuge_restrolle(userid, rollenmenge, team):
    tempname = 'Weitere ' + TblUserIDundName.objects \
        .filter(userid=userid).values('abteilung')[0]['abteilung']
    rolle = alte_oder_neue_restrolle(tempname, userid, team)

    erledigt = hole_soll_af_mengen(rollenmenge)
    rest = hole_alle_offenen_AFen_zur_userid(userid, erledigt)

    for eintrag in rest:
        if eintrag['enthalten_in_af'] == 'ka':
            continue
        af = TblAfliste.objects.filter(af_name=eintrag['enthalten_in_af'])
        if af.count() == 0:
            if TblAfliste.objects.filter(af_name='Noch_nicht_akzeptierte_AF').count() == 0:
                print('WARN: Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen')
                print('WARN: Auslöser ist', eintrag['enthalten_in_af'])
                af = TblUebersichtAfGfs.objects.create(
                    name_gf_neu='Noch_nicht_akzeptierte_GF',
                    name_af_neu='Noch_nicht_akzeptierte_AF',
                    kommentar='Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen',
                    zielperson='Alle',
                    af_text='Bitte in der Anwendung unter "Magie" einmalig "neue AF hinzufügen" ausführen',
                    gf_text='',
                    af_langtext='',
                    af_ausschlussgruppen='',
                    af_einschlussgruppen='',
                    af_sonstige_vergabehinweise='',
                    geloescht=False,
                    kannweg=False,
                    modelliert=timezone.now(),
                )
                af.save()
                with connection.cursor() as cursor:
                    try:
                        cursor.callproc("erzeuge_af_liste")
                    except:
                        e = sys.exc_info()[0]
                        print('Fehler in erzeuge_restrolle, StoredProc erzeuge_af_liste: {}'.format(e))
                    cursor.close()
            merkaf = TblAfliste.objects.get(af_name='Noch_nicht_akzeptierte_AF')
        else:
            merkaf = TblAfliste.objects.get(af_name=eintrag['enthalten_in_af'])

        neu = TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_NONE,
            bemerkung='Rechtebündel; Details siehe Konzept der Abteilung',
            af=merkaf,
            rollenname=rolle,
        )
        neu.save()
    return rolle


def hole_soll_af_mengen(rollenmenge):
    """
    Hole für jede der übergebenen Rollen die SOLL-AFen.
    :param rollenmenge:
    :return: QUerySet mit den SOLL-AFen
    """
    retval = TblRollehataf.objects.none()

    for rolle in rollenmenge:
        retval |= liefere_af_zu_rolle(rolle)
    return retval


def hole_alle_offenen_AFen_zur_userid(userid, erledigt):
    # sourcery skip: inline-immediately-returned-variable
    """
    Liefert eine Menge aller AFen, die für eine UserID in der Gesamttabelle aufgeführt sind
    und die nicht in der erledigt-Liste auftauchen
    :param erledigt: Liste der bereits erledigten AFen
    :param userid:
    :return: QuerySet mit den gesuchten AFen
    """
    """
    print('erledigt Anzahl = {}\n Inhalt ='.format(erledigt.count(), list(erledigt)))
    print('ungefilterte Gesamtliste = ',
          list(TblGesamt.objects
               .exclude(geloescht=True)
               .exclude(userid_name_id__geloescht=True)
               .filter(userid_name_id__userid=userid)
               .values('enthalten_in_af')
               .distinct()
               .order_by('enthalten_in_af')
               ))
    print('Länge der Gesamtliste = ',
          TblGesamt.objects
          .exclude(geloescht=True)
          .exclude(userid_name_id__geloescht=True)
          .filter(userid_name_id__userid=userid)
          .values('enthalten_in_af')
          .distinct()
          .count()
          )
    """
    af_qs = TblGesamt.objects \
        .exclude(geloescht=True) \
        .exclude(userid_name_id__geloescht=True) \
        .exclude(enthalten_in_af__in=erledigt) \
        .filter(userid_name_id__userid=userid) \
        .values('enthalten_in_af') \
        .distinct() \
        .order_by('enthalten_in_af')
    # print('AF_QS Anzahl = {}, Inhalt = {}'.format(af_qs.count(), list(af_qs)))
    return af_qs


def liefere_af_menge(rollenMenge):
    """
    Liefert die Menge der AFen, die von einer Menge an Rollen adressiert wird
    :param rollenMenge: Die Menge an Rollen, zu denen die AFen gesucht werden
    :return: af_menge aller gefundener AFen
    """
    af_menge = set()
    for rolle in rollenMenge:
        af_liste = liefere_af_zu_rolle(rolle)
        af_menge.update({af['af__af_name'] for af in af_liste})
    return af_menge

