from urllib.parse import unquote

from django import forms

from .models import TblUserhatrolle
from .models import hole_organisationen


class ShowUhRForm(forms.ModelForm):
    """
    Das hätte man auch einfacher haben können,
    indem die relevanten Infos in views.py eingetragen worden wären
    """

    class Meta:
        model = TblUserhatrolle
        fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


# Hier ist das anders, weil eine Methode zur Klasse hinzugekommen ist:
# Initialisiere das Input Formular für neue Rolleneinträge mit der UserID,
# dem Modell und der Zuständigkeitsstufe
class CreateUhRForm(forms.ModelForm):
    """
    Das hätte man auch einfacher haben können,
    indem die relevanten Infos in views.py eingetragen worden wären
    """

    class Meta:
        model = TblUserhatrolle
        fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

    def __init__(self, *args, **kwargs):
        """
        Hole die 3 Parameter, die von der ReST-Schnittstelle übergeben wurden
        und fülle damit eine initial-Struktur.
        Damit werden die drei Werte Userid, Rollenname
        und Schweerpunkt/Vertretung initialisiert angezeigt.

        :param args:
        :param kwargs: Das Wesentliche steht hier drin
        """

        self.userid = kwargs.pop('userid', None)
        if self.userid is not None:
            self.userid = 'X' + self.userid[1:7].upper()
        self.rollenname = unquote(kwargs.pop('rollenname', 'Spielrolle'))
        self.schwerpunkt_vertretung = kwargs.pop('schwerpunkt_vertretung', 'Schwerpunkt')
        super(CreateUhRForm, self).__init__(*args, **kwargs)

        self.initial['userid'] = self.userid
        self.initial['rollenname'] = self.rollenname
        self.initial['schwerpunkt_vertretung'] = self.schwerpunkt_vertretung


class ImportForm(forms.Form):
    """
    Die ersten Parameter, die für einen CSV-Import abgefragt werden müssen.
    Hier ist das Thema das Initialisieren des Organisations-Choicefields.
    """
    organisation = forms.ChoiceField(label='Organisation')
    datei = forms.FileField(label='Dateiname')
    update_gruppe = forms.BooleanField(required=False, initial=False,
                                       label='Gruppenzugehörigkeit aktualisieren')

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.fields['organisation'].choices = hole_organisationen()


class ImportFormSchritt3(forms.Form):
    """
    Das hier behandelte boolean Field ist nicht Inhalt des Models,
    sondern ändert lediglich den Workflow.
    Der Abschluss des zweiten Schritts besteht ebenfalls nur aus einer Bestätigung,
    deshalb sind auch hier keine Datenfelder angegeben
    (eventuell kann hier noch ein Flag angegeben werden, ob Doppeleinträge gesucht wertden sollen).
    """
    doppelte_suchen = forms.BooleanField(label='Suche nach doppelten Einträgen (optional)',
                                         required=False)


class FormUmbenennen(forms.Form):
    """
    Formular für das Umbenennen von Rollen
    """
    alter_name = forms.CharField(max_length=50, label='Bestehender Rollenname',
                                 error_messages={'required': 'Bitte geben Sie den bestehenden Rollennamen an',  # NOQA
                                                 'invalid': 'Bestehender Rollennamen wird benötigt'})           # NOQA
    neuer_name = forms.CharField(max_length=50, label='Zukünftiger Rollenname',
                                 error_messages={'required': 'Bitte geben Sie den zukünftigen Rollennamen an',  # NOQA
                                                 'invalid': 'Zukünftiger Rollennamen wird benötigt'})           # NOQA


class FormNPUSetzen(forms.Form):
    """
    Formular für das Erzeugen der Rollen für NPUs
    Wir benötigen keine Eingfabefelder
    """


class FormMussKann(forms.Form):
    """
    Formular für das Ermitteln der Organisation für die Muss-Kann-Liste
    """
    orgasymbol = forms.CharField(max_length=50,
                                 label='Orgasymbol für die Ermittlung (Wildcard mit _ und %)',
                                 error_messages={
                                     'required': 'Bitte geben Sie das Orgasymbol an, für das die Liste erzeugt werden soll, gegebenenfalls mit Wildcards',  # NOQA
                                     'invalid': 'Orgasymbol wird benötigt'
                                     })
