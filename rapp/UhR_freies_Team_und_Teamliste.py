from __future__ import unicode_literals
from rapp.models import TblOrga


def behandle_freies_team(panel_liste, request, teamqs):
    """
    Wenn in der tblOrga für die aktuelle Selektion ein Freies_Team eingetragen ist,
    müssen an dieser Stelle zunächst die angegebenen Namen berücksichtigt werden.
    Die Anzeigeinhalte werden dann später bearbeitet.
    :param panel_liste: Das bisherige Panel-QS
    :param request: Das Übliche
    :param teamqs: Hieran hängt in dieser Funktion der Inhalt "freies_team"
    :return: gefilterte Namensliste als QuerySet
    """
    eintraege = teamqs.freies_team.split('|')
    user = []
    for e in eintraege:
        user += [e.split(':')[0]]  # erster Teil ist der Name, zweiter Teil die gewünschte Anzeige
    print('gesuchte User =', user)
    namen_liste = panel_liste.filter(name__in=user)
    return behandle_ft_oder_tl(namen_liste, request)


def behandle_teamliste(panel_liste, request, teamqs):
    """
    Wenn in der tblOrga für die aktuelle Selektion eine Teamliste eingetragen ist,
    müssen an dieser Stelle die angegebenen Namen berücksichtigt werden.
    :param panel_liste: Das bisherige Panel-QS
    :param request: Das Übliche
    :param teamqs: Hieran hängt in dieser Funktion der Inhalt "teamliste"
    :return: gefilterte Namensliste als QuerySet
    """
    teamliste = teamqs.teamliste.split(',')
    # print('Teamliste =', teamliste)
    namen_liste = panel_liste.filter(orga__team__in=teamliste)
    return behandle_ft_oder_tl(namen_liste, request)


def behandle_ft_oder_tl(namen_liste, request):
    """
    In den rufenden Funktionen wurde bereits eine Namensliste erstellt.
    Diese muss nun allerdings noch weiter gefiltert werden,
    falls eine Namensteil oder eine Gruppe als Filterkriterien angegeben wurden.
    Dabei können nicht die normalen Filterfunktionen verwendet werden, weil ja die Angabe
    freies_teamm oder teamliste ghenau den anderen Filterkritereien widersprechen könnten.
    Außerdem werden von dieser Funktion nur XV-Nummern-Einträge zurückgeliefert,
    das vereinfacht das weitere Vorgehen erheblich.

    :param namen_liste: Die besher gefundenen Namen als QuerySet
    :param request: Das Übliche
    :return: Die möglicherweise weiter gefilterte Nanemsliste
    """
    name = request.GET.get('name')
    gruppe = request.GET.get('gruppe')
    # print('gefundene namen_liste vor Filterung =', namen_liste)
    if gruppe is not None and gruppe != '':
        # print('Filtere nach Gruppe', gruppe)
        namen_liste = namen_liste.filter(gruppe__icontains=gruppe)
        # print(namen_liste)
    if name is not None and name != '':
        # print('Filtere nach Name', name)
        namen_liste = namen_liste.filter(name__istartswith=name)
        # print(namen_liste)
    namen_liste = namen_liste.filter(userid__istartswith="xv").select_related("orga")
    # print('Letztendliche Liste der Namen:', namen_liste)
    return namen_liste


def freies_team(request):
    return not kein_freies_team(request)


def kein_freies_team(request):
    """
    Ist in der aktuellen Selektion ein Eintrag in der Teamdefinition "freies_team" gesetzt?
    :param request:
    :return: True, wenn "freies_feld" weder None noch '' ist
    """
    teamnr = request.GET.get('orga')
    if teamnr is None or teamnr == '':
        return True

    teamqs = TblOrga.objects.get(id=teamnr)
    return teamqs.freies_team is None or teamqs.freies_team == ''
