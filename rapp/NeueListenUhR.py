from rapp.excel import Excel
from django.shortcuts import render
from django.utils.encoding import smart_str
from rapp.forms import ShowUhRForm
from rapp.views import version
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_erzeuge_listen_mit_rollen
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_hole_rollengefilterte_daten


# Für alle selektierten User und deren IDs alle AFen,
# die für die konkrete UserID nicht zu Rollen zugeordnet sind
class NeueListenUhr:
    excel = None

    def setze_context(self, request):
        """
        Diese Factory-Klasse selektiert zunächst alle AFen,
        die für den jeweiligen User noch nicht mit einer Rolle belegt sind.

        Darüber hinaus werden alle Optionen gesucht, die für die jeweiligen AFen gültig sind.

        :param request: GET oder POST Request vom Browser
        :return: Context für das zu rendernde HTML
        """
        namen_liste, panel_filter, rollen_liste, rollen_filter \
            = UhR_erzeuge_listen_mit_rollen(request)
        userids, af_per_uid, vorhanden, optional = UhR_hole_rollengefilterte_daten(
            namen_liste, "-")

        form = ShowUhRForm(request.GET)
        return {
            'filter': panel_filter, 'form': form,
            'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
            'userids': userids,
            'af_per_uid': af_per_uid,
            'vorhanden': vorhanden,
            'nur_neue': True,
            'optional': optional,
            'version': version,
        }

    def behandle(self, request, _):
        """
        Erzeuge die HTML-Sicht für den Dialog
        :param request: der HTTP-Request, enthält '-' als rollenname
        :param _: wird nicht benötigt, ist bei anderen die ID
        :return: Das gerenderte HTML
        """
        return render(request, 'rapp/panel_UhR_rolle.html', self.setze_context(request))

    def get_options(self, key):
        return self.context['optional'][key]

    def get_num_optional(self, key):
        # -1 wegen des Leerstrings am Ende
        return len(self.get_options(key)) - 1

    def behandle_userid(self, name, userid):
        """
            Erzeuge die CSV-Ausgaben zeilenweise für einen Namen mit der jeweiligen UserID
        """
        for af in sorted(self.context['af_per_uid'][userid]):
            if af == 'ka':  # Das Zeug interessiert niemanden
                continue

            bastelkey = userid + '!' + af
            options = self.get_options(bastelkey)
            numoptional = self.get_num_optional(bastelkey)

            if numoptional == 0:  # keine Optionen gefunden, also nur die gefundene AF ausgeben
                self.excel.writerow([name, userid, af, "--"])
            else:
                for i in range(numoptional):
                    self.excel.writerow([name, userid, af, options[i]])

    def exportiere(self, request, _):
        """
        Liefert die Daten dieser Klasse als CSV-Datei.

        :param request: der HTTP-Request, enthält '-' als rollenname
        :return: Die csv-Daten zum Download
        """
        self.context = self.setze_context(request)
        userids = self.context['userids']

        headline = [
            smart_str(u'Name'),
            smart_str(u'UserID'),
            smart_str(u'AF'),
            smart_str(u'Mögliche Rollen')
        ]
        self.excel = Excel("AFen_ohne_Rollenzuordnung.csv")
        self.excel.writerow(headline)

        # ToDo: Geht das python-mäßiger uind einfacher in nur einer Schleife?
        for name in userids:
            for userid in userids[name]:
                self.behandle_userid(name, userid)

        return self.excel.response
