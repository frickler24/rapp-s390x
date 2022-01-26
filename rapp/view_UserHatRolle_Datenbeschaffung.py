from __future__ import unicode_literals
from django.db.models import Count

from rapp.filters import RollenFilter, UseridFilter
from rapp.models import TblGesamt
from rapp.models import TblOrga
from rapp.models import TblRollehataf
from rapp.models import TblUserIDundName
from rapp.models import TblUserhatrolle
from rapp.UhR_freies_Team_und_Teamliste import behandle_freies_team, behandle_teamliste


def UhR_erzeuge_gefilterte_namensliste(request):
    """
    Finde alle relevanten Informationen zur aktuellen Selektion: UserIDs und zugehörige Orga

    Ausgangspunkt ist TblUseridUndName.
    Hierfür gibt es einen Filter, der per GET abgefragt wird.
    Geliefert werden nur die XV-Nummern zu den Namen (diese muss es je Namen zwingend geben)

    Die dort gefundene Treffermenge wird angereichert um die relevanten Daten aus TblUserHatRolle.
    Hier werden alle UserIDen zurückgeliefert je Name.
    Von dort aus gibt eine ForeignKey-Verbindung zu TblRollen.

    Problematisch ist noch die Verbindung zwischen TblRollen und TblRollaHatAf,
    weil hier der Foreign Key per Definition in TblRolleHatAf liegt.
    Das kann aber aufgelöst werden,
    sobald ein konkreter User betrachtet wird und nicht mehr eine Menge an Usern.

    :param request: GET oder POST Request vom Browser
    :return: name_liste, panel_liste, panel_filter
    """
    panel_liste = TblUserIDundName.objects.filter(
        geloescht=False).order_by('name')
    panel_filter = UseridFilter(request.GET, queryset=panel_liste)
    namen_liste = panel_filter.qs.filter(
        userid__istartswith="xv").select_related("orga")

    teamnr = request.GET.get('orga')
    if teamnr is not None and teamnr != '':
        teamqs = TblOrga.objects.get(id=teamnr)
        if teamqs.teamliste is not None \
                and teamqs.freies_team is not None \
                and teamqs.teamliste != '' \
                and teamqs.freies_team != '':
            print("""Fehler in UhR_erzeuge_gefiltere_namensliste: \
                        Sowohl teamliste als auch freies_team sind gesetzt in Team {}: \
                        teammliste = {}, freies_team = {}."""
                  .format(teamnr, teamqs.teamliste, teamqs.freies_team))
            return namen_liste, panel_filter
        if teamqs.teamliste is not None and teamqs.teamliste != '':
            namen_liste = behandle_teamliste(panel_liste, request, teamqs)
        elif teamqs.freies_team is not None and teamqs.freies_team != '':
            namen_liste = behandle_freies_team(panel_liste, request, teamqs)

    """
    # Ein paar Testzugriffe über das komplette Modell
    #   Hier ist die korrekte Hierarchie abgebildet von UserID bis AF:
    #   TblUserIDundName enthält Userid
    #       TblUserHatRolle hat Foreign Key 'userid' auf TblUserIDundName
    #       -> tbluserhatrolle_set.all auf eine aktuelle UserID-row liefert
    #          die Menge der relevanten Rollen
    #            Rolle hat ForeignKey 'rollenname' auf TblRolle und erhält damit
    #            die nicht-User-spezifischen Rollen-Parameter
    #               TblRolleHatAF hat ebenfalls einen ForeignKey 'rollennname' auf TblRollen
    #               -> rollenname.tblrollehataf_set.all liefert für eine konkrete Rolle
    #                  die Liste der zugehörigen AF-Detailinformationen
    #
    #        TblGesamt hat FK 'userid_name' auf TblUserIDundName
    #        -> .tblgesamt_set.filter(geloescht = False) liefert die aktiven Arbeitsplatzfunktionen
    #

    user = TblUserIDundName.objects.filter(userid = 'XV13254')[0]
    print ('1:', user)
    foo = user.tbluserhatrolle_set.all()
    print ('2:', foo)

    for x in foo:
        print ('3:', x, ',', x.rollenname, ',', x.rollenname.system)
        foo2 = x.rollenname.tblrollehataf_set.all()
        for y in foo2:
            print ('4:', y, ', AF=', y.af, ', Muss:', y.mussfeld, ', Einsatz:', y.einsatz)
    af_aktiv = user.tblgesamt_set.filter(geloescht = False)
    af_geloescht = user.tblgesamt_set.filter(geloescht = True)
    print ("5: aktive AF-Liste:", af_aktiv, "geloescht-Liste:", af_geloescht)
    for x in af_aktiv:
        print ('5a:', x.enthalten_in_af, x.tf, x.tf_beschreibung, sep = ', ')
    print
    for x in af_geloescht:
        print ('5b:', x.enthalten_in_af, x.tf, x.tf_beschreibung, sep = ', ')
    print
    af_liste = TblUserIDundName.objects.get(id=id).enthalten_in_af
    print ('6:', af_liste)
    """
    return namen_liste, panel_filter


def UhR_erzeuge_listen_ohne_rollen(request):
    """
    Liefert zusätzlich zu den Daten aus UhR_erzeuge_gefiltere_namensliste
    noch eine leere Rollenliste, damit das Suchfeld angezeigt wird.
    :param request:
    :return: namen_liste, panel_liste, panel_filter, rollen_liste, rollen_filter
    """

    # Hole erst mal eine leere Rollenliste ud dazu passenden Filter
    rollen_liste = TblUserhatrolle.objects.none()
    rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

    # Und nun die eigentlich wichtigen Daten holen
    (namen_liste, panel_filter) = UhR_erzeuge_gefilterte_namensliste(request)
    return namen_liste, panel_filter, rollen_liste, rollen_filter


def UhR_erzeuge_listen_mit_rollen(request):
    """
    Liefert zusätzlich zu den Daten aus UhR_erzeuge_gefiltere_namensliste
    noch die dazu gehörenden Rollen.
    Ausgangspunkt sind die Rollen, nach denen gesucht werden soll.
    Daran hängen UserIDs, die wiederum geeignet gefilter werden nach den zu findenden Usern

    Geliefert wird
    - die Liste der selektiert Namen (unabhängig davon, ob ihnen AFen oder Rollen zugewiesen sind)
    - den Panel_filter für korrekte Anzeige
    - Die Liste der Rollen, die in der Abfrage derzeit relevant sind
    - der Rollen_filter, der benötigt wird, um das "Rolle enthält"-Feld anzeigen lassen zu können
    :param request
    :return: namen_liste, panel_filter, rollen_liste, rollen_filter
    """

    # Hole erst mal die Menge an Rollen, die namentlich passen
    suchstring = request.GET.get('rollenname', 'nix')
    if suchstring in ["*", "-"]:
        rollen_liste = TblUserhatrolle.objects.all().order_by('rollenname')
    else:
        rollen_liste = TblUserhatrolle.objects \
            .filter(rollenname__rollenname__icontains=suchstring) \
            .order_by('rollenname')
    rollen_filter = RollenFilter(request.GET, queryset=rollen_liste)

    (namen_liste, panel_filter) = UhR_erzeuge_gefilterte_namensliste(request)

    return namen_liste, panel_filter, rollen_liste, rollen_filter


def hole_unnoetigte_afen(namen_liste):
    """
    Diese Funktion dient dazu, überflüssige AFen in Rollendefinitionen zu erkennen
    Erzeuge Deltaliste zwischen der Sollvorgabe der Rollenmenge
    und der Menge der vorhandenen Arbeitsplatzfunktionen.

    :param namen_liste: Liste der Namen, die derzeit selektiert sind.
    :return: Queryset mit Treffern, beinhaltet Rollennamen und AF
    """

    # Zunächst wird das Soll der User-Rollen ermittelt
    soll_rollen = TblUserhatrolle.objects \
        .filter(userid__name__in=namen_liste.values('name')) \
        .values('userid__name', 'rollenname')

    # Nun das Ist der AFen je User:
    ist_afen = TblGesamt.objects \
        .exclude(geloescht=True) \
        .exclude(userid_name__geloescht=True) \
        .filter(userid_name__name__in=namen_liste.values('name')) \
        .values('enthalten_in_af').annotate(dcount=Count('enthalten_in_af'))

    # Und das Delta: Ziehe alle IST-AFen von den Soll-AFen ab und liefere das Delta zurück
    delta = TblRollehataf.objects \
        .filter(rollenname__in=soll_rollen.values('rollenname')) \
        .exclude(af__af_name__in=ist_afen.values('enthalten_in_af')) \
        .order_by('rollenname__rollenname', 'af', ) \
        .values(
            'rollenname__rollenname',
            'af__af_name',
        )

    return delta


def hole_userids_zum_namen(selektierter_name):
    """
    Hole alle UserIDs, die zu dem ausgesuchten User passen.
    Dies funktioniert nur, weil der Name ein unique Key in der Tabelle ist.
    Wichtig: Filtere gelöschte User heraus, sonst gibt es falsche Anzeigen

    Zunächst wird der zusammengesetzte userid|Name-String getrennt,
    dann wird von der Userid die erste Stelle entfernt,
    damit anschließend nach allen UserIDs gesucht werden kann,
    die dem Muster ?v<Nummer> entsprechen.
    Das wird benötigt, weil es User mit gleichem Namen, aber diskunkten UserIDs gibt.

    :param selektierter_name: Zu welchem Namen ("xv|name, vorname")
                              sollen die UserIDs gesucht werden?
    :return: Liste der UserIDs (als String[])
    """
    userid, name = str(selektierter_name).split(" | ")
    userid = userid[1:]
    query = TblUserIDundName.objects \
        .filter(name=name) \
        .filter(userid__iendswith=userid) \
        .order_by('-userid') \
        .filter(geloescht=False) \
        .values('userid')
    return [q['userid'] for q in query]


def UhR_hole_daten(panel_liste, id):
    """
    Selektiere alle Userids und alle Namen in TblUserHatRolle, die auch in der Selektion vorkommen

    Die Liste der disjunkten UserIDs wird später in der Anzeige benötigt
    (welche UserID gehören zu einem Namen).
    Hintergrund ist die Festlegung, dass die Rollen am UserNAMEN un dnicht an der UserID hängen.
    Dennoch gibt es Rollen, die nur zu bestimmten Userid-Typen
    (also bspw. nur für XV-Nummer) sinnvoll
    und gültig sind.

    Die af_menge wird benutzt zur Anzeige, welche der rollenbezogenen AFen bereits im IST vorliegt

    """
    usernamen = set()  # Die Namen aller User,  die in der Selektion erfasst werden
    userids = set()  # Die UserIDs aller User,  die in der Selektion erfasst werden
    # Die Menge aller AFs aller mit ID spezifizierten User (für Berechtigungskonzept)
    afmenge = set()
    selektierte_userids = set()  # Die Liste der UserIDs, die an Identität ID hängen
    afmenge_je_userID = {}  # Menge mit UserID-spezifischen AF-Listen

    for row in panel_liste:
        usernamen.add(row.name)  # Ist Menge, also keine Doppeleinträge möglich
        userids.add(row.userid)

    if id != 0:  # Dann wurde der ReST-Parameter 'id' mitgegeben

        userHatRolle_liste = TblUserhatrolle.objects.filter(
            userid__id=id).order_by('rollenname')
        selektierter_name = TblUserIDundName.objects.get(id=id).name

        # Wahrscheinlich werden verschiedene Panels auf die Haupt-UserID referenzieren
        # (die XV-Nummer)
        selektierte_haupt_userid = TblUserIDundName.objects.get(id=id).userid

        # Hole alle UserIDs, die zu dem ausgesuchten User passen.
        selektierte_userids = hole_userids_zum_namen(
            "{} | {}".format(selektierte_haupt_userid, selektierter_name))

        # Selektiere alle Arbeitsplatzfunktionen, die derzeit mit dem User verknüpft sind.
        afliste = TblUserIDundName.objects.get(
            id=id).tblgesamt_set.all()  # Das QuerySet
        for e in afliste:
            if not e.geloescht:  # Bitte nur die Rechte, die nicht schon gelöscht wurden
                # AF der Treffermenge in die Menge übernehmen (Wiederholungsfrei)
                afmenge.add(e.enthalten_in_af)

        # Erzeuge zunächst die Hashes für die UserIDs.
        # Daran werden nachher die Listen der Rechte gehängt.
        for uid in selektierte_userids:
            afmenge_je_userID[uid] = set()

        # Selektiere alle Arbeitsplatzfunktionen,
        # die derzeit mit den konkreten UserIDs verknüpft sind.
        for uid in selektierte_userids:
            tmp_afliste = TblUserIDundName.objects.get(
                userid=uid).tblgesamt_set.filter(geloescht=False)
            for e in tmp_afliste:
                # Element an das UserID-spezifische Dictionary hängen
                afmenge_je_userID[uid].add(e.enthalten_in_af)
    else:
        userHatRolle_liste = []
        selektierter_name = -1
        selektierte_haupt_userid = 'keine_userID'

    return userHatRolle_liste, selektierter_name, userids, usernamen, \
        selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID


def hole_rollen_zuordnungen(af_dict):
    """
    Liefert eine Liste der Rollen, in denen eine Menge von AFs vorkommt,
    sortiert nach Zuordnung zu einer Liste an UserIDs

    :param af_dict: Die Eingabeliste besteht aus einem Dictionary
                    af_dict[Userid] = AF_Menge_zur_UserID[]
    :return: vorhanden = Liste der Rollen,
                         in denen die AF vorkommt und die dem Namen zugeordnet sind
    :return: optional = Liste der Rollen,
                        in denen die AF vorkommt und die dem User nicht zugeordnet sind
    """
    # Die beiden Ergebnislisten
    vorhanden = {}
    optional = {}

    # Eingangsparameter ist eine Liste von Userids mit den zugehörenden Listen an AFen:
    for userid in af_dict:
        af_menge = af_dict[userid]

        for af in af_menge:
            # Für genau eine Kombination aus UserID und AF wird gesucht,
            # ob sie als Rolle (oder mehrere Rollen)
            # bereits administriert ist: ex(istierende Rollen).
            # Zusätzlich werden alle Möglichkeiten der Administration angeboten,
            # die noch nicht genutzt wurden: opt(ionale Rollen).
            (ex, opt) = suche_rolle_fuer_userid_und_af(userid, af)
            # Flache Datenstruktur für Template erforderlich
            tag = '!'.join((userid, af))
            vorhanden[tag] = ex
            optional[tag] = opt
    return vorhanden, optional


def stamm_userid(userid):
    """
    Liefert die XV-Nummer zu einer UserID zurück (die Stammnummer der Identität zur UserID)
    :param userid: Eine beliebige UserID einer Identität
    :return: Die StammuserID der Identität
    """
    return 'X' + userid[1:]


def suche_rolle_fuer_userid_und_af(userid, af):
    """
    Liefere für einen AF einer UserID die Liste der dazu passenden Rollen.
    Auch hier wird unterscheiden zwischen den existierenden Rollen des Users
    und den optionalen Rollen.
    Wichtig ist hier die Unterscheidung zwischen der Identität (in unserem Fall UserIDen XV\d{5}
    und den unterschiedlichen UserIDen ([XABCD]V\d{5})
    :param userid: Die UserID, für die die AF geprüft werden soll
    :param af: Die AF, die geprüft werden soll
    :return: Tupel mit zwei Listen: den vorhandenen Rollen und den optionalen Rollen
        Wichtig bei den Liste ist, dass beide als letztes einen leeren String erhalten.
        Das stellt sicher, dass in der Template-Auflösung nicht die Chars einzeln angezeigt werden,
        wenn nur eine einzige Rolle gefunden wurde.
    """

    # Hole erst mal die Menge an Rollen, die bei dieser AF und der UserID passen
    rollen = TblRollehataf.objects.filter(af__af_name=af)
    rollen_liste = [str(rolle) for rolle in rollen]

    # Dann hole die Rollen, die dem User zugewiesen sind
    userrollen = TblUserhatrolle.objects \
        .filter(userid=stamm_userid(userid)) \
        .order_by('rollenname')

    # Sortiere die Rollen, ob sie dem dem User zugeordnet sind oder nicht
    vorhanden = [str("{}!{}".format(einzelrolle.userundrollenid, einzelrolle.rollenname))
                 for einzelrolle in userrollen
                 if str(einzelrolle.rollenname) in rollen_liste
                 ]

    # Mengenoperation: Die Differenz zwischen den Rollen,
    # die zur AF gehören und den Rollen, die der User bereits hat,
    # ist die Menge der Rollen, die als optional ebenfalls für die AF genutzt werden kann.
    # Leider sind "rollen_liste" und "vorhanden" inzwischen in verschiedenen Formaten,
    # deshalb geht die einfache Mengendifferenzbildung nicht mehr.
    optional = set(rollen_liste)
    for s in set(vorhanden):
        optional.discard(s.split('!')[1])
    optional = list(optional)
    optional.sort()
    # Das hier sind die beiden Leerstrings am Ende der Liste
    vorhanden.append('')
    optional.append('')
    return vorhanden, optional


def hole_af_mengen(userids, gesuchte_rolle):
    """
    Hole eine Liste mit AFen, die mit der gesuchten Rolle verbunden sind.
    Erzeuge die Liste der AFen, die mit den UserIDs verbunden sind
    und liefere die Menge an AFen, die beiden Kriterien entsprechen.
    Für die Anzeige im Portal liefert die Funktion eine möglichst flache Datenstruktur.
    :param userids: Dictionary mit Key = Name der Identität und
                    val = Liste der UserIDs der Identität
                    (Beispiel: userids['Eichler, Lutz'] = ['XV13254])
    :param gesuchte_rolle: Wenn None, suche nach allen Rollen,
                    sonst filtere nach dem Suchstring (icontains).
                    Ist die gesuchte Rolle "-", dann filtere nach unzugewiesenen AFen.
                    gesuchte_rolle wird als None übergeben, wenn der Suchstring "*" verwendet wurde
    :return: af_dict{}[UserID] = AF[]

    """

    such_af = liefere_af_zu_rolle(gesuchte_rolle)

    af_dict = {}
    for name in dict(userids):
        for userid in userids[name]:  # Die erste UserID ist die XV-Nummer
            if gesuchte_rolle is None:  # Finde alle AFen zur UserID
                af_liste = TblGesamt.objects.filter(
                    userid_name_id__userid=userid).filter(geloescht=False)

            elif gesuchte_rolle == "-":
                # Finde alle AFen zur UserID, die nicht Rollen zugeordnet sind
                bekannte_rollen = TblUserhatrolle.objects.filter(
                    userid=userids[name][0]).values('rollenname')

                # Irgendwelche Merkwürdigkeiten?
                suche_nach_none_wert(bekannte_rollen)
                unerwuenschte_af = TblRollehataf.objects.filter(rollenname__in=bekannte_rollen) \
                    .exclude(af__af_name=None) \
                    .values('af__af_name')

                af_liste = TblGesamt.objects.filter(userid_name_id__userid=userid) \
                    .filter(geloescht=False) \
                    .exclude(enthalten_in_af__in=unerwuenschte_af)
            else:
                af_liste = TblGesamt.objects.filter(userid_name_id__userid=userid) \
                    .filter(geloescht=False) \
                    .filter(enthalten_in_af__in=such_af)

            af_menge = {af.enthalten_in_af for af in af_liste}
            af_dict[userid] = af_menge
    return af_dict


def liefere_af_zu_rolle(gesuchte_rolle):
    """
    Hole die Einträge in TblRolleHatAF, die zu einer angegebenen Rolle passen.
    Wurde None oder "-" als Rollenname übergeben, liefere die Liste für alle Rollen.
    :param gesuchte_rolle: EIN Rollenname oder None oder "-"
    :return: Trefferergebnis der Abfrage
    """
    if gesuchte_rolle is None or gesuchte_rolle == "-":
        return TblRollehataf.objects.all() \
            .values('af__af_name') \
            .distinct() \
            .order_by('af__af_name')
    else:
        return TblRollehataf.objects \
            .filter(rollenname__rollenname__icontains=gesuchte_rolle) \
            .values('af__af_name') \
            .distinct() \
            .order_by('af__af_name')


def suche_nach_none_wert(bekannte_rollen):
    """
    Suche nach Einträgen in der Tabelle RolleHatAf, bei denen die AF None ist.
    :param bekannte_rollen:
    :return: True, wenn was gefunden wurde, sonst False
    """
    none_af = TblRollehataf.objects.filter(
        rollenname__in=bekannte_rollen).filter(af__af_name=None)
    if len(none_af) > 0:
        print('WARNING: Möglicherweise Irritierende Resultate, weil None in Suchmenge enthalten ist:')     # NOQA
        print('none_af:', len(none_af), none_af)
        print('Der Wert wurde in dieser Abfrage herausgefiltert, kann aber an andere Stelle irritieren.')  # NOQA
        print('Das entsteht, wenn als AF in einer Rolle "-----" selektiert wurde')
        return True
    return False


def UhR_hole_rollengefilterte_daten(erweiterte_namen_liste, gesuchte_rolle=None):
    """
    Finde alle UserIDs, die über die angegebene Rolle verfügen.
    Wenn gesuchte_rolle is None, dann finde alle Rollen.

    Erzeuge die Liste der UserIDen, die mit den übergebenen Namen zusammenhängen
    Dann erzeuge die Liste der AFen, die mit den UserIDs verbunden sind
    - Notiere für jede der AFen,
      welche Rollen Grund für diese AF derzeit zugewiesen sind (aus UserHatRolle)
    - Notiere, welche weiteren Rollen, die derzeit nicht zugewiesen sind,
      für diese AF in Frage kämen

    Liefert die folgende Hash-Liste zurück:
    Rollenhash{}[(Name, UserID, AF)] = (
        (liste der vorhandenen Rollen, in denen die AF enthalten ist),
        (liste weiterer Rollen, in denen die AF enthalten ist)
        )

    Liefert die Namen / UserID-Liste zurück
    userids{}[Name] = (Userids zu Name, alfabeitsch absteigend sortiert: XV, DV, CV, BV, AV)

    :param namen_liste: Zu welchen Namen soll die Liste erstellt werden?
    :param gesuchte_rolle: s.o.
    :return: (rollenhash, userids)
    """
    userids = {
        name: hole_userids_zum_namen(name) for name in erweiterte_namen_liste
    }

    af_dict = hole_af_mengen(userids, gesuchte_rolle)
    (vorhanden, optional) = hole_rollen_zuordnungen(af_dict)
    return userids, af_dict, vorhanden, optional


def soll_komplett(request, row):
    """
    Liefere für einen konkreten User in row, ob für ihn die Komplettdarstellung erfolgen soll
    oder die eingeschränkte Sicht
    :param request: Für die Orga-Definition benötigt
    :param row: Der aktuelle User
    :return: True falls für den User die KOmmplettdarstellung erfolgen soll
    """
    teamnr = request.GET.get('orga')
    teamqs = TblOrga.objects.get(id=teamnr)
    assert teamqs.freies_team is not None
    eintraege = teamqs.freies_team.split('|')
    for e in eintraege:
        zeile = e.split(':')
        if row.name.lower() == zeile[0].lower():
            return zeile[1].lower() == 'komplett'
    return False
