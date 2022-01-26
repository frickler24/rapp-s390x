from django.shortcuts import render
from rapp.forms import ShowUhRForm
from rapp.views import pagination
from rapp.views import version
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_erzeuge_listen_ohne_rollen, UhR_hole_daten


# Ein einzelner User mit seiner UserID und all seinen vergebenen Rollen
class EinzelUhr:
    def setze_context(self, request, id):
        """
        Finde alle relevanten Informationen zur aktuellen Selektion
        Das ist die Factory-Klasse für die Betrachtung einzelner User und deren spezifischer Rollen

        :param request: GET oder POST Request vom Browser
        :param id: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen;
            0 -> kein User gewählt
        :return: Gerendertes HTML
        """
        namen_liste, panel_filter, rollen_liste, rollen_filter \
            = UhR_erzeuge_listen_ohne_rollen(request)
        userHatRolle_liste, selektierter_name, userids, usernamen, \
            selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID \
            = UhR_hole_daten(namen_liste, id)
        paginator, pages, pagesize = pagination(request, namen_liste, 100)

        form = ShowUhRForm(request.GET)
        return {
            'paginator': paginator, 'pages': pages, 'pagesize': pagesize,
            'filter': panel_filter, 'form': form,
            'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
            'userids': userids, 'usernamen': usernamen, 'afmenge': afmenge,
            'userHatRolle_liste': userHatRolle_liste,
            'id': id,
            'selektierter_name': selektierter_name,
            'selektierte_userid': selektierte_haupt_userid,
            'selektierte_userids': selektierte_userids,
            'afmenge_je_userID': afmenge_je_userID,
            'version': version,
        }

    def behandle(self, request, id):
        """
        Erzeuge die HTML-Sicht für den Dialog

        :param request: Der HTTP-Request, kann '' oder einen Rollennamenteil beinhalten
        :param id: optional die ID eines Users
        :return: Das gerenderte HTML
        """
        return render(request, 'rapp/panel_UhR.html', self.setze_context(request, id))
