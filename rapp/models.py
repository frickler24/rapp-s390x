# -*- coding: utf-8 -*-
# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify,
#     and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models
from django.utils.html import format_html
# Used to generate URLs by reversing the URL patterns
from django.urls import reverse
from django.utils import timezone
from django.db import connection
from mdeditor.fields import MDTextField


# Die drei Rollentabellen sowie die AF-Liste hängen inhaltlich zusammen
# Die Definition der Rollen
class TblRollen(models.Model):
    rollenname = models.CharField(db_column='rollenname', primary_key=True,
                                  max_length=100, verbose_name='Rollen-Name')
    system = models.CharField(db_column='system', max_length=150,
                              verbose_name='System', db_index=True)
    rollenbeschreibung = models.CharField(db_column='rollenbeschreibung',
                                          max_length=190, blank=True, null=True, db_index=True)
    datum = models.DateTimeField(
        db_column='datum', default=timezone.now, blank=True)

    class Meta:
        managed = True
        db_table = 'tbl_Rollen'
        verbose_name = "Rollenliste"
        verbose_name_plural = "03_Rollen-Übersicht (tbl_Rollen)"
        ordering = ['rollenname', ]
        unique_together = (
            ('rollenname', 'system', 'rollenbeschreibung', 'datum'),)

    def __str__(self) -> str:
        return str(self.rollenname)


# Meta-Tabelle, welche Arbeitsplatzfunktion in welcher Rolle enthalten ist (n:m Beziehung)
#
# Die drei ursprünglichen Einzelfelder nurXV, XABCV und DV wurden zusammengefast zu einer Col
#     einsatz = 8:    Nur gültig für AV, BV, CV-User (z.B. Zweituser-Recht)
#    einsatz = 4:    Nur gültig für XV-Userid
#    einsatz = 2:     Gültig für alles außer DV-User
#    einsatz = 1:    Nur gültig für DV-User
class TblRollehataf(models.Model):
    EINSATZ_NONE = 0
    EINSATZ_NURDV = 1
    EINSATZ_XABCV = 2
    EINSATZ_NURXV = 4
    EINSATZ_ABCV = 8
    EINSATZ_CHOICES = (
        (EINSATZ_NONE, 'nicht zugewiesen'),
        (EINSATZ_NURDV, 'Nur DV-User'),
        (EINSATZ_XABCV, 'XV, AV, BV, CV'),
        (EINSATZ_NURXV, 'nur XV-User'),
        (EINSATZ_ABCV, 'AV, BV, CV'),
    )

    rollenmappingid = models.AutoField(db_column='rollenmappingid',
                                       primary_key=True, verbose_name='ID')
    rollenname = models.ForeignKey('TblRollen', models.CASCADE,
                                   to_field='rollenname', db_column='rollenname')
    af = models.ForeignKey('TblAfliste', models.CASCADE, to_field='id', db_column='af',
                           blank=True, null=True, verbose_name='AF')
    mussfeld = models.IntegerField(
        db_column='mussfeld', blank=True, null=True, verbose_name='Muss')
    bemerkung = models.CharField(
        db_column='bemerkung', max_length=250, blank=True, null=True)
    einsatz = models.IntegerField(db_column='einsatz',
                                  choices=EINSATZ_CHOICES, default=EINSATZ_NONE)

    class Meta:
        managed = True
        db_table = 'tbl_RolleHatAF'
        # unique_together = (('rollenname', 'af'),)
        verbose_name = "Rolle und ihre Arbeitsplatzfunktionen"
        verbose_name_plural = "02_Rollen und ihre Arbeitsplatzfunktionen (tbl_RolleHatAF)"
        ordering = ['rollenname__rollenname', 'af__af_name', ]

    def __str__(self) -> str:
        return str(self.rollenname)

    def get_muss(self):
        return self.mussfeld

    get_muss.boolean = True
    get_muss.admin_order_field = 'mussfeld'
    get_muss.short_description = 'Muss'
    mussfeld.boolean = True


# Referenz der User auf die ihnen zur Verfügung stehenden Rollen
class TblUserhatrolle(models.Model):
    SCHWERPUNKT_TYPE = (
        ('Schwerpunkt', 'Schwerpunktaufgabe'),
        ('Vertretung', 'Vertretungstätigkeiten, Zweitsysteme'),
        ('Allgemein', 'Rollen, die nicht Systemen zugeordnet sind'),
    )

    userundrollenid = models.AutoField(db_column='userundrollenid',
                                       primary_key=True, verbose_name='ID')
    userid = models.ForeignKey('Tbluseridundname', models.CASCADE, to_field='userid',
                               db_column='userid', verbose_name='UserID, Name')
    rollenname = models.ForeignKey(
        'TblRollen', models.CASCADE, db_column='rollenname')
    schwerpunkt_vertretung = \
        models.CharField(db_column='schwerpunkt_vertretung',
                         max_length=100, blank=True, null=True,
                         choices=SCHWERPUNKT_TYPE
                         )
    bemerkung = models.TextField(db_column='bemerkung', blank=True, null=True)
    teamspezifisch = models.ForeignKey('TblOrga', models.CASCADE, db_column='id',
                                       blank=True, null=True, default=None)
    letzte_aenderung = models.DateTimeField(db_column='letzte_aenderung',
                                            default=timezone.now, blank=True, db_index=True)

    class Meta:
        managed = True
        db_table = 'tbl_UserHatRolle'
        verbose_name = "User und Ihre Rollen"
        verbose_name_plural = "01_User und Ihre Rollen (tbl_UserHatRolle)"
        ordering = ['userid__name', '-userid__userid',
                    'schwerpunkt_vertretung', 'rollenname', ]
        unique_together = (('userid', 'rollenname'),)

    def __str__(self) -> str:
        return str(self.userundrollenid)

    def get_rollenbeschreibung(self):
        return str(self.rollenname.rollenbeschreibung)

    get_rollenbeschreibung.short_description = 'Rollenbeschreibung'

    def get_absolute_url(self):
        # Returns the url for the whole list.
        return reverse('user_rolle_af', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-update', args=[str(self.userundrollenid)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model
        # (no ID given, the element does not exist yet).
        return reverse('user_rolle_af-create', args=[])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-delete', args=[str(self.userundrollenid)])


# Tabelle enthält die aktuell genehmigten (modellierten und in Modellierung befindlichen)
# AF + GF-Kombinationen
class TblUebersichtAfGfs(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    name_gf_neu = models.CharField(
        db_column='name_gf_neu', max_length=50, verbose_name='GF Neu')
    name_af_neu = models.CharField(db_column='name_af_neu', max_length=50,
                                   verbose_name='AF Neu', db_index=True)
    kommentar = models.CharField(
        db_column='kommentar', max_length=150, blank=True, null=True)
    zielperson = models.CharField(db_column='zielperson', max_length=50, )
    af_text = models.CharField(
        db_column='af_text', max_length=150, blank=True, null=True)
    gf_text = models.CharField(
        db_column='gf_text', max_length=150, blank=True, null=True)
    af_langtext = models.CharField(
        db_column='af_langtext', max_length=250, blank=True, null=True)
    af_ausschlussgruppen = models.CharField(db_column='af_ausschlussgruppen',
                                            max_length=250, blank=True, null=True)
    af_einschlussgruppen = models.CharField(db_column='af_einschlussgruppen',
                                            max_length=250, blank=True, null=True)
    af_sonstige_vergabehinweise = models.CharField(db_column='af_sonstige_vergabehinweise',
                                                   max_length=250, blank=True, null=True)
    geloescht = models.IntegerField(
        db_column='geloescht', blank=True, null=True)
    kannweg = models.IntegerField(blank=True, null=True)
    modelliert = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblUEbersichtAF_GFs'
        unique_together = (('name_gf_neu', 'name_af_neu'),)
        verbose_name = "Erlaubte AF/GF-Kombination"
        verbose_name_plural = "04_Erlaubte AF/GF-Kombinationen-Übersicht (tblUebersichtAF_GFs)"
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name_gf_neu + ' | ' + self.name_af_neu

    geloescht.boolean = True
    kannweg.boolean = True


# Die Tabelle enthält die Teambeschreibungen. Das eigentliche Team ist das Feld "team"
class TblOrga(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    team = models.CharField(db_column='team', max_length=64,
                            blank=False, null=False, db_index=True)
    themeneigentuemer = models.CharField(db_column='themeneigentuemer',
                                         max_length=64, blank=False, null=False)
    teamliste = models.TextField(max_length=400, blank=True,
                                 null=True, default=None)  # Listen von Teams
    freies_team = models.TextField(max_length=4000, blank=True,
                                   null=True, default=None)  # Usernamen + Spezifika

    class Meta:
        managed = True
        db_table = 'tblOrga'
        verbose_name = "Orga-Information"
        verbose_name_plural = "06_Team-Übersicht (tblOrga)"
        ordering = ['team']
        unique_together = (('id', 'team', 'themeneigentuemer'),)

    def __str__(self) -> str:
        return self.team

    def get_absolute_url(self):
        # Returns the url for the item.
        return reverse('teamliste', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('team-update', args=[str(self.id)])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('team-delete', args=[str(self.id)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model (no ID given,
        # the element does not exist yet).
        return reverse('team-create', args=[])


# Die Namen aller aktiven und gelöschten UserIDen und der dazugehörenden Namen
# (Realnamen und Technische User)
class TblUserIDundName(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    userid = models.CharField(db_column='userid', max_length=32, unique=True)
    name = models.CharField(db_column='name', max_length=191, db_index=True)
    orga = models.ForeignKey('TblOrga', db_column='orga_id', on_delete=models.DO_NOTHING,
                             verbose_name='Team', db_index=True)
    zi_organisation = models.CharField(db_column='zi_organisation', max_length=64,
                                       verbose_name='ZI-Organisation', db_index=True)
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True,
                                    verbose_name='gelöscht')
    abteilung = models.CharField(
        db_column='abteilung', max_length=64, db_index=True, )
    gruppe = models.CharField(db_column='gruppe', max_length=50, db_index=True)
    npu_rolle = models.CharField(max_length=20, blank=True, null=True)
    npu_grund = models.CharField(max_length=2000, blank=True, null=True)
    iiq_organisation = models.CharField(
        max_length=64, blank=True, null=True, db_index=True)

    class Meta:
        managed = True
        db_table = 'tblUserIDundName'
        verbose_name = "UserID-Name-Kombination"
        verbose_name_plural = "05_UserID-Name-Übersicht (tblUserIDundName)"
        ordering = ['geloescht', 'name', '-userid']
        unique_together = (('userid', 'name'),
                           ('id', 'userid', 'name', 'orga', 'zi_organisation',
                            'geloescht', 'abteilung', 'gruppe', 'npu_rolle'),
                           )
        index_together = (('gruppe', 'geloescht'),)
        index_together = (('geloescht', 'zi_organisation'),)

    def __str__(self) -> str:
        return str(self.userid + ' | ' + self.name)

    def get_active(self):
        return not self.geloescht

    get_active.boolean = True
    get_active.admin_order_field = 'geloescht'
    get_active.short_description = 'aktiv'

    geloescht.boolean = True

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            '21610B' if (self.get_active()) else "B40404",
            self.name,
        )

    colored_name.admin_order_field = 'name'
    colored_name.short_description = 'Name, Vorname'

    def get_absolute_url(self):
        # Returns the url for the whole list.
        return reverse('userliste', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        # return reverse('user-detail', args=[str(self.id)])
        return reverse('user-update', args=[str(self.id)])

    def get_absolute_toggle_geloescht_url(self):
        # Returns the url to access a particular instance of the model.
        # return reverse('user-detail', args=[str(self.id)])
        return reverse('user-toggle-geloescht', args=[str(self.id)])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        # return reverse('user-detail', args=[str(self.id)])
        return reverse('user-delete', args=[str(self.id)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model
        # (no ID given, the element does not exist yet).
        return reverse('user-create', args=[])


# Diese Funktion gehört inhaltlich zu tblUserIDundName, aber nicht in die Klasse
# (wird in form.py genutzt)
def hole_organisationen():
    # Liefert eine Liste an Tupeln mit Choices für die Orga-Auswahl zurück.
    # Die Liste stammt aus tblUserIDundName.
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT zi_organisation FROM tblUserIDundName")
        rows = cursor.fetchall()
        return [('Bitte Organisation wählen', 'Bitte Organisation wählen')] \
            + [(r[0], r[0]) for r in rows]


# Die verschiedenen technischne Plattformen (RACF, CICS, Unix, Win, AD, LDAP, test/Prod usw.)
class TblPlattform(models.Model):
    """
    Das heißt heute in IIQ eher "Application" und beschreibt die Umgebung,
    in der sihc das Recht befindet.
    """
    id = models.AutoField(db_column='id', primary_key=True)
    tf_technische_plattform = models.CharField(db_column='tf_technische_plattform', max_length=32,
                                               verbose_name='Plattform', unique=True)
    geloescht = models.IntegerField(
        blank=True, null=True, verbose_name='gelöscht')

    class Meta:
        managed = True
        db_table = 'tblPlattform'
        verbose_name = "Plattform"
        verbose_name_plural = "07_Plattform-Übersicht (tblPlattform)"
        ordering = ['tf_technische_plattform']
        unique_together = (('id', 'tf_technische_plattform', 'geloescht'),)

    def __str__(self) -> str:
        return self.tf_technische_plattform


class TblGesamt(models.Model):
    """
    tblGesamt enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen
    """
    id = models.AutoField(db_column='id', primary_key=True)
    userid_name = models.ForeignKey('TblUserIDundName', db_column='userid_und_name_id',
                                    on_delete=models.CASCADE)
    tf = models.CharField(db_column='tf', max_length=100,
                          verbose_name='TF', db_index=True)
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=500,
                                       blank=True, null=True, verbose_name='TF-Beschreibung')
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100,
                                       blank=True, null=True, verbose_name='AF', db_index=True)
    modell = models.ForeignKey('TblUebersichtafGfs', db_column='modell',
                               on_delete=models.CASCADE, db_index=True)
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64,
                                        blank=True, null=True,
                                        verbose_name='TF-Kritikalität')
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64,
                                          blank=True, null=True,
                                          verbose_name='TF-Eigentümer-orga')
    plattform = models.ForeignKey('TblPlattform', db_column='plattform_id',
                                  on_delete=models.CASCADE,
                                  verbose_name='Plattform', db_index=True)
    gf = models.CharField(db_column='gf', max_length=100,
                          blank=True, null=True, verbose_name='GF')
    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True,
                                         verbose_name='AF gültig ab')
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True,
                                          verbose_name='AF gültig bis')
    direct_connect = models.CharField(db_column='direct_connect', max_length=100,
                                      blank=True, null=True,
                                      verbose_name='Direktverbindung')
    hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='hk_tf_in_af', max_length=4,
                                                       blank=True, null=True,
                                                       verbose_name='max. Krit. TF in AF')
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=250,
                                       blank=True, null=True,
                                       verbose_name='GF Kurzbeschreibung')
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum',
                                              blank=True, null=True,
                                              verbose_name='AF Zuweisung', db_index=True)
    datum = models.DateTimeField(
        db_column='datum', verbose_name='Recht gefunden am')
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True,
                                    verbose_name='gelöscht', db_index=True)
    gefunden = models.IntegerField(blank=True, null=True)
    wiedergefunden = models.DateTimeField(blank=True, null=True)
    geaendert = models.IntegerField(db_column='geaendert', blank=True, null=True,
                                    verbose_name='AF geändert')
    neueaf = models.CharField(
        db_column='neueaf', max_length=50, blank=True, null=True)
    nicht_ai = models.IntegerField(db_column='nicht_ai', blank=True, null=True)
    patchdatum = models.DateTimeField(
        db_column='patchdatum', blank=True, null=True)
    wertmodellvorpatch = models.TextField(
        db_column='wert_modell_vor_patch', blank=True, null=True)
    loeschdatum = models.DateTimeField(
        db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum')
    letzte_aenderung = models.DateTimeField(auto_now=True, db_index=True)
    af_beschreibung = models.TextField(
        max_length=2000, blank=True, null=True, default='Keine Beschreibung vorhanden')

    class Meta:
        managed = True
        db_table = 'tblGesamt'
        verbose_name = "Eintrag der Gesamttabelle (tblGesamt)"
        verbose_name_plural = "08_Gesamttabelle Übersicht (tblGesamt)"
        index_together = (('userid_name', 'tf', 'enthalten_in_af', 'plattform', 'gf'),
                          ('gf', 'enthalten_in_af'),
                          )
        ordering = ['id']  # Ist erforderlich wegen Paginierter Anzeige

    def __str__(self) -> str:
        return str(self.id)

    def get_active(self):
        return not self.geloescht

    get_active.boolean = True
    get_active.admin_order_field = 'geloescht'
    get_active.short_description = 'aktiv'

    def get_gefunden(self):
        return self.gefunden

    get_gefunden.boolean = True

    def get_geaendert(self):
        return self.geaendert

    geaendert.boolean = True

    def get_direct_connect(self):
        return self.direct_connect == 'Ja'

    get_direct_connect.boolean = True
    get_direct_connect.admin_order_field = 'direct_connect'
    get_direct_connect.short_description = 'direkt'

    def get_ai(self):
        return not self.nicht_ai

    get_ai.boolean = True

    def get_absolute_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('gesamt-detail', args=[str(self.id)])


# tblGesamtHistorie enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen,
# wenn der User (mal) gelöscht wurde
class TblGesamtHistorie(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    id_alt = models.IntegerField(
        db_column='id_alt', blank=False, null=False, db_index=True)
    userid_name = models.ForeignKey(
        'TblUserIDundName', models.PROTECT, db_column='userid_und_name_id', to_field='id', )
    tf = models.CharField(db_column='tf', max_length=100, verbose_name='TF')
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=500,
                                       blank=True, null=True,
                                       verbose_name='TF-Beschreibung')
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100,
                                       blank=True, null=True,
                                       verbose_name='AF')
    modell = models.ForeignKey(
        'TblUebersichtafGfs', db_column='modell', on_delete=models.CASCADE)
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64,
                                        blank=True, null=True,
                                        verbose_name='TF-Kritikalität')
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64,
                                          blank=True, null=True,
                                          verbose_name='TF-Eigentümer-orga')
    plattform = models.ForeignKey('TblPlattform', db_column='plattform_id',
                                  on_delete=models.CASCADE,
                                  verbose_name='Plattform')  # Field name made lowercase.
    gf = models.CharField(db_column='gf', max_length=100,
                          blank=True, null=True, verbose_name='GF')
    datum = models.DateTimeField(
        db_column='datum', verbose_name='Recht gefunden am')
    geloescht = models.IntegerField(
        db_column='geloescht', blank=True, null=True, verbose_name='gelöscht')
    gefunden = models.IntegerField(blank=True, null=True)
    wiedergefunden = models.DateTimeField(blank=True, null=True)
    geaendert = models.IntegerField(
        db_column='geaendert', blank=True, null=True, verbose_name='AF geändert')
    neueaf = models.CharField(
        db_column='neueaf', max_length=50, blank=True, null=True, db_index=True)
    loeschdatum = models.DateTimeField(
        db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum')
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True,
                                              verbose_name='AF Zuweisung')
    # ToDo: überlegen, ob af_zuweisungsdatum_alt weg kann oder wozu es genutzt werden soll
    af_zuweisungsdatum_alt = models.DateTimeField(db_column='af_zuweisungsdatum_alt',
                                                  blank=True, null=True,
                                                  verbose_name='AF Zuweisung alt')
    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True,
                                         verbose_name='AF gültig ab')
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True,
                                          verbose_name='AF gültig bis')
    direct_connect = models.CharField(db_column='direct_connect', max_length=100, blank=True,
                                      null=True, verbose_name='Direktverbindung')
    hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='hk_tf_in_af', max_length=4,
                                                       blank=True, null=True,
                                                       verbose_name='max. Krit. TF in AF')
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=300,
                                       blank=True, null=True,
                                       verbose_name='GF Kurzbeschreibung')
    nicht_ai = models.IntegerField(db_column='nicht_ai', blank=True, null=True)
    patchdatum = models.DateTimeField(
        db_column='patchdatum', blank=True, null=True)
    wertmodellvorpatch = models.TextField(
        db_column='wert_modell_vor_patch', blank=True, null=True)
    letzte_aenderung = models.DateTimeField(blank=True, null=True)
    af_beschreibung = models.TextField(
        max_length=2000, blank=True, null=True, default='--')

    class Meta:
        managed = True
        db_table = 'tblGesamtHistorie'
        verbose_name = "Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)"
        verbose_name_plural = "99_Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)"

    def __str__(self) -> str:
        return str(self.id)


# Dies ist nur eine Hilfstabelle, auch wenn sie wichtig ist.
# Sie besteht aus dem `tblÜbersichtAF_GFs`.`Name AF Neu` für alle Felder,
# bei denen `modelliert` nicht null ist.
# (das automatisch ergänzte Datum wird nicht benötigt,
# hier könnte auch das `modelliert`genommen werden)
# Original Query im Access:_
#
# Sinn der Tabelle ist, eine eindeutige Liste an AFs vorliegen zu haben.
class TblAfliste(models.Model):
    id = models.AutoField(db_column='id', verbose_name='ID', primary_key=True)
    af_name = models.CharField(
        db_column='af_name', max_length=150, verbose_name='AF-Name', unique=True)
    neu_ab = models.DateTimeField(db_column='neu_ab')

    class Meta:
        managed = True
        db_table = 'tbl_AFListe'
        verbose_name = "Gültige AF"
        verbose_name_plural = "98_Übersicht gültiger AFen (tbl_AFListe)"
        ordering = ['af_name']
        unique_together = (('id', 'af_name', 'neu_ab'),)

    def __str__(self) -> str:
        return str(self.af_name)


# ##################################### Tblsubsysteme, Tblsachgebiete, TblDb2
# Ein paar Hilfstabellen.
# Die sind inhaltlich wahrscheinlich nicht super aktuell, helfen aber bei verschiedenen Fragen.
class Tblsachgebiete(models.Model):
    sachgebiet = models.CharField(
        db_column='Sachgebiet', primary_key=True, max_length=32)
    definition = models.CharField(
        db_column='Definition', max_length=250, blank=True, null=True)
    verantwortlicher = models.CharField(
        db_column='Verantwortlicher', max_length=150, blank=True, null=True)
    telefon_verantwortlicher = models.CharField(
        db_column='Telefon', max_length=150, blank=True, null=True)
    user_id_verantwortlicher = models.CharField(
        db_column='user_id', max_length=50, blank=True, null=True)
    fk = models.CharField(db_column='Führungskraft',
                          max_length=250, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblSachgebiete'
        verbose_name = "Sachgebiet"
        verbose_name_plural = "97_Übersicht Sachgebiete (tbl_Sachgebiete)"
        ordering = ['sachgebiet']


class Tblsubsysteme(models.Model):
    sgss = models.CharField(db_column='sgss', primary_key=True, max_length=32)
    definition = models.CharField(
        db_column='Definition', max_length=250, blank=True, null=True)
    verantwortlicher = models.CharField(
        db_column='Verantwortlicher', max_length=150, blank=True, null=True)
    telefon_verantwortlicher = models.CharField(
        db_column='Telefon', max_length=150, blank=True, null=True)
    user_id_verantwortlicher = models.CharField(
        db_column='user_id', max_length=50, blank=True, null=True)
    fk = models.CharField(db_column='Führungskraft',
                          max_length=250, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblSubsysteme'
        verbose_name = "Subsystem"
        verbose_name_plural = "96_Übersicht Subsysteme (tbl_Subsysteme)"
        ordering = ['sgss']


class TblDb2(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    source = models.CharField(db_column='source', max_length=8, default='none')
    # grantee = models.ForeignKey('TblRacfGruppen', models.PROTECT,
    #   to_field='group', db_column='grantee')
    grantee = models.CharField(
        db_column='grantee', max_length=15, default='none')
    creator = models.CharField(
        db_column='CREATOR', max_length=15, default='none')
    table = models.CharField(db_column='TABLE', max_length=31, db_index=True)
    selectauth = models.CharField(
        db_column='SELECTAUTH', max_length=3, blank=True, null=True)
    insertauth = models.CharField(
        db_column='INSERTAUTH', max_length=3, blank=True, null=True)
    updateauth = models.CharField(
        db_column='UPDATEAUTH', max_length=3, blank=True, null=True)
    deleteauth = models.CharField(
        db_column='DELETEAUTH', max_length=3, blank=True, null=True)
    alterauth = models.CharField(
        db_column='ALTERAUTH', max_length=3, blank=True, null=True)
    indexauth = models.CharField(
        db_column='INDEXAUTH', max_length=3, blank=True, null=True)
    grantor = models.CharField(db_column='GRANTOR', max_length=15)
    grantedts = models.CharField(db_column='GRANTEDTS', max_length=63)
    datum = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tbl_DB2'
        verbose_name = 'DB2-Berechtigung'
        verbose_name_plural = '30_DB2 - Berechtigungen (Tbl_DB2)'
        ordering = ['id', ]

    def __str__(self) -> str:
        return str(self.id)


class Tblrechteneuvonimport(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    identitaet = models.CharField(
        db_column='Identität', max_length=150, blank=False, null=False, db_index=True)
    nachname = models.CharField(
        db_column='Nachname', max_length=100, blank=True, null=True)
    vorname = models.CharField(
        db_column='Vorname', max_length=100, blank=True, null=True)
    tf_name = models.CharField(
        db_column='TF Name', max_length=100, blank=True, null=True)
    tf_beschreibung = models.CharField(
        db_column='TF Beschreibung', max_length=500, blank=True, null=True)
    af_anzeigename = models.CharField(
        db_column='AF Anzeigename', max_length=100, blank=True, null=True)
    af_beschreibung = models.CharField(
        db_column='AF Beschreibung', max_length=2000, blank=True, null=True)
    hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='Höchste Kritikalität TF in AF',
                                                       max_length=150, blank=True, null=True)
    tf_eigentuemer_org = models.CharField(
        db_column='TF Eigentümer Org', max_length=150, blank=True, null=True)
    tf_applikation = models.CharField(
        db_column='TF Applikation', max_length=150, blank=True, null=True)
    tf_kritikalitaet = models.CharField(
        db_column='TF Kritikalität', max_length=150, blank=True, null=True)
    gf_name = models.CharField(
        db_column='GF Name', max_length=150, blank=True, null=True)
    gf_beschreibung = models.CharField(
        db_column='GF Beschreibung', max_length=250, blank=True, null=True)
    direct_connect = models.CharField(
        db_column='Direct Connect', max_length=150, blank=True, null=True)
    af_zugewiesen_an_account_name = models.CharField(db_column='AF zugewiesen an Account-Name',
                                                     max_length=150, blank=True, null=True)
    af_gueltig_ab = models.DateTimeField(
        db_column='AF Gültig ab', blank=True, null=True)
    af_gueltig_bis = models.DateTimeField(
        db_column='AF Gültig bis', blank=True, null=True)
    af_zuweisungsdatum = models.DateTimeField(
        db_column='AF Zuweisungsdatum', blank=True, null=True)
    npu_rolle = models.CharField(max_length=20, blank=True, null=True)
    npu_grund = models.CharField(max_length=2000, blank=True, null=True)
    iiq_organisation = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblRechteNeuVonImport'
        verbose_name = 'Importiere neue Daten (tblRechteNeuVonImport)'
        verbose_name_plural = 'Importiere neue Daten (tblRechteNeuVonImport)'
        ordering = ['id', ]


class Tblrechteamneu(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    userid = models.CharField(
        db_column='userid', max_length=50, blank=True, null=True)
    name = models.CharField(
        db_column='name', max_length=100, blank=True, null=True)
    tf = models.CharField(db_column='tf', max_length=100,
                          blank=True, null=True, db_index=True)
    tf_beschreibung = models.CharField(
        db_column='tf_beschreibung', max_length=500, blank=True, null=True)
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100,
                                       blank=True, null=True,
                                       db_index=True)
    tf_kritikalitaet = models.CharField(
        db_column='tf_kritikalitaet', max_length=64, blank=True, null=True)
    tf_eigentuemer_org = models.CharField(
        db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True)
    tf_technische_plattform = models.CharField(db_column='tf_technische_plattform', max_length=64,
                                               blank=True, null=True, db_index=True)
    gf = models.CharField(db_column='gf', max_length=100,
                          blank=True, null=True, db_index=True)
    af_gueltig_ab = models.DateTimeField(
        db_column='af_gueltig_ab', blank=True, null=True)
    af_gueltig_bis = models.DateTimeField(
        db_column='af_gueltig_bis', blank=True, null=True)
    direct_connect = models.CharField(
        db_column='direct_connect', max_length=50, blank=True, null=True)
    hoechste_kritikalitaet_tf_in_af = models.CharField(
        db_column='hk_tf_in_af', max_length=150, blank=True, null=True)
    gf_beschreibung = models.CharField(
        db_column='gf_beschreibung', max_length=250, blank=True, null=True)
    af_zuweisungsdatum = models.DateTimeField(
        db_column='af_zuweisungsdatum', blank=True, null=True)
    gefunden = models.IntegerField(db_column='gefunden', blank=True, null=True)
    geaendert = models.IntegerField(
        db_column='geaendert', blank=True, null=True)
    angehaengt_bekannt = models.IntegerField(
        db_column='angehaengt_bekannt', blank=True, null=True)
    angehaengt_sonst = models.IntegerField(
        db_column='angehaengt_sonst', blank=True, null=True)
    doppelerkennung = models.IntegerField(blank=True, null=True)
    af_beschreibung = models.TextField(
        max_length=2000, blank=True, null=True, default='')
    npu_rolle = models.CharField(max_length=20, blank=True, null=True)
    npu_grund = models.CharField(max_length=2000, blank=True, null=True)
    iiq_organisation = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblRechteAMNeu'
        unique_together = (('userid', 'tf', 'enthalten_in_af',
                           'tf_technische_plattform', 'gf'),)


class RACF_Rechte(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    type = models.CharField(max_length=4, null=True)
    group = models.CharField(max_length=10)
    ressource_class = models.CharField(
        max_length=16, db_column='class', null=True)
    profil = models.CharField(max_length=128, db_index=True, null=True)
    access = models.CharField(max_length=16, null=True)
    test = models.IntegerField()
    produktion = models.IntegerField()
    alter_control_update = models.IntegerField()
    datum = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'RACF-Rechte'
        verbose_name_plural = '40_RACF - Berechtigungen'
        ordering = ['group', 'profil', ]
        # Zum schnelleren Update bei Neulieferung
        index_together = (('group', 'profil'),)

    def __str__(self) -> str:
        return str(self.id)


class Orga_details(models.Model):
    id = models.AutoField(primary_key=True)
    abteilungsnummer = models.CharField(max_length=32, null=True)
    organisation = models.CharField(max_length=100)
    orgaBezeichnung = models.CharField(max_length=100, null=True)
    fk = models.CharField(max_length=32, null=True)
    kostenstelle = models.CharField(max_length=32, null=True)
    orgID = models.IntegerField(null=True)
    parentOrga = models.CharField(max_length=32, null=True)
    parentOrgID = models.IntegerField(null=True)
    orgaTyp = models.CharField(max_length=32, null=True)
    fkName = models.CharField(max_length=32, null=True)
    delegationEigentuemer = models.CharField(max_length=32, null=True)
    delegationFK = models.CharField(max_length=32, null=True)
    datum = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Orga-Details'
        verbose_name_plural = '50_Orga - Details'
        ordering = ['organisation', 'orgID', 'parentOrga', 'fkName', ]

    def __str__(self) -> str:
        return str(self.id)


# Versionshistorie der Daten-Importe; Darüber ist auch ein aktuell laufender Import feststellbar
# Die beiden Felder max und aktuell dienen dem Anzeigen eins Fortschrittbalkens
class Letzter_import(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.DateTimeField(null=False)
    user = models.CharField(max_length=100, null=True)
    end = models.DateTimeField(null=True)
    max = models.IntegerField(null=False)
    aktuell = models.IntegerField(null=False)
    schritt = models.IntegerField(null=False, default=1)
    zi_orga = models.CharField(max_length=64, null=True)

    class Meta:
        managed = True
        verbose_name = 'Letzter Import'
        verbose_name_plural = 'Letzte Importe'
        ordering = ['id', ]


class Modellierung(models.Model):
    """
    Tabelle aus dem Export für die TF-Rezertifizierung.
    Die Daten enthalten alle aktuellen Modellierungen einer TF in die GFs und AFs

    Das kann dem späteren Erzeugen von Mails dienen, um User auf Möglichekiten hinzuweisen,
    sich von Direct Connects zu trennen.
    """
    id = models.AutoField(primary_key=True)
    entitlement = models.CharField(max_length=50, null=True, db_index=True)
    neue_beschreibung = models.CharField(max_length=500, null=True)
    plattform = models.CharField(max_length=30, null=True, db_index=True)
    gf = models.CharField(max_length=50, null=False, db_index=True)
    beschreibung_der_gf = models.CharField(max_length=500, null=True)
    af = models.CharField(max_length=50, null=False, db_index=True)
    beschreibung_der_af = models.CharField(max_length=500, null=True)
    organisation_der_af = models.CharField(max_length=100, null=True)
    eigentuemer_der_af = models.CharField(max_length=100, null=True)
    aus_modellierung_entfernen = models.CharField(max_length=100, null=True)
    datei = models.CharField(max_length=100, null=True)
    letzte_aenderung = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Modellierung AF GF TF'
        verbose_name_plural = '60_Modellierung AF GF TF'


class Direktverbindungen(models.Model):
    """
    Tabelle aus dem Export für die TF-Rezertifizierung.
    Die Daten enthalten alle derzeit bekannten Direktverbindungen zu TFs der Abteilung.

    Auch das kann dem späteren Erzeugen von Mails dienen, um User auf Möglichekiten hinzuweisen,
    sich von Direct Connects zu trennen.
    Diese Tabelle muss geeignet mit der Tabelle Modellierung verknüpft werden
    """
    id = models.AutoField(primary_key=True)
    organisation = models.CharField(max_length=30, null=False)
    entscheidung = models.CharField(max_length=30, null=True)
    entitlement = models.CharField(max_length=100, null=False, db_index=True)
    applikation = models.CharField(max_length=20, null=True)
    instanz = models.CharField(max_length=20, null=True)
    identitaet = models.CharField(max_length=50, null=False, db_index=True)
    manager = models.CharField(max_length=100, null=True)
    vorname = models.CharField(max_length=100, null=False)
    nachname = models.CharField(max_length=100, null=False)
    account_name = models.CharField(max_length=50, null=False)
    status = models.CharField(max_length=100, null=True)
    typ = models.CharField(max_length=100, null=True)
    nicht_anmailen = models.CharField(max_length=8, null=True)
    ansprechpartner = models.CharField(max_length=100, null=True)
    letzte_aenderung = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Direktverbindungen'
        verbose_name_plural = '61_Direktverbindungen'
        unique_together = (('entitlement', 'account_name'),)


class Manuelle_Berechtigung(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False, unique=True, )
    verbundene_af = models.ForeignKey(
        'TblAfliste', models.PROTECT, null=True, )
    ersteller = models.CharField(max_length=50, null=True, )
    letzte_aenderung = models.DateTimeField(default=timezone.now)
    statisch = MDTextField()
    relativ = MDTextField()

    class Meta:
        managed = True
        verbose_name = "Manuell nachzuhaltenede Berechtigung"
        verbose_name_plural = "10_Manuell nachzuhaltenede Berechtigungen"
        ordering = ['name']

    def __str__(self) -> str:
        return str(self.id) \
            + ' ' \
            + str(self.name) \
            + ' (erstellt von {} am {})'.format(self.ersteller, timezone.now())


class ACLGruppen(models.Model):
    id = models.AutoField(primary_key=True)
    tf = models.CharField(max_length=150, null=False, db_index=True, )
    zugriff = models.CharField(max_length=50, null=False, )
    server = models.CharField(max_length=50, null=False, )
    pfad = models.CharField(max_length=400, null=False, )
    letzte_aenderung = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        verbose_name = "ACL-Gruppen"
        verbose_name_plural = "95_ACL-Gruppen"
        ordering = ['tf']


class Setze_NPU_namen_status(models.Model):
    """
    Die Tabelle hält das Ergbnis der einzelnen Schritte beim Setzen der NPU-Rollen
    """
    id = models.AutoField(primary_key=True)
    anzeige = models.CharField(max_length=200, null=True, db_index=False, )
    wert = models.IntegerField(null=True, db_index=False,)
    stamp = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True


class Muss_Kann_Liste(models.Model):
    """
    Die Tabelle hält das Ergbnis der Muss-/Kann-Auswertung zu den Rollen
    """
    rollenname = models.CharField(max_length=100, null=False, db_index=False, )
    af_name = models.CharField(max_length=150, null=False, db_index=False, )
    enthalten_in_af = models.CharField(
        max_length=150, null=True, db_index=False, )
    wcUserid = models.CharField(max_length=32, null=False, db_index=False, )
    userid = models.CharField(max_length=32, null=True, db_index=False, )
    name = models.CharField(max_length=191, null=True, db_index=False, )
    mussfeld = models.IntegerField(null=True, db_index=False,)
    name_vn = models.CharField(max_length=191, null=True, db_index=False, )
    userundrollenid = models.IntegerField(null=False, db_index=False,)
    rollenmappingid = models.IntegerField(null=False, primary_key=True,)

    class Meta:
        db_table = 'lookformust_erg'
        managed = False     # Die Tabelle wird regelmäßig gelöscht und neu angelegt
