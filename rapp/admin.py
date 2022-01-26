# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
# Zum Verändern der Standardeigenschaften eines Textpanes
from django.db import models
from django.forms import Textarea
# Für den Im- und Export
from import_export.admin import ImportExportModelAdmin
from mdeditor.widgets import MDEditorWidget

from rapp.models import ACLGruppen
# Die Datenbanken / Models
from rapp.models import TblUebersichtAfGfs, \
    TblUserIDundName, TblOrga, TblPlattform, \
    TblGesamt, TblGesamtHistorie, \
    TblRollen, TblAfliste, TblUserhatrolle, TblRollehataf, \
    Tblsubsysteme, Tblsachgebiete, TblDb2, \
    RACF_Rechte, Orga_details, \
    Modellierung, Direktverbindungen, \
    Manuelle_Berechtigung
from rapp.resources import GesamtExporterModel, \
    ModellierungExporterModel, DirektverbindungenExporterModel


# Register your models here.

# Vorwärtsreferenzen gehen nicht in python :-(
# Inline function to show all Instances in other view
class UserhatrolleInline(admin.TabularInline):
    model = TblUserhatrolle
    extra = 1

    fields = ['userundrollenid', 'userid', 'rollenname',
              'schwerpunkt_vertretung', 'bemerkung', 'teamspezifisch', ]

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={
                    'rows': 1,
                    'cols': 40,
                    'style': 'height: 1.4em;'
                })},
    }


class GesamtInline(admin.TabularInline):
    model = TblGesamt
    extra = 0


class UserIDundNameInline(admin.TabularInline):
    model = TblUserIDundName
    extra = 1


class RollehatafInline(admin.TabularInline):
    model = TblRollehataf
    extra = 1
    fields = ['af', 'bemerkung', 'mussfeld', 'einsatz', ]


class UebersichtAfGfsInline(admin.TabularInline):
    model = TblUebersichtAfGfs
    extra = 1


class AflisteInline(admin.TabularInline):
    model = TblAfliste
    extra = 1


class RollenInline(admin.TabularInline):
    model = TblRollen
    extra = 1


# ######################################################################################################
# tbl Gesamt
# ######################################################################################################
@admin.register(TblGesamt)
class GesamtAdmin(ImportExportModelAdmin):
    actions_on_top = False  # Keine Actions, weil diese Tabelle nie manuell geändert wird
    actions_on_bottom = False

    list_select_related = ('modell', 'userid_name', 'plattform',)

    # Diese Fieldsets greifen bei Detailsichten zu Änderungen und Neuanlagen von Einträgen.
    # Braucht so eigentlich niemand...
    fieldsets = [
        ('Standard-Informationen', {'fields': ['userid_name', 'tf',
                                               'tf_beschreibung',
                                               'enthalten_in_af',
                                               'af_beschreibung',
                                               'plattform', 'gf',
                                               'af_gueltig_bis',
                                               'modell', 'direct_connect',
                                               'af_zuweisungsdatum', 'datum', 'geloescht', ]}),
        ('Detail-Informationen  ', {'fields': ['tf_kritikalitaet',
                                               'tf_eigentuemer_org',
                                               'af_gueltig_ab',
                                               'hoechste_kritikalitaet_tf_in_af',
                                               'gf_beschreibung',
                                               'gefunden', 'wiedergefunden', 'geaendert',
                                               'neueaf', 'nicht_ai',
                                               'patchdatum',
                                               'wertmodellvorpatch',
                                               'loeschdatum', ],
                                    'classes': ['collapse']}),
    ]
    list_display = ('id', 'userid_name', 'tf', 'tf_beschreibung',
                    'enthalten_in_af', 'gf',
                    'plattform', 'get_direct_connect', 'get_active',
                    )
    list_filter = ('geloescht', 'direct_connect',
                   'userid_name__gruppe', 'plattform',)
    list_display_links = ('id',)
    list_editable = ('tf', 'tf_beschreibung', 'enthalten_in_af',
                     'plattform', 'gf',)
    search_fields = ['id', 'userid_name__name', 'tf',
                     'tf_beschreibung', 'af_beschreibung'
                     ]

    list_per_page = 25

    # Parameter für import/export
    resource_class = GesamtExporterModel
    sortable_by = ['userid_name']


# ######################################################################################################
# tbl UserIDundName
# ######################################################################################################
@admin.register(TblUserIDundName)
class UserIDundNameAdmin(admin.ModelAdmin):
    list_select_related = ('orga',)

    fieldsets = [
        ('User-Informationen', {'fields': ['userid', 'name', 'orga', 'geloescht']}),
        ('Orga-Details      ', {'fields': ['zi_organisation', 'abteilung', 'gruppe'],
                                'classes': ["""'collapse'"""]}),
    ]

    list_display = ('id', 'userid', 'colored_name', 'orga', 'zi_organisation',
                    'get_active', 'abteilung', 'gruppe',
                    'npu_rolle', 'npu_grund',
                    'iiq_organisation',
                    )
    list_display_links = ('userid', 'colored_name', 'get_active',)
    list_editable = ('orga', 'zi_organisation', 'abteilung', 'gruppe',)
    search_fields = ['name', 'zi_organisation', 'abteilung', 'gruppe', 'userid',
                     'npu_rolle', 'npu_grund', 'iiq_organisation',
                     ]

    list_filter = ('geloescht', 'abteilung', 'orga', 'gruppe',)

    actions_on_top = True
    actions_on_bottom = True

    inlines = [UserhatrolleInline]
    # Nette Idee, grottig lahm
    # inlines += [GesamtInline]

    list_per_page = 20
    # inlines = [UserhatrolleInline]


# ######################################################################################################
# tbl Orga
# ######################################################################################################
@admin.register(TblOrga)
class Orga(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True
    list_display = ('team', 'teamliste', 'freies_team', 'themeneigentuemer',)
    list_filter = ('themeneigentuemer',)
    list_display_links = ('team',)
    list_editable = ('themeneigentuemer',)
    search_fields = ['team', 'teamliste', 'freies_team', ]

    inlines = [UserIDundNameInline]


# ######################################################################################################
# tbl Plattform
# ######################################################################################################
@admin.register(TblPlattform)
class Plattform(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True
    list_display = ('id', 'tf_technische_plattform',)
    # list_filter = ('tf_technische_plattform',)
    # list_display_links = ('tf_technische_plattform')
    list_editable = ('tf_technische_plattform',)
    search_fields = ['tf_technische_plattform', ]
    # Nette Idee, grottig lahm
    # inlines = [GesamtInline]


# ######################################################################################################
# tbl UebersichtAfGfs
# ######################################################################################################
@admin.register(TblUebersichtAfGfs)
class UebersichtAfGfs(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True

    fieldsets = [
        ('Standard       ', {'fields': ['name_af_neu', 'name_gf_neu', 'af_text', 'gf_text',
                                        'geloescht', 'af_langtext', 'modelliert', 'zielperson', ]}),
        ('Rechte-Details ', {'fields': ['kommentar', 'af_ausschlussgruppen', 'af_einschlussgruppen',
                                        'af_sonstige_vergabehinweise', 'kannweg', ],
                             'classes': ['collapse']}),
    ]

    list_display = ('id', 'name_af_neu', 'name_gf_neu', 'af_text', 'gf_text',
                    'geloescht', 'af_langtext', 'modelliert', 'zielperson',
                    'kommentar', 'af_ausschlussgruppen', 'af_einschlussgruppen',
                    'af_sonstige_vergabehinweise', 'kannweg',)

    list_filter = ('geloescht', 'modelliert', 'zielperson',)

    list_display_links = ()

    list_editable = ('name_af_neu', 'name_gf_neu', 'af_text', 'gf_text', 'af_langtext',
                     'zielperson', 'kommentar',
                     'af_ausschlussgruppen', 'af_einschlussgruppen', 'af_sonstige_vergabehinweise',)

    search_fields = ['name_af_neu', 'name_gf_neu', 'af_text', 'gf_text', 'af_langtext', ]


# ######################################################################################################
# tbl GesamtHistorie
# ######################################################################################################
@admin.register(TblGesamtHistorie)
class TblGesamtHistorie(admin.ModelAdmin):
    actions_on_top = False
    actions_on_bottom = False

    list_display = ('id', 'id_alt', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'gf',
                    'modell', 'tf_kritikalitaet', 'tf_eigentuemer_org', 'plattform',
                    'datum', 'geloescht', 'gefunden', 'wiedergefunden', 'geaendert', 'neueaf',
                    'loeschdatum',)

    search_fields = ['id_alt__id', 'userid_name__name',
                     'tf', 'tf_beschreibung', 'enthalten_in_af', ]


# ######################################################################################################
# tbl Userhatrolle
# ######################################################################################################
@admin.register(TblUserhatrolle)
class UserhatrolleAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True
    actions_selection_counter = True
    list_select_related = True

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={
                    'rows': 1,
                    'cols': 40,
                    'style': 'height: 1.4em;'
                })},
    }

    list_display = ('userundrollenid', 'userid', 'teamspezifisch', 'rollenname',
                    'schwerpunkt_vertretung', 'get_rollenbeschreibung',
                    'bemerkung', 'letzte_aenderung',)
    # list_filter = ('schwerpunkt_vertretung', 'rollenname',)
    list_display_links = ('userundrollenid', 'rollenname',)
    list_editable = ('schwerpunkt_vertretung', 'bemerkung', 'teamspezifisch',)
    search_fields = ['schwerpunkt_vertretung', 'rollenname__rollenname',
                     'bemerkung', 'userid__name', 'userid__userid', ]

    list_per_page = 25
    extra = 1


# ######################################################################################################
# tbl Rollen
# ######################################################################################################
@admin.register(TblRollen)
class RollenAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={
                    'rows': 1,
                    'cols': 50,
                    'style': 'height: 1.4em;'
                })},
    }

    list_display = ('rollenname', 'system', 'rollenbeschreibung', 'datum',)
    list_filter = ('system',)
    list_display_links = ('rollenname',)
    list_editable = ('system', 'rollenbeschreibung', 'rollenbeschreibung',)
    search_fields = ['rollenname', 'system', 'rollenbeschreibung', ]

    inlines = [RollehatafInline, UserhatrolleInline, ]
    extra = 1

    """
    def get_formsets_with_inlines(self, request, obj=None):
        print("get_formsets_with_inlines called with {}, {}", self, request)
        for inline in self.get_inline_instances(request, obj):
            inline.cached_userids = [(i.pk, str(i)) for i in TblUserIDundName.objects.all()]
            inline.cached_rollennames = [(i.pk, str(i)) for i in TblRollen.objects.all()]
            inline.cached_cached_afs = [(i.pk, str(i)) for i in TblAfliste.objects.all()]
            yield inline.get_formset(request, obj), inline
        print("leaving get_formsets_with_inlines")
    """


# ######################################################################################################
# tbl AFListe
# ######################################################################################################
@admin.register(TblAfliste)
class Afliste(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True

    list_display = ('id', 'af_name', 'neu_ab',)
    # list_display_links = ( 'id', )
    list_editable = ('af_name',)
    search_fields = ['af_name', ]
    # list_filter = ( )

    inlines = [RollehatafInline]


# ######################################################################################################
# tbl RolleHatAF
# ######################################################################################################
# ToDo: Suche AF in Rollen mit Anzeige zugehöriger User
# ToDo: - Suche ist schon erweitert: Anzeige betroffener User integrieren (besser in neuer Abfrage?)
@admin.register(TblRollehataf)
class RollehatafAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True

    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={
                    'rows': 1,
                    'cols': 40,
                    'style': 'height: 1.4em;'
                })},
    }

    list_display = ('rollenmappingid', 'rollenname', 'af', 'get_muss', 'einsatz', 'bemerkung',)
    list_display_links = ('rollenname',)
    list_editable = ('af', 'bemerkung',)
    search_fields = ['rollenname__rollenname', 'af__af_name', 'bemerkung', ]
    list_filter = ('mussfeld', 'einsatz',)

    list_per_page = 10


# ######################################################################################################
# Eine Reihe von Hilfstabellen, alle nach dem selben Schema. Keine Foreign Keys
# ######################################################################################################
@admin.register(Tblsubsysteme)
class Subsysteme(admin.ModelAdmin):
    alle = ['sgss', 'definition', 'verantwortlicher', 'fk', ]
    search_fields = alle
    list_display = alle


@admin.register(Tblsachgebiete)
class Sachgebiete(admin.ModelAdmin):
    alle = ['sachgebiet', 'definition', 'verantwortlicher', 'fk', ]
    search_fields = alle
    list_display = alle


@admin.register(TblDb2)
class Db2(admin.ModelAdmin):
    list_display = ['id', 'source', 'grantee', 'creator', 'table',
                    'selectauth', 'insertauth', 'updateauth', 'deleteauth',
                    'alterauth', 'indexauth',
                    'grantor', 'grantedts', 'datum',
                    ]
    search_fields = ['table', 'grantee', 'grantor']
    list_filter = ('source', 'datum')


# Wahrscheinlich kann die DB mal entsorgt werden.
# Sie war ursprünglich entwickelt worden, um die Frage der SE zu beantworten,
# welche Rechte in Produktion Schreibrechte sind.
"""
# ToDo Tabelle RacfGruppen entsorgen, wenn sie bis Jahresmitte 2019 nicht mehr benötigt wurde
#@admin.register(TblRacfGruppen)
class RacfGruppen(admin.ModelAdmin):
    alle = ['group', 'test', 'get_produktion', 'get_readonly', 'get_db2_only', 'stempel', ]
    search_fields = alle
    list_display = alle
"""


@admin.register(RACF_Rechte)
class RACF_Rechte(admin.ModelAdmin):
    alle = ['id', 'type', 'group', 'ressource_class', 'profil', 'access',
            'test', 'produktion', 'alter_control_update', 'datum', ]
    search_fields = alle
    list_display = alle


@admin.register(Orga_details)
class Orga_details(admin.ModelAdmin):
    alle = ['id', 'abteilungsnummer', 'organisation', 'orgaBezeichnung',
            'fk', 'kostenstelle', 'orgID', 'parentOrga', 'parentOrgID',
            'orgaTyp', 'fkName', 'delegationEigentuemer', 'delegationFK',
            'datum', ]
    search_fields = alle
    list_display = alle


@admin.register(Modellierung)
class Modellierung(ImportExportModelAdmin):
    alle = [
        'entitlement', 'neue_beschreibung', 'plattform', 'gf',
        'beschreibung_der_gf', 'af', 'beschreibung_der_af',
        'organisation_der_af', 'eigentuemer_der_af',
        'aus_modellierung_entfernen', 'datei', 'letzte_aenderung'
    ]
    search_fields = alle
    list_display = alle
    list_editable = ()  # Read Only Tabelle

    # Parameter für import/export
    resource_class = ModellierungExporterModel
    sortable_by = ['entitlement', 'plattform', 'gf', 'af']


@admin.register(Direktverbindungen)
class Direktverbindungen(ImportExportModelAdmin):
    alle = [
        'organisation', 'entscheidung', 'entitlement', 'applikation',
        'instanz', 'identitaet', 'manager', 'vorname', 'nachname', 'account_name',
        'status', 'typ', 'nicht_anmailen', 'ansprechpartner', 'letzte_aenderung'
    ]
    search_fields = alle
    list_display = alle
    list_editable = ('entscheidung', 'nicht_anmailen', 'ansprechpartner')

    # Parameter für import/export
    resource_class = DirektverbindungenExporterModel
    sortable_by = ['entitlement', 'plattform', 'gf', 'af']


@admin.register(Manuelle_Berechtigung)
class Manuelle_BerechtigungAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }


@admin.register(ACLGruppen)
class ACLGruppen(admin.ModelAdmin):
    alle = ['tf', 'zugriff', 'server', 'pfad', 'letzte_aenderung', ]
    search_fields = ['tf', 'zugriff', 'server', 'pfad', ]
    list_display = alle
