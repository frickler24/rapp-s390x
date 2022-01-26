from __future__ import unicode_literals
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView
from rapp.UhR import UhR
from rapp.forms import CreateUhRForm
from rapp.models import TblUserhatrolle

###################################################################
# Zuordnungen der Rollen zu den Usern (TblUserHatRolle ==> UhR)
# Diese Funktionalität wird über das Klassenmodell von Django behandelt.
###################################################################

class UhRCreate(CreateView):
    """
    Erzeugt eine neue Rolle für einen User.
    Sowohl User als auch Rolle müssen bereits existieren.
    """
    model = TblUserhatrolle
    template_name = 'rapp/uhr_form.html'
    # Entweder form-Angabe oder Field-Liste
    form_class = CreateUhRForm

    # fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

    def get_form_kwargs(self):
        """
        Definiere die benötigten benannten Parameter
        :return: kwargs mit den Inhalten der Oberklasse und den benötigten Parametern
        """
        kwargs = super(UhRCreate, self).get_form_kwargs()
        kwargs['rollenname'] = ""
        kwargs['schwerpunkt_vertretung'] = ""
        kwargs['userid'] = self.kwargs['userid']

        if 'rollenname' in self.kwargs:
            kwargs['rollenname'] = self.kwargs['rollenname']
        if 'schwerpunkt_vertretung' in self.kwargs:
            kwargs['schwerpunkt_vertretung'] = self.kwargs['schwerpunkt_vertretung']
        return kwargs

    # Im Erfolgsfall soll die vorherige Selektion im Panel "User und Rollen" wieder aktualisiert gezeigt werden.
    # Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
    def get_success_url(self):
        return success_url(self)


class UhRDelete(DeleteView):
    """Löscht die Zuordnung einer Rolle zu einem User."""
    model = TblUserhatrolle
    template_name = 'rapp/uhr_confirm_delete.html'

    # Nach dem Löschen soll die vorherige Selektion im Panel "User und Rollen" wieder aktualisiert gezeigt werden.
    # Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzten Suchparameter benötigt.
    def get_success_url(self):
        usernr = self.request.GET.get('user', "0")  # Sicherheitshalber - falls mal kein User angegeben ist

        urlparams = "%s?"
        for k in self.request.GET.keys():
            if k != 'user' and self.request.GET[k] != '':
                urlparams += "&" + k + "=" + self.request.GET[k]
        # Falls dieUsernr leer ist, kommmen wir von der Rollensicht des Panels, weil dort die Usernummer egal ist.
        # Die Nummer ist nur gesetzt wen wir auf der Standard-Factory aufgerufen werden.
        if usernr == "":
            return urlparams % reverse('user_rolle_af')
        else:
            return urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})


class UhRUpdate(UpdateView):
    """Ändert die Zuordnung von Rollen zu einem User."""
    # ToDo: Hierfür gibt es noch keine Buttons. Das ist noch über "Change" inkonsistent abgebildet
    model = TblUserhatrolle
    fields = '__all__'

    # Im Erfolgsfall soll die vorherige Selektion im Panel "User und RolleN" wieder aktualisiert gezeigt werden.
    # Dazu werden nebem dem URL-Stamm die Nummer des anzuzeigenden Users sowie die gesetzte Suchparameter benötigt.
    def get_success_url(self):
        return success_url(self)


def success_url(self):
    """
        Liefert die URL zurück, die im Success-Fall nach der Bearbeitung des UserHatRolle-Eintrags aufgerufden wird
    """
    usernr = self.request.GET.get('user', 0)  # Sicherheitshalber - falls mal kein User angegeben ist

    urlparams = "%s?"
    for k in self.request.GET.keys():
        if k != 'user' and self.request.GET[k] != '':
            urlparams += "&" + k + "=" + self.request.GET[k]
    return urlparams % reverse('user_rolle_af_parm', kwargs={'id': usernr})


# Zeige das Selektionspanel
# Das wird nicht über die Klassenvariante, sondern mit der alten Methode erzeugt,
# weil dann das Handling get GETs und POSTs einfacher schien.
# ToDo: Auch mal umstellen auf Class Based
def panel_UhR(request, id=0):
    """
    Finde die richtige Anzeige und evaluiere sie über das factory-Pattern

    - wenn rollenname = "-" ist, rufe die Factory "nur_neue"
    - wenn rollenname anderweitig gesetzt ist, rufe die Factory "rolle"
    - wenn rollenname nicht gesetzt oder leer ist und afname gesetzt ist, rufe factory "af"
    - Ansonsten rufe die Standard-Factory "einzel"

    :param request: GET oder POST Request vom Browser
    :param id: ID des XV-UserID-Eintrags, zu dem die Detaildaten geliefert werden sollen
    :return: Gerendertes HTML
    """
    assert request.method == 'GET', 'Irgendwas ist im panel_UhR nicht über GET angekommen: ' + request.method

    if request.GET.get('rollenname', None) is None:
        name = 'einzel'
    elif request.GET.get('rollenname', None) == "-":
        name = 'nur_neue'
    elif request.GET.get('rollenname', None) != "":
        name = 'rolle'
    # elif request.GET.get('afname', None) != "":
    #    name = 'af'
    else:
        name = 'einzel'

    obj = UhR.factory(name)
    if request.GET.get('export', None) is not None:
        return obj.exportiere(request, id)
    else:
        return obj.behandle(request, id)


