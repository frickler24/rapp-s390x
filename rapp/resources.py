"""
Einige Ressourcen für das Handling von csv and Excel sheets
Über diese Klassen in dem Modul werden die Inhalte bestimmt,
die in den jkeweiligen Funktionen exportiert werden sollen.
"""

from import_export import resources

from .models import TblGesamt, Modellierung, Direktverbindungen


class GesamtExporterModel(resources.ModelResource):
    """
        Resource-Class für export der Gesamttabelle (nach Selektion)
    """

    class Meta:
        model = TblGesamt
        encoding = "utf-8"
        delimiter = ";"
        fields = (
            'id', 'userid_name',
            'userid_name__name', 'userid_name__userid',

            'tf', 'tf_beschreibung', 'plattform', 'plattform__tf_technische_plattform',
            'direct_connect', 'enthalten_in_af', 'af_beschreibung', 'gf', 'gf_beschreibung',

            'af_gueltig_ab', 'af_gueltig_bis',
            'af_zuweisungsdatum', 'datum',

            'tf_kritikalitaet', 'tf_eigentuemer_org',
            'hoechste_kritikalitaet_tf_in_af',
            'gefunden', 'wiedergefunden', 'geaendert', 'neueaf', 'nicht_ai',
            'patchdatum', 'wertmodellvorpatch', 'geloescht', 'loeschdatum',

            'modell', 'modell__name_af_neu', 'modell__name_gf_neu',
        )

        export_order = fields


class ModellierungExporterModel(resources.ModelResource):
    """
        Resource-Class für export der Modellierungs-Tabelle
    """

    class Meta:
        model = Modellierung
        encoding = "utf-8"
        delimiter = ';'
        quotechar = '"'
        escapechar = '\\',
        fields = (
            'entitlement', 'neue_beschreibung', 'plattform', 'gf',
            'beschreibung_der_gf', 'af', 'beschreibung_der_af',
            'organisation_der_af', 'eigentuemer_der_af',
            'aus_modellierung_entfernen', 'datei', 'letzte_aenderung',
        )

        export_order = fields


class DirektverbindungenExporterModel(resources.ModelResource):
    """
        Resource-Class für Im- und Eport der Direktverbindungen-Tabelle
    """

    class Meta:
        model = Direktverbindungen
        encoding = "utf-8"
        delimiter = ';'
        quotechar = '"'
        escapechar = '\\',
        fields = ('id',
                  'organisation', 'entscheidung', 'entitlement', 'applikation',
                  'instanz', 'identitaet', 'manager', 'vorname', 'nachname', 'account_name',
                  'status', 'typ', 'nicht_anmailen', 'ansprechpartner'
                  )

        export_order = fields
