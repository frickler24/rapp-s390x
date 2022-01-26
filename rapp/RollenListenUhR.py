from django.shortcuts import render
from django.utils.encoding import smart_str
from rapp.forms import ShowUhRForm
from rapp.views import version
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_erzeuge_listen_mit_rollen
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_hole_rollengefilterte_daten
from rapp.view_UserHatRolle_Datenbeschaffung import hole_unnoetigte_afen
from rapp.excel import Excel


# Für alle selektierten Used und ihre IDs alle AFen und die dazugehörigen Rollen (+ / *)
class RollenListenUhr:
    def __init__(self):
        """
        Wir sammeln Daten schrittweise ein,
        da wir dem Excel nur komplette Zeilen übergeben dürfen.
        Außerhalb der Klasse interesssiert die Daten niemand
        """
        self.__context = None
        self.__excel = None
        self.__userids = None
        self.__userid = None
        self.__name = None
        self.__numvorhanden = 0
        self.__numoptional = 0
        self.__af = None

    # ###########################################################################
    # behandle() erzeugt das HTML für den Dialog,
    # exportiere() liefert eine csv-Datei an den Browser.
    # Jeweils werden die gewünschten Rollen-Modi (+, -, *, rollenname, None) beachtet.
    # ###########################################################################

    def behandle(self, request, _):
        """
        Erzeuge die HTML-Sicht für den Dialog
        :param request: der HTTP-Requerst, kann * oder * enthalten in rollenname
        :param _: entsteht durch den Fabric-Aufruf (ist id in anderer Behandlung)
        :return: Das gerenderte HTML
        """
        html, context = self.setze_context(request)
        return render(request, html, context)

    def exportiere(self, request, _):
        """
        Finde die korrekte Exportfuntion anhand des Parameters rollenmenge
        :param request: Der Request
        :param _: entsteht durch den Fabric-Aufruf (ist id in anderer Behandlung)
        :return: Die CSV-Inhalte zum Download
        """
        gesuchte_rolle = request.GET.get('rollenname', None)
        if gesuchte_rolle == '+':
            return self.exportiere_plus(request)
        if gesuchte_rolle == '*':
            return self.exportiere_stern(request)
        else:
            print('RollenListenUhr: gesuchte_rolle ist merkwürdigerweise >>>{}<<<',
                  format(gesuchte_rolle))

    def setze_context(self, request):
        """
        Finde alle relevanten Informationen zur aktuellen Selektion
        Dies dient der Betrachtung aller User mit spezifischen Rollen- oder AF-Namen

        :param request: GET oder POST Request vom Browser
        :return: Zu renderndes HTML-File, Context für das zu rendernde HTML
        """
        (namen_liste, panel_filter, rollen_liste, rollen_filter) = \
            UhR_erzeuge_listen_mit_rollen(request)

        form = ShowUhRForm(request.GET)
        gesuchte_rolle = request.GET.get('rollenname', None)

        # Finde alle AFen in den verwendeten Rollen, die keinem der User zugewiesen sind
        if gesuchte_rolle == "+":
            af_liste = hole_unnoetigte_afen(namen_liste)
            context = {
                'filter': panel_filter, 'form': form,
                'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
                'namen_liste': namen_liste,
                'af_liste': af_liste,
                'version': version,
            }
            return 'rapp/panel_UhR_ueberfluessige_af.html', context

        if gesuchte_rolle == "*":
            gesuchte_rolle = None

        (userids, af_per_uid, vorhanden, optional) \
            = UhR_hole_rollengefilterte_daten(namen_liste, gesuchte_rolle)

        context = {
            'filter': panel_filter, 'form': form,
            'rollen_liste': rollen_liste, 'rollen_filter': rollen_filter,
            'userids': userids,
            'af_per_uid': af_per_uid,
            'vorhanden': vorhanden,
            'optional': optional,
            'version': version,
        }
        return 'rapp/panel_UhR_rolle.html', context

    def zweiter(self, string):
        """
        Liefert den zweiten Teil eines mit '!' getrennten Strings.
        Wenn der String Leerstring ist
        oder der String nicht leer ist, aber kein '!' enthält,
        liefere den Eingangsstring zurück.
        Wenn der String mehrere '!' enthält, liefer den zweiten Teil.
        :param string: Der String xxx!yyyyy
        :return: yyyyy oder '' wenn String == ''
        """
        if string == '' or '!' not in string:
            return string
        return string.split('!')[1]

    # ###########################################################################
    # Behandlung der Abfrage nach "+" für Export
    # ###########################################################################
    def exportiere_plus(self, request):
        """
        Liefert die Liste der AFen, die zur aktuellen Treffernmenge
        zwar in den Rollen modelliert sind, aber keine Verwendung bei den Usern finden.

        :param request: Der HTML-Request mit den gewünschten Filtern und '+' als Rollenname
                        Achtung: das '+' muss ein %2B sein, sonst wird es vom Button eliniert!
        :return: Die csv-Daten zum Download
        """
        headline = [
            smart_str(u'Rollenname'),
            smart_str(u'Ungenutze AF'),
        ]
        excel = Excel("rollen.csv")
        excel.writerow(headline)

        _, context = self.setze_context(request)
        for af in context['af_liste']:
            line = [
                af['rollenname__rollenname'],
                af['af__af_name']
            ]
            excel.writerow(line)
        return excel.response

    # ###########################################################################
    # Behandlung der Abfrage nach "*" für Export
    # ###########################################################################
    def exportiere_stern(self, request):
        """
        Liefert die Liste der AFen, die zur aktuellen Treffernmenge mit Rollen hinterlegt sind
        sowie die Menge der Rollen,
        die zusätzlich oder alternativ für die AF vergeben werden könnten.

        self.behandle_name und die darin gerufenen Funktionen "füllen" self.__excel,
        damit es abschließend als zu übermittelnde Datei zurückgelieferrt werden kann.

        :param request: Der HTTP-Request
        :return: Die csv-Daten zum Download
        """
        _, self.__context = self.setze_context(request)
        self.__userids = self.__context['userids']

        headline = [
            smart_str(u'Name'),
            smart_str(u'UserID'),
            smart_str(u'AF'),
            smart_str(u'Vergebene Rolle'),
            smart_str(u'Mögliche weitere Rollen')
        ]
        self.__excel = Excel("Rollenzuordnungen_zu_AFen.csv")
        self.__excel.writerow(headline)

        for name in self.__userids:
            self.behandle_name(name)

        return self.__excel.response

    def get_vorhanden(self, key):
        """
        Liefert die Liste der vorhandenen Rollen zur userID!AF-Kombination

        :param key: userID!AF-Kombination
        :return: Die Liste der vorhandenen Rollen zur userID!AF-Kombination
        """
        return self.__context['vorhanden'][key]

    def get_optional(self, key):
        """
        Liefert die Liste der optionalen Rollen zur userID!AF-Kombination

        :param key: userID!AF-Kombination
        :return: Die Liste der optionalen Rollen zur userID!AF-Kombination
        """
        return self.__context['optional'][key]

    def get_num_vorhanden(self, key):
        """
        Liefere die Anzahl vorhandener (dem User zugewiesener) Rollen
        (-1 wegen des Leerstrings am Ende)
        """
        return len(self.get_vorhanden(key)) - 1

    def get_num_optional(self, key):
        """ Liefere die Anzahl optionaler Rollen (-1 wegen des Leerstrings am Ende) """
        return len(self.get_optional(key)) - 1

    def gather_line(self, vorhanden, optional):
        """ Baue alle bereits gesammelten Informationen zu einer Liste zusammen """
        return [self.__name, self.__userid, self.__af, vorhanden, optional]

    def get_vorhanden_eintrag(self, i, key):
        """
        Liefert den korrekten Rollennamen zur derzeit behandelten AF

        :param i: In der wievielten Zeile der vorhandenen bzw. optionalen Elemente befinden wir uns
        :param key: Die zusammengesetzte UserID!AF-Angabe, die gerade dokumentiert wird
        :return: Den Namen der Rolle für genau diese eine Zeile der CSV-Datei,
                 gegebenenfalls wiederholt, wenn keine weitere Rolle gefunden wird
                 (das filtert nachher das Template über on_change heraus)
                 oder 'keine Zuordnung', wenn diese AF zu keiner der zugeordneten Rollen gehört
        """
        if i < self.__numvorhanden:
            # den aktuellen Wert ermitteln
            return self.zweiter(self.__context['vorhanden'][key][i])
        elif i >= 0:
            # letzten Wert bis zum Ende wiederholen für bessere Darstellung
            return self.zweiter(self.__context['vorhanden'][key][self.__numvorhanden - 1])
        else:
            # Wenn schon für i=0 nichts zu finden ist, gibt es eben nichts anzuzeigen
            return 'keine Zuordnung'

    def getcsvline(self, i, key):
        """
        Liefert die Daten für eine Zeile in der CSV-Datei:
        zu einem Namen und einer UserID wird für eine AF zurückgeliefert:
        - die Mmenge der gegebenenfalls vorhandenen Rollen
        - sowie die Menge der Rollen,
          die zusätzlich oder alternativ für die AF vergeben werden könnten.

        :param i: In der wievielten Zeile der vorhandenen bzw. optionalen Elemente befinden wir uns
        :param key: Die zusammengesetzte UserID!AF-Angabe, die gerade dokumentiert wird
        :return: Die Daten für genau diese eine Zeile der CSV-Datei
        """
        return self.gather_line(
            self.get_vorhanden_eintrag(i, key),
            self.get_optional(key)[i] if i < self.__numoptional else ' '
        )

    def behandle_AF(self, af):
        """
        Ermittle für jede AF, in welcher für die UserID vergebenen Rolle sie vorkommt
        und welche weiteren, optionalen Rollen sie enthalten

        :param request: Die AF zu der die Informationen gesucht werden sollen.
                        Weitere, implizite Parameter sind bereits ermittelte Attribute der Klasse.
        :return: None; Als Seiteneffekt werden Zeilen in self.__excel geschrieben
        """
        self.__af = af
        bastelkey = self.__userid + '!' + self.__af
        self.__numvorhanden = self.get_num_vorhanden(bastelkey)
        self.__numoptional = self.get_num_optional(bastelkey)

        if (self.__numvorhanden == 0 and self.__numoptional == 0):
            line = [self.__name, self.__userid, self.__af, " ", " "]
            self.__excel.writerow(line)
        else:
            for i in range(max(self.__numvorhanden, self.__numoptional)):
                line = self.getcsvline(i, bastelkey)
                self.__excel.writerow(line)

    def behandle_userid(self, userid):
        """ Iteriere über die AFen zu den UserIDs zum bereits vorher ermittelten Namen """
        self.__userid = userid
        for af in sorted(self.__context['af_per_uid'][self.__userid]):
            if af == 'ka':  # Das Zeug interessiert niemanden
                continue
            self.behandle_AF(af)

    def behandle_name(self, name):
        """ Iteriere über die UserIDs zum Namen """
        self.__name = name
        for userid in self.__userids[self.__name]:
            self.behandle_userid(userid)
