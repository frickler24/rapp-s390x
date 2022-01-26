import re
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from ..anmeldung import Anmeldung
from ..models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
    TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen, Tblrechteneuvonimport
from ..view_import import patch_datum, neuer_import
from ..views import home


def schoen(s: object) -> object:
    print(str(s).replace('\\n', '\n').replace(
        '\\r', '\r').replace('\\t', '\t'))


class AAAASetupDatabase(TestCase):
    # Immer als erstes die Stoored Procedures laden!
    def setUp(self):
        Anmeldung(self.client.login)

    def test_setup_setup_database_load_stored_proc(self):
        url = reverse('stored_procedures')
        data = {}
        self.response = self.client.post(url, data)
        self.assertContains(
            self.response, 'push_sp_anzahl_import_elemente war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_vorbereitung war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_neue_user war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_behandle_user war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_behandle_rechte war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_loesche_doppelte_rechte war erfolgreich.', 1)
        self.assertNotContains(
            self.response, 'push_sp_nichtai war erfolgreich.')
        self.assertContains(
            self.response, 'push_sp_erzeuge_af_liste war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_ueberschreibe_modelle war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_direct_connects war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_af_umbenennen war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_ungenutzte_teams war erfolgreich.', 1)
        self.assertContains(
            self.response, 'push_sp_rolle_umbenennen war erfolgreich.', 1)


class ZZZZSetupDatabase(AAAASetupDatabase):
    """
    Der Klassen-Hack hier wird benötigt, damit sowohl beim Vorwärts- als auch beim Rückwärtstest
    immer als erstes die Datenbank mit den Stored Procedures initialisiert wird.
    Das geht wahrscheinlich auch anders...
    """
    pass


class HomeTests(TestCase):
    def xtest_something_is_running(self):
        self.assertTrue(True)

    # Funktioniert die Einstiegsseite?
    def xtest_home_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def xtest_home_url_resolves_home_view(self):
        view = resolve('/rapp/')
        self.assertEqual(view.func, home)

    def test_home_url_gets_info_screen(self):
        # Alle Daten erscheinen auf der Übersichtsseiteo
        url = reverse('home')
        self.response = self.client.get(url)

        self.assertEqual(self.response.status_code, 200)
        self.assertContains(
            self.response, 'Statistik über die RApp-Inhalte:', 1)
        self.assertContains(self.response, 'Status Stored Procedures:', 1)
        self.assertContains(self.response, 'Stand letzte Importe:', 1)
        self.assertContains(self.response, 'Administrierte Berechtigungen:', 1)
        self.assertContains(self.response, 'Aktive Rechte:', 1)
        self.assertContains(self.response, 'Administrierte UserIDs:', 1)
        self.assertContains(self.response, 'Aktive UserIDs:', 1)
        self.assertContains(self.response, 'UserIDs von AI-BA:', 1)
        self.assertContains(self.response, 'Vorhandene Teams:', 1)
        self.assertContains(self.response, 'Bekannte Plattformen:', 1)
        self.assertContains(self.response, 'Anwender der RApp:', 1)
        self.assertContains(self.response, 'Aktuelle TFen in AI-BA:', 1)
        # self.assertContains(self.response, '/static/admin/img/icon-yes.svg', 1)


class GesamtlisteTests(TestCase):
    # Funktioniert die Gesamtliste?
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

        for i in range(100):
            TblOrga.objects.create(
                team='Django-Team-{}'.format(i),
                themeneigentuemer='Ihmchen_{}'.format(2 * i)
            )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            kommentar='Kein Kommentar',
            zielperson='Lutz',
            af_text='Das ist der AF-normaltext',
            gf_text='Das ist der AF-normaltext',
            af_langtext='Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
            af_ausschlussgruppen='Das soll niemand außer mir bekommen!!!',
            af_einschlussgruppen='das soll die ganze Welt erhalten können',
            af_sonstige_vergabehinweise='Keine Hinweise',
            geloescht=False,
            kannweg=False,
            modelliert=timezone.now(),
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00500_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00500_neue_AF auch mit mehr Zeichen als sonst',
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00380_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
        )

        for i in range(10, 20):
            TblUserIDundName.objects.create(
                userid='xv100{}'.format(i),
                name='User_xv100{}'.format(i),
                orga=TblOrga.objects.get(team='Django-Team-{}'.format(i)),
                zi_organisation='AI-BA',
                geloescht=False,
                abteilung='ZI-AI-BA',
                gruppe='ZI-AI-BA-PS',
            )

        TblPlattform.objects.create(tf_technische_plattform='RACFP')

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10011'),
            tf='Die superlange schnuckelige TF',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='Superkritisch sich ist das auch schon zu lang',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='no direct connect',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10012'),
            tf='Die superlange schnuckelige TF2',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='Superkritisch sich ist das auch schon zu lang',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='no direct connect',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

    def test_gesamtliste_view_status_code(self):
        url = reverse('gesamtliste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_gesamtliste_view_not_found_status_code(self):
        url = reverse('gesamt-detail', kwargs={'pk': 99999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # Kann das zweite Element direkt adressiert werden?
    def test_gesamtliste_view_success_status_code(self):
        url = reverse(
            'gesamt-detail', kwargs={'pk': TblGesamt.objects.get(tf='Die superlange schnuckelige TF2').id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TeamListTests(TestCase):
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

    # Geht die Team-Liste?
    # Ist die Seite da?
    # ToDo: Beim Test der Teamliste fehlen noch die drei subpanels.
    def test_teamlist_view_status_code(self):
        url = reverse('teamliste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CreateTeamTests(TestCase):
    # Geht die Team-Liste inhaltlich?
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(team='MeinTeam', themeneigentuemer='Icke')

    def test_create_team_view_success_status_code(self):
        url = reverse('team-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    """
    def test_create_team_url_resolves_new_topic_view(self):
        view = resolve('/teamliste/create/')
        self.assertEqual(view.func, TblOrgaCreate.as_view)
    """

    def test_create_team_view_contains_link_back_to_board_topics_view(self):
        new_team_url = reverse('team-create')
        teamlist_url = reverse('teamliste')
        response = self.client.get(new_team_url)
        self.assertContains(response, 'href="{0}"'.format(teamlist_url))


class UserListTests(TestCase):
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

    # Geht die User-Liste?
    # Ist die Seite da?
    def test_userlist_view_status_code(self):
        url = reverse('userliste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CreateUserTests(TestCase):
    # Geht die User-Liste inhaltlich?
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(team='Django-Team', themeneigentuemer='Ihmchen')

        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            kommentar='Kein Kommentar',
            zielperson='Lutz',
            af_text='Das ist der AF-normaltext',
            gf_text='Das ist der GF-normaltext',
            af_langtext='Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
            af_ausschlussgruppen='Das soll niemand außer mir bekommen!!!',
            af_einschlussgruppen='das soll die ganze Welt erhalten können',
            af_sonstige_vergabehinweise='Keine Hinweise',
            geloescht=False,
            kannweg=False,
            modelliert=timezone.now(),
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00500_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00500_neue_AF auch mit mehr Zeichen als sonst',
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
        )

        TblUserIDundName.objects.create(
            userid='xv10010',
            name='User_xv10010',
            orga=TblOrga.objects.get(team='Django-Team'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

    def test_create_user_view_success_status_code(self):
        url = reverse('user-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_user_view_contains_link_back_to_board_topics_view(self):
        new_user_url = reverse('user-create')
        userlist_url = reverse('userliste')
        response = self.client.get(new_user_url)
        self.assertContains(response, 'href="{0}"'.format(userlist_url))


class PanelTests(TestCase):
    # Suche-/Filterpanel. Das wird mal die Hauptseite für Reports
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01'
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02'
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            kommentar='Kein Kommentar',
            zielperson='Lutz',
            af_text='Das ist der AF-normaltext',
            gf_text='Das ist der GF-normaltext',
            af_langtext='Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
            af_ausschlussgruppen='Das soll niemand außer mir bekommen!!!',
            af_einschlussgruppen='das soll die ganze Welt erhalten können',
            af_sonstige_vergabehinweise='Keine Hinweise',
            geloescht=False,
            kannweg=False,
            modelliert=timezone.now(),
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00500_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00500_neue_AF auch mit mehr Zeichen als sonst',
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
        )

        TblUserIDundName.objects.create(
            userid='xv10099',
            name='User_xv10099',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        TblPlattform.objects.create(tf_technische_plattform='RACFP')

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10099'),
            tf='Die superlange schnuckelige TF',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='H',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00380_neueGF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='nein',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10099'),
            tf='Die superlange schnuckelige TF2',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='k',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='nein',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10099'),
            tf='Die direct connection TF3',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='ka',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='u',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='ka',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='ja',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='',
            af_zuweisungsdatum=None,
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

    # Ist die Seite da?
    def test_panel_view_status_code(self):
        url = reverse('panel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_panel_view_with_valid_selection_status_code(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?geloescht=3&userid_name__zi_organisation=ai-ba')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv10099")

    def test_panel_view_with_invalid_selection1_status_code(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?geloescht=99&userid_name__zi_organisation=ZZ-XX')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keine Treffer")

    def test_panel_view_with_invalid_selection2_status_code(self):
        url = '{0}{1}'.format(reverse('panel'), '?DAS_FELD_GIBTS_NICHT=1')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv10099")

    def test_panel_view_with_valid_userID(self):
        url = '{0}{1}'.format(reverse('panel'), '?userid_name__userid=xv10099')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 8)

    def test_panel_view_with_invalid_userID(self):
        url = '{0}{1}'.format(reverse('panel'), '?userid_name__userid=xvabc99')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_userName(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__name=User_xv10099')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 8)

    def test_panel_view_with_invalid_userName(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__name=meier%2C+f')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_team(self):
        id = TblOrga.objects.get(team='Django-Team-01').id
        url = '{0}{1}{2}'.format(reverse('panel'), '?userid_name__orga=', id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

    def test_panel_view_with_invalid_team(self):
        id = TblOrga.objects.get(team='Django-Team-02').id
        url = '{0}{1}{2}'.format(reverse('panel'), '?userid_name__orga=', id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_TFBeschreibung(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf_beschreibung=TF')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

    def test_panel_view_with_validNotActive_TFBeschreibung(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf_beschreibung=TF2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_invalid_TFBeschreibung(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf_beschreibung=gibtsnicht')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_group(self):
        url = '{0}{1}'.format(reverse('panel'), '?userid_name__gruppe=BA')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

        url = '{0}{1}'.format(reverse('panel'), '?userid_name__gruppe=AI-BA')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__gruppe=AI-BA-PS')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__gruppe=ZI-AI-BA')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__gruppe=ZI-AI-BA-PS')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 6)

    def test_panel_view_with_invalid_group(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?userid_name__gruppe=die-sollte-es-nicht-geben')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_af(self):
        url = '{0}{1}'.format(reverse(
            'panel'), '?enthalten_in_af=rva_00458_neue_AF auch mit mehr Zeichen als sonst')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)
        url = '{0}{1}'.format(
            reverse('panel'), '?enthalten_in_af=rva_00458_neue_AF')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)
        url = '{0}{1}'.format(
            reverse('panel'), '?enthalten_in_af=Zeichen als sonst')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)
        url = '{0}{1}'.format(reverse('panel'), '?enthalten_in_af=auch mit ')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)

    def test_panel_view_with_invalid_af(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?enthalten_in_af=rvo_00458_org_ba')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_tf(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?tf=Die superlange schnuckelige TF2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf=Die superlange')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)

        url = '{0}{1}'.format(reverse('panel'), '?tf=superlange schnuckelige')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)

        url = '{0}{1}'.format(reverse('panel'), '?tf=TF2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

    def test_panel_view_with_invalid_tf(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf=nö')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_tfkrit(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=h')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=H')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=k')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=K')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=u')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=U')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

    def test_panel_view_with_invalid_tfkrit(self):
        url = '{0}{1}'.format(reverse('panel'), '?tf_kritikalitaet=nix')
        response = self.client.get(url)
        # schoen(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")

    def test_panel_view_with_valid_gf(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?gf=rvg_00380_neueGF mit echt mehr Zeichen als sonst')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)
        url = '{0}{1}'.format(reverse('panel'), '?gf=rvg_00380_neueGF')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)
        url = '{0}{1}'.format(reverse('panel'), '?gf=Zeichen als sonst')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)
        url = '{0}{1}'.format(reverse('panel'), '?gf= mit echt mehr ')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 4)
        url = '{0}{1}'.format(reverse('panel'), '?gf=ka')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv10099", 2)

    def test_panel_view_with_invalid_gf(self):
        url = '{0}{1}'.format(
            reverse('panel'), '?enthalten_in_af=rvg_00458_org_ba')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv10099")


class PanelExportCSVTest(TestCase):
    # User / Rolle / AF : Das wird mal die Hauptseite für
    # Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01'
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            kommentar='Kein Kommentar',
            zielperson='Lutz',
            af_text='Das ist der AF-normaltext',
            gf_text='Das ist der GF-normaltext',
            af_langtext='Das ist der AF-Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaang-Text',
            af_ausschlussgruppen='Das soll niemand außer mir bekommen!!!',
            af_einschlussgruppen='das soll die ganze Welt erhalten können',
            af_sonstige_vergabehinweise='Keine Hinweise',
            geloescht=False,
            kannweg=False,
            modelliert=timezone.now(),
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00500_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00500_neue_AF auch mit mehr Zeichen als sonst',
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als sonst',
            name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
        )

        TblUserIDundName.objects.create(
            userid='xv10099',
            name='User_xv10099',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        TblPlattform.objects.create(tf_technische_plattform='RACFP')

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10099'),
            tf='Die superlange schnuckelige TF',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00380_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00380_neueAF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='Superkritisch sich ist das auch schon zu lang',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00380_neueGF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='no direct connect',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv10099'),
            tf='Die superlange schnuckelige TF2',
            tf_beschreibung='Die superlange schnuckelige TF-Beschreibung',
            enthalten_in_af='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_af_neu='rva_00458_neue_AF auch mit mehr Zeichen als sonst',
                                                  name_gf_neu='rvg_00458_neueGF mit echt mehr Zeichen als sonst'),
            tf_kritikalitaet='Superkritisch sich ist das auch schon zu lang',
            tf_eigentuemer_org='Keine Ahnung Org',
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='RACFP'),
            gf='rvg_00458_neueAF mit echt mehr Zeichen als sonst',
            af_gueltig_ab=timezone.now() - timedelta(days=365),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            direct_connect='no direct connect',
            hoechste_kritikalitaet_tf_in_af='u',
            gf_beschreibung='Die superlange, mindestens 250 Zeichen umfassende GF-Beschreibung. Hier könnte man auch mal nach CRLF suchen',
            af_zuweisungsdatum=timezone.now() - timedelta(days=200),
            datum=timezone.now() - timedelta(days=500),
            geloescht=False,
            gefunden=True,
            wiedergefunden=timezone.now(),
            geaendert=False,
            neueaf='',
            nicht_ai=False,
            patchdatum=None,
            wertmodellvorpatch='Hier kommt nix rein',
            loeschdatum=None,
            letzte_aenderung=None
        )

    # Eine leere Auswahl
    def test_panel_online_without_selection(self):
        url = reverse('panel_download')
        response = self.client.get(url)
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Name\tTeam\tTF\tTF Beschreibung\tAF\tAF Beschreibung\tHöchste Kritikalitaet TFin AF\tGF\tgf_beschreibung\tZI-Orga\tPlattform\tTF Kritikalität\tRecht aktiv\tUser aktiv\tloeschdatum\taf_gueltig_ab\taf_gueltig_bis\tdirect_connect\taf_zuweisungsdatum\ttf_eigentuemer_org\tgefunden\twiedergefunden\tletzte_aenderung\tAF Neu\tGF Neu\r",
                            1)
        self.assertContains(response, "Die superlange schnuckelige TF\tDie superlange schnuckelige TF-Beschreibung\t",
                            1)
        self.assertContains(response, "Die superlange schnuckelige TF2\tDie superlange schnuckelige TF-Beschreibung\t",
                            1)
        self.assertContains(
            response, "rva_00458_neue_AF auch mit mehr Zeichen als ", 3)
        self.assertContains(
            response, "rvg_00458_neueGF mit echt mehr Zeichen als ", 1)
        self.assertContains(response, "User_xv10099\tDjango-Team-01\t", 2)
        self.assertContains(
            response, "rva_00380_neue_AF auch mit mehr Zeichen als ", 1)
        self.assertContains(
            response, "rvg_00380_neueAF mit echt mehr Zeichen als ", 1)

    # Eine gültige Auswahl für einen User in einer Gruppe
    def test_panel_online_with_valid_selection(self):
        url = '{0}{1}'.format(reverse('panel_download'), '?tf=TF2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Name\tTeam\tTF\tTF Beschreibung\tAF\tAF Beschreibung\tHöchste Kritikalitaet TFin AF\tGF\tgf_beschreibung\tZI-Orga\tPlattform\tTF Kritikalität\tRecht aktiv\tUser aktiv\tloeschdatum\taf_gueltig_ab\taf_gueltig_bis\tdirect_connect\taf_zuweisungsdatum\ttf_eigentuemer_org\tgefunden\twiedergefunden\tletzte_aenderung\tAF Neu\tGF Neu",
                            1)
        self.assertNotContains(response, "Die superlange schnuckelige TF\t")
        self.assertNotContains(
            response, "rva_00380_neue_AF auch mit mehr Zeichen als ")
        self.assertNotContains(
            response, "rvg_00380_neueAF mit echt mehr Zeichen als ")
        self.assertContains(
            response, "rva_00458_neue_AF auch mit mehr Zeichen als ", 2)
        self.assertContains(
            response, "rvg_00458_neueGF mit echt mehr Zeichen als ", 1)
        self.assertContains(response, "Die superlange schnuckelige TF2\tDie superlange schnuckelige TF-Beschreibung\t",
                            1)
        self.assertContains(response, "User_xv10099\tDjango-Team-01\t", 1)


class UserRolleAFTestsGeneratePDF(TestCase):
    # Der Testfall muss aufgrund der PDF-Lieferung separat gehalten werden
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei User: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        # Zwei Rollen, die auf den XV-User vergeben werden
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    def test_panel_view_use_konzept_pdf(self):
        print()  # weil das PDF immer irgend eine Warnung ausgibt
        pdf_url = reverse('uhr_konzept_pdf')
        response = self.client.get(pdf_url)
        # Und trotzdem funktioniert es
        self.assertEqual(response.status_code, 200)


class UserRolleAFTests(TestCase):
    # User / Rolle / AF: Die Hauptseite für Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nu',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei User: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        # Zwei Rollen, die auf den XV-User vergeben werden
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=None,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Hier fehlt die Mussfeld-Angabe',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01219_beta91_job_abst_nu",
            name_af_neu="rva_01219_beta91_job_abst_nu",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Ist die Seite da?
    def test_panel_view_status_code(self):
        url = reverse('user_rolle_af')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_panel_view_with_valid_selection_status_code(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")

    # Hat der User zwei Rollen (XV un DV)?
    def test_panel_view_num_userids(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertContains(response, "dv13254")

    def test_panel_view_num_roles(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")
        self.assertContains(response, '(2 Rollen,')

    # Sind bei einer der Rollen ein Recht nicht vergeben und zwei Rechte vergeben und insgesamt 3 Rechte behandelt?
    def test_panel_view_with_deep_insight(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")
        self.assertContains(response, 'icon-yes', 2)
        self.assertContains(response, 'icon-no', 5)
        self.assertContains(response, 'icon-alert', 1)

    def test_panel_view_with_deep_insight_find_delete_link(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")
        rolle1 = TblUserhatrolle.objects.get(
            userid='xv13254', rollenname='Erste Neue Rolle')
        rolle2 = TblUserhatrolle.objects.get(
            userid='xv13254', rollenname='Zweite Neue Rolle')
        self.assertContains(
            response, '/rapp/user_rolle_af/{}/delete/?'.format(rolle1), 1)
        self.assertContains(
            response, '/rapp/user_rolle_af/{}/delete/?'.format(rolle2), 1)

        # Zum Abschluss klicken wir mal auf die Löschlinks und erhalten die Sicherheitsabfrage.
        # Erster Link
        loeschurl = '/rapp/user_rolle_af/{}/delete/'.format(rolle1)
        response = self.client.get(loeschurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
        self.assertContains(response, '<p>"Erste Neue Rolle":</p>')
        # Zweiter Link
        loeschurl = '/rapp/user_rolle_af/{}/delete/'.format(rolle2)
        response = self.client.get(loeschurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
        self.assertContains(response, '<p>"Zweite Neue Rolle":</p>')

    def test_panel_view_with_deep_insight_find_change_link(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")

        rolle1 = TblUserhatrolle.objects.get(
            userid='xv13254', rollenname='Erste Neue Rolle')
        rolle2 = TblUserhatrolle.objects.get(
            userid='xv13254', rollenname='Zweite Neue Rolle')
        changeurl1 = '/adminrapp/tbluserhatrolle/{}/change/?'.format(rolle1)
        changeurl2 = '/adminrapp/tbluserhatrolle/{}/change/?'.format(rolle2)

        self.assertContains(response, changeurl1, 1)
        self.assertContains(response, changeurl2, 1)

        # ToDo Zum Abschluss klicken wir mal auf die Change-Links und erhalten den Änderungsdialog.
        """
        Aus welchen Gründen auch immer das hier nur zu einer Weiterleitung 302 führt...
        # Erster Link
        response = self.client.get(changeurl1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User und Ihre Rollen ändern')
        self.assertContains(response, '<option value="Erste Neue Rolle">')
        #Zweiter Link
        response = self.client.get(changeurl2)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User und Ihre Rollen ändern')
        self.assertContains(response, '<option value="Zweite Neue Rolle">')
        """

    def test_panel_view_with_deep_insight_find_create_link(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")
        self.assertContains(
            response, '/rapp/user_rolle_af/create/xv13254/?&', 1)

        # Zum Abschluss klicken wir mal auf den Create-Link und erhalten den Erstellungsdialog.
        createurl = '/rapp/user_rolle_af/create/xv13254/?&name=&orga=1&rollenname=&gruppe=&user='
        response = self.client.get(createurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rollen-Eintrag ergänzen für')
        self.assertContains(
            response, '<option value="xv13254">xv13254 | User_xv13254</option>')
        self.assertContains(
            response, '<option value="" selected>---------</option>', 2)
        self.assertContains(response, '<option value="">---------</option>', 1)

    def test_panel_view_with_deep_insight_find_export_link(self):
        id = TblUserIDundName.objects.get(userid='xv13254').id
        url = '{0}{1}/{2}'.format(reverse('user_rolle_af'),
                                  id, '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")
        # Nun klicken wir mal auf den Export-Link und erhalten den Erstellungsdialog.
        exporturl = '/rapp/user_rolle_af/export/{}/?'.format(id)
        self.assertContains(response, exporturl)
        response = self.client.get(exporturl)
        self.assertEqual(response.status_code, 200)
        # print('____________')
        # print(response.content)
        # gesuchter_exportstring = "Name\tRollenname\tAF\tMussrecht\txv13254\tdv13254\r\n" \
        #     + "User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst\tja\tja\tnein\r\n" \
        #     + "User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst_nicht_zugewiesen\tundef\tnein\tnein\r\n" \
        #     + "User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst_nicht_zugewiesen\tja\tnein\tnein\r\n" \
        #     + "User_xv13254\tZweite Neue Rolle\trva_01219_beta91_job_abst\tnein\tja\tnein\r\n"

        self.assertContains(
            response, 'Name\tRollenname\tAF\tMussrecht\txv13254\tdv13254\r\n')
        self.assertContains(
            response, 'User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst\tja\tja\tnein\r\n')
        self.assertContains(response,
                            'User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst_nicht_zugewiesen\tja\tnein\tnein\r\n')
        self.assertContains(response,
                            'User_xv13254\tErste Neue Rolle\trva_01219_beta91_job_abst_nicht_zugewiesen\tundef\tnein\tnein\r\n')
        self.assertContains(response,
                            'User_xv13254\tZweite Neue Rolle\trva_01219_beta91_job_abst\tnein\tja\tnein\r\n')
        # self.assertContains(response, gesuchter_exportstring)

    def test_panel_view_with_invalid_selection_status_code(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?geloescht=99&zi_organisation=ZZ-XX')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keine angezeigten User")

    def test_panel_view_with_invalid_selection_returns_complete_list_status_code(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?DAS_FELD_GIBTS_NICHT=1')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254")

    def test_panel_view_contains_link_back_to_home_view(self):
        new_user_url = reverse('user_rolle_af')
        userlist_url = reverse('home')
        response = self.client.get(new_user_url)
        self.assertContains(response, 'href="{0}"'.format(userlist_url))

    # Gibt es den "Konzept" Button?
    def test_panel_view_contains_link_to_konzept_view(self):
        url = reverse('user_rolle_af')
        konzept_url = reverse('uhr_konzept')
        response = self.client.get(url)
        self.assertContains(
            response, 'href="{0}?episch=0"'.format(konzept_url), 1)
        self.assertContains(
            response, 'href="{0}?episch=9"'.format(konzept_url), 1)

    def test_panel_view_contains_link_to_matrix_view(self):
        url = reverse('user_rolle_af')
        konzept_url = reverse('uhr_matrix')
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}?"'.format(konzept_url))

    def test_panel_view_contains_no_user_first(self):
        url = reverse('user_rolle_af')
        response = self.client.get(url)
        self.assertContains(response, 'Kein User selektiert', 1)

    def test_panel_view_use_konzept_view(self):
        url = reverse('uhr_konzept')
        pdf_url = reverse('uhr_konzept_pdf')
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}?episch=1"'.format(pdf_url), 1)
        self.assertContains(response, 'Erste Neue Rolle', 1)
        self.assertContains(response, 'Zweite Neue Rolle', 1)
        self.assertContains(response, 'rva_01219_beta91_job_abst', 4)
        self.assertContains(response, 'Das ist eine Testrolle', 1)
        self.assertContains(response, 'Das ist auch eine Testrolle', 1)
        self.assertContains(response, 'Testsystem', 1)
        self.assertContains(response, 'Irgendein System', 1)
        self.assertContains(response, 'Erzeuge PDF kurz', 1)
        self.assertContains(response, 'Erzeuge PDF mit TF-Auflösung', 1)
        self.assertContains(response, 'Erzeuge PDF episch,', 1)
        self.assertContains(response, '<div>Keine TF-Menge geliefert</div>', 1)
        self.assertContains(
            response, '<div>Keine RACF-Liste geliefert</div>', 1)
        self.assertContains(
            response, '<div>Keine Db2-Daten geliefert</div>', 1)
        self.assertContains(
            response, '<div>Keine ACL-Daten geliefert</div>', 1)

    def test_panel_view_use_matrix_view(self):
        url = reverse('uhr_matrix')
        pdf_url = reverse('uhr_matrix_csv')
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}?"'.format(pdf_url))
        self.assertContains(response, '<small>Erste Neue Rolle</small>', 1)
        self.assertContains(response, '<small>Zweite Neue Rolle</small>', 1)
        self.assertContains(response, 'User_xv13254', 1)
        self.assertContains(response, 'Schwerpunkt', 1)
        self.assertContains(response, 'Vertretung', 1)

    # Suche nach dem User und ob seiner UserID mindestens eine Rolle zugeodnet ist.
    # Falls ja, suche weiter nach der Liste der AFen zu der Rolle (Auszug).
    # Im Detail: Wir suchen über /.../user_rolle_af/<Nummer des Eintrags UserHatRolle>
    # nach dem konkreten Eintrag (die Nummer variiert über die Anzahl der ausgeführten Testfälle,
    # deshalb das etwas umständliche Gesuche unten).
    def test_panel_view_with_valid_selection_find_UserHatRolle_id(self):
        id = TblOrga.objects.get(team='Django-Team-01').id
        url = '{0}{1}{2}{3}'.format(
            reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Die UserID gibt es schon mal
        self.assertContains(response, "User_xv13254")

        suchstr = "Wir haben in der ReST-Schreibweise keinen Treffer gelandet!"
        for k in response:
            foo = re.search('/user_rolle_af/(\d+)/', str(k))
            if foo != None:
                suchstr = re.split('/', str(foo))
                suchstr = ("/{}/{}/".format(suchstr[1], suchstr[2]))
        # Die UserIDhatRolle-Zeile wurde in der ReST-Schreibweise gefunden
        self.assertContains(response, suchstr)

    def test_panel_view_with_valid_selection_find_accordeon_link(self):
        id = TblOrga.objects.get(team='Django-Team-01').id
        url = '{0}{1}{2}{3}'.format(
            reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        for k in response:
            foo = re.search('/user_rolle_af/(\d+)/', str(k))
            if foo != None:
                suchstr = re.split('/', str(foo))
                url = '{0}{1}/{2}{3}{4}'.format(reverse('user_rolle_af'),
                                                suchstr[2],
                                                '?name=&orga=', id, '&gruppe=&pagesize=100')
                # print ()
                # print ('suche nach folgender URL: {}'.format (url))
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
            else:
                # Das war nix - offensichtlich die URL nicht korrekt
                self.assertFalse(True)
        self.assertContains(response, 'Erste Neue Rolle')  # Rollenname
        self.assertContains(response, 'Testsystem')  # System
        # Beschreibung in TblRollen
        self.assertContains(response, 'Das ist eine Testrolle')
        # Die gesuchte AF eine Stufe tiefer
        self.assertContains(response, 'rva_01219_beta91_job_abst')
        # Beschreibung in TblUserHatRolle
        self.assertContains(response, 'Das ist eine Testrolle für ZI-AI-BA-PS')
        # Wertigkeit in der Verantwortungsmatrix
        self.assertContains(response, 'Schwerpunkt')


class UserRolleVariantsTest(TestCase):
    # User / Rolle / AF : Das wird mal die Hauptseite für
    # Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei UserIDen für eine Identität: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv
        TblUserIDundName.objects.create(
            userid='xv00042',
            name='User_xv00042',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv: Für diesen User gibt es noch keine eingetragene Rolle
        TblUserIDundName.objects.create(
            userid='xv00023',
            name='User_xv00023',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Zwei Rollen, die auf den ersten XV-User vergeben werden, die zweite wird auch dem m2. User vergeben
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen zu Rollen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # User 12354_ Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Dem zweiten User 00042 wird nur eine Rolle zugeordnet
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv00042'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Und dem dritten User 00023 keine Rolle

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00042'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        # ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Ist die Seite da?
    def test_panel_01_view_status_code(self):
        url = reverse('user_rolle_af')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Eine gültige Auswahl für einen User in einer Gruppe: Das nutzt noch das erste Panel in der Ergebnisanzeige
    def test_panel_02_view_with_valid_selection(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertNotContains(response, "Betrachtung von Rollenvarianten")

    def test_panel_03_view_with_valid_role_star_name_and_group(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=*&name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254", 4)
        self.assertContains(response, "xv00042", 5)
        self.assertContains(response, "xv00023", 2)

    def test_panel_03a_view_with_valid_role_star_unique_name_and_group(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=*&name=UseR_xv00023&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv13254")
        self.assertNotContains(response, "xv00042")
        self.assertContains(response, "xv00023", 7)
        self.assertContains(response, "Export", 1)

    def test_panel_04_view_with_valid_role_star(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertContains(response, "Betrachtung von Rollenvarianten")
        self.assertContains(response, "rva_01219_beta91_job_abst", 5)
        # Beide Identitäten haben eine Rolle, für die es mehrere Varianten gibt.
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00042/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=*#xv00042.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00042/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=*#xv00042.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        # Die Löschlinks enthalten die Nummern der User-hat-Rolle-Definition. Das brauchen wir später nochmal
        erste_rolle_des_ersten_users = TblUserhatrolle.objects.get(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first())
        zweite_rolle_des_ersten_users = TblUserhatrolle.objects.get(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'))
        rolle_des_zweiten_users = TblUserhatrolle.objects.get(userid=TblUserIDundName.objects.get(userid='xv00042'),
                                                              rollenname=TblRollen.objects.first())
        str11 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(
            erste_rolle_des_ersten_users)
        str12 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(
            zweite_rolle_des_ersten_users)
        str2 = '<a href="/rapp/user_rolle_af/{}/delete/?&rollenname=*&user=">'.format(
            rolle_des_zweiten_users)

        self.assertContains(response, str11)
        self.assertContains(response, str12)
        self.assertContains(response, str2)

        # Zum Abschluss klicken wir mal auf einen der Löschlinks und erhalten die Sicherheitsabfrage:
        loeschurl = '/rapp/user_rolle_af/{}/delete/?&rollenname=*&user='.format(
            erste_rolle_des_ersten_users)
        response = self.client.get(loeschurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<p>Sie löschen gerade den folgenden Rollen-Eintrag:</p>')
        self.assertContains(response, '<p>"Erste Neue Rolle":</p>')

        response = self.client.post(loeschurl, {'rollenname': erste_rolle_des_ersten_users,
                                                'userid': TblUserIDundName.objects.get(userid='xv13254')
                                                })
        self.assertEqual(response.status_code, 302)
        # ToDo Hier sollte eigentlich ein Eintrag gelöscht worden sein - das klappt aber nicht (XSRF-Token?)

    def test_panel_06_view_with_valid_role_star(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=*')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertContains(response, "Betrachtung von Rollenvarianten")
        self.assertContains(response, "rva_01219_beta91_job_abst", 5)
        # Beide Identitäten haben eine Rolle, für die es mehrere Varianten gibt.
        # ToDo Der Testfall muss angepasst werden, wenn die Doppelnennung von Rollen behandelt wird
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00042/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=*#xv00042.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        # Zum Abschluss klicken wir mal auf einen der Löschlinks und erhalten die Sicherheitsabfrage:
        createurl = '/rapp/user_rolle_af/{}/create/{}%20Neue%20Rolle/Schwerpunkt?&rollenname=*#{}.rva_01219_beta91_job_abst' \
            .format('xv00042', 'Zweite', 'xv00042')
        response = self.client.get(createurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Rollen-Eintrag ergänzen für <strong></strong>')
        self.assertContains(response, '<option value="">---------</option>', 3)
        self.assertContains(
            response, '<option value="xv00042">xv00042 | User_xv00042</option>')
        self.assertContains(
            response, '<option value="xv13254">xv13254 | User_xv13254</option>')
        self.assertContains(
            response, '<option value="dv13254">dv13254 | User_xv13254</option>')
        # ToDo Achtung, hier werden in der Liste auch gelöschte User angezeigt!
        # self.assertNotContains(response, '<option value="av13254">av13254 | User_xv13254</option>')
        self.assertContains(
            response, '<option value="Erste Neue Rolle">Erste Neue Rolle</option>')
        self.assertContains(
            response, '<option value="Zweite Neue Rolle" selected>Zweite Neue Rolle</option>')
        self.assertContains(
            response, '<option value="Schwerpunkt" selected>Schwerpunktaufgabe</option>')
        self.assertContains(
            response, '<option value="Vertretung">Vertretungstätigkeiten, Zweitsysteme</option>')
        self.assertContains(
            response, '<option value="Allgemein">Rollen, die nicht Systemen zugeordnet sind</option>')
        # self.assertContains(response,
        #                     '<th><label for="id_bemerkung">Bemerkung:</label></th><td><textarea name="bemerkung" cols="40" rows="10" id="id_bemerkung">')
        response = self.client.post(createurl, {'rollenname': "Erste Neue Rolle",
                                                'userid': TblUserIDundName.objects.get(userid='xv13254')
                                                })
        # Todo: Warum geht das? Die Rolle ist doch schon vergeben...
        self.assertEqual(response.status_code, 200)


class UserRolleNurNeueAFTest(TestCase):
    # User / Rolle / AF : Das wird mal die Hauptseite für
    # Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei UserIDen für eine Identität: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv
        TblUserIDundName.objects.create(
            userid='xv00042',
            name='User_xv00042',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv: Für diesen User gibt es noch keine eingetragene Rolle
        TblUserIDundName.objects.create(
            userid='xv00023',
            name='User_xv00023',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Zwei Rollen, die auf den ersten XV-User vergeben werden, die zweite wird auch dem 2. User vergeben
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen zu Rollen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # User 12354_ Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Dem zweiten User 00042 wird nur eine Rolle zugeordnet
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv00042'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Und dem dritten User 00023 keine Rolle

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01219_beta91_job_abst",
            name_af_neu="rva_01219_beta91_job_abst",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00042'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        # ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

        # Der XV-User der dritten Identität erhält ein Recht, das einer Rolle zugeordnet ist, die er aber noch nicht hat
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00023'),
            tf='eine_TF_in_rva_01219_beta91_job_abst',
            tf_beschreibung='TF-Beschreibung für eine_TF_in_rva_01219_beta91_job_abst',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die viertegeniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='rvg_01219_beta91_job_abst',
            datum=timezone.now() - timedelta(days=42),
            geloescht=False,
        )

    """
    def test_vorbereiten_rufe_startseite(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    """

    def test_panel_01_view_status_code(self):
        """
        Ist die Seite vorhanden?
        """
        url = reverse('user_rolle_af')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_panel_02_view_with_valid_selection(self):
        """
        Eine gültige Auswahl für einen User in einer Gruppe:
        Das nutzt noch das erste Panel in der Ergebnisanzeige
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertNotContains(response, "Betrachtung von Rollenvarianten")

    def test_panel_03_view_with_valid_role_star_name_and_group(self):
        """
        Zum Vergleich wird hier nochmal geprüft, ob die "*"-Anzeige für die geänderten Userelemente korrekt ist
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=-&name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254", 2)
        self.assertContains(response, "xv00042", 2)
        self.assertContains(response, "xv00023", 7)
        self.assertContains(response, "nicht vergeben", 1)
        self.assertContains(response, "Erste Neue Rolle", 1)
        self.assertContains(response, "Zweite Neue Rolle", 1)
        self.assertContains(
            response, "Keine AF zugewiesen oder durch Filter ausgeblendet", 3)

    def test_panel_03_view_with_valid_role_dash_name_and_group(self):
        """
        Die gleiche Anordnung wie in test_panel_03_view_with_valid_role_star_name_and_group,
        aber nun mit dem mSuchstring "-" für die Rolle.
        Damit müssten alle AFen, die zu einer zugewiesenen Rollen gehören, ausgeblendet werden.
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=-&name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254", 2)
        self.assertContains(response, "xv00042", 2)
        self.assertContains(response, "xv00023", 7)
        self.assertContains(response, "nicht vergeben", 1)
        self.assertContains(response, "Erste Neue Rolle", 1)
        self.assertContains(response, "Zweite Neue Rolle", 1)
        self.assertContains(
            response, "Keine AF zugewiesen oder durch Filter ausgeblendet", 3)

    def test_panel_04_view_with_valid_role_dash_unique_name_and_group(self):
        """
        Suche nach den nicht zugewiesenen AFen bei einem vorgegebenen User, der so etwas enthält.
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=-&name=UseR_xv00023&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "xv13254")
        self.assertContains(response, "Export", 1)
        self.assertNotContains(response, "xv00042")
        self.assertContains(response, "xv00023", 14)
        self.assertContains(response, "nicht vergeben", 1)
        self.assertContains(response, "Erste Neue Rolle", 1)
        self.assertContains(response, "Zweite Neue Rolle", 1)
        self.assertNotContains(
            response, "Keine AF zugewiesen oder durch Filter ausgeblendet")

    def test_panel_05_view_with_valid_role_dash_unique_name_and_group_not_containing_new_AF(self):
        """
        Suche nach den nicht zugewiesenen AFen bei einem vorgegebenen User, der so etwas nicht enthält.
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=-&name=UseR_xv13254&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254", 7)
        self.assertContains(response, "Export", 1)
        self.assertNotContains(response, "xv00042")
        self.assertNotContains(response, "xv00023")
        self.assertNotContains(response, "nicht vergeben")
        self.assertNotContains(response, "Erste Neue Rolle")
        self.assertNotContains(response, "Zweite Neue Rolle")
        self.assertContains(
            response, "Keine AF zugewiesen oder durch Filter ausgeblendet", 2)

    def test_panel_06_view_with_valid_role_dash(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=-')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254", 2)
        self.assertContains(response, "Betrachtung von Rollenvarianten", 1)
        self.assertContains(response, "rva_01219_beta91_job_abst", 4)
        # Zwei Identitäten haben eine Rolle, für die es mehrere Varianten gibt, eine Identität hat keine Rolle
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00023/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=-#xv00023.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00023/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=-#xv00023.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        self.assertContains(response, "nicht vergeben", 1)
        self.assertContains(response, "Erste Neue Rolle", 1)
        self.assertContains(response, "Zweite Neue Rolle", 1)
        self.assertContains(
            response, "Keine AF zugewiesen oder durch Filter ausgeblendet", 3)

        # Es sollten keine Löschlinks vorhanden sein
        self.assertNotContains(response, '/delete/?&rollenname=')

    def test_panel_07_view_with_valid_role_dash(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=-')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertContains(response, "Betrachtung von Rollenvarianten")
        self.assertContains(response, "rva_01219_beta91_job_abst", 4)
        # In dieser Ansicht hat nur ein Identität nicht vergebene Rollen zu AFen
        self.assertContains(response,
                            '<a href="/rapp/user_rolle_af/xv00023/create/Zweite%2520Neue%2520Rolle/Schwerpunkt?&rollenname=-#xv00023.rva_01219_beta91_job_abst">Zweite Neue Rolle</a>',
                            1)
        # Zum Abschluss klicken wir mal auf einen der Zuordnungs-links und erhalten die Sicherheitsabfrage:
        createurl = '/rapp/user_rolle_af/{}/create/{}%20Neue%20Rolle/Schwerpunkt?&rollenname=-#{}.rva_01219_beta91_job_abst' \
            .format('xv00023', 'Zweite', 'xv00023')
        response = self.client.get(createurl)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Rollen-Eintrag ergänzen für <strong></strong>')
        self.assertContains(response, '<option value="">---------</option>', 3)
        self.assertContains(
            response, '<option value="xv00042">xv00042 | User_xv00042</option>')
        self.assertContains(
            response, '<option value="xv13254">xv13254 | User_xv13254</option>')
        self.assertContains(
            response, '<option value="dv13254">dv13254 | User_xv13254</option>')
        # ToDo Achtung, hier werden in der Liste auch gelöschte User angezeigt (uhr_form.html anpassen)!
        # self.assertNotContains(response, '<option value="av13254">av13254 | User_xv13254</option>')
        self.assertContains(
            response, '<option value="Erste Neue Rolle">Erste Neue Rolle</option>')
        self.assertContains(
            response, '<option value="Zweite Neue Rolle" selected>Zweite Neue Rolle</option>')
        self.assertContains(
            response, '<option value="Schwerpunkt" selected>Schwerpunktaufgabe</option>')
        self.assertContains(
            response, '<option value="Vertretung">Vertretungstätigkeiten, Zweitsysteme</option>')
        self.assertContains(
            response, '<option value="Allgemein">Rollen, die nicht Systemen zugeordnet sind</option>')
        # self.assertContains(response,
        #                     '<th><label for="id_bemerkung">Bemerkung:</label></th><td><textarea name="bemerkung" cols="40" rows="10" id="id_bemerkung">')


class UserRolleUnbenutzteAFTest(TestCase):
    # User / Rolle / AF : Das wird mal die Hauptseite für
    # Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei UserIDen für eine Identität: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv
        TblUserIDundName.objects.create(
            userid='xv00042',
            name='User_xv00042',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv: Für diesen User gibt es noch keine eingetragene Rolle
        TblUserIDundName.objects.create(
            userid='xv00023',
            name='User_xv00023',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Zwei Rollen, die auf den ersten XV-User vergeben werden, die zweite wird auch dem 2. User vergeben
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen zu Rollen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # User 12354_ Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Dem zweiten User 00042 wird nur eine Rolle zugeordnet
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv00042'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Und dem dritten User 00023 keine Rolle

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01219_beta91_job_abst",
            name_af_neu="rva_01219_beta91_job_abst",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00042'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        # ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

        # Der XV-User der dritten Identität erhält ein Recht, das einer Rolle zugeordnet ist, die er aber noch nicht hat
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00023'),
            tf='eine_TF_in_rva_01219_beta91_job_abst',
            tf_beschreibung='TF-Beschreibung für eine_TF_in_rva_01219_beta91_job_abst',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die viertegeniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='rvg_01219_beta91_job_abst',
            datum=timezone.now() - timedelta(days=42),
            geloescht=False,
        )

    """
    def test_vorbereiten_rufe_startseite(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    """

    def test_panel_01_view_status_code(self):
        """
        Ist die Seite vorhanden?
        """
        url = reverse('user_rolle_af')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_panel_02_view_with_valid_selection(self):
        """
        Eine gültige Auswahl für einen User in einer Gruppe:
        Das nutzt noch das erste Panel in der Ergebnisanzeige
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "xv13254")
        self.assertNotContains(
            response, " die Selektion ungenutzte Arbeitsplatzfunktionen in den angegebenen Rollen")

    def test_panel_03_view_with_valid_role_plus_name_and_group(self):
        """
        Die gleiche Anordnung wie in test_panel_03_view_with_valid_role_star_name_and_group,
        aber nun mit dem mSuchstring "-" für die Rolle.
        Damit müssten alle AFen, die zu einer zugewiesenen Rollen gehören, ausgeblendet werden.
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=%2B&name=UseR&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Keine angezeigten User", 1)
        self.assertContains(response, "Rollenname", 1)
        self.assertContains(response, "Ungenutzte AF", 2)
        self.assertContains(response, "Erste Neue Rolle", 3)
        self.assertContains(
            response, "rva_01219_beta91_job_abst_nicht_zugewiesen", 2)
        self.assertContains(
            response, " die Selektion ungenutzte Arbeitsplatzfunktionen in den angegebenen Rollen", 1)

    def test_panel_04_view_with_valid_role_plus_unique_name_and_group(self):
        """
        Suche nach den nicht zugewiesenen AFen bei einem vorgegebenen User, der so etwas enthält.
        """
        url = '{0}{1}'.format(reverse('user_rolle_af'),
                              '?rollenname=%2B&name=UseR_xv00023&gruppe=BA-ls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, " die Selektion ungenutzte Arbeitsplatzfunktionen in den angegebenen Rollen")
        self.assertContains(response, "Keine angezeigten User", 1)
        self.assertContains(response, "Keine AF-Liste erkannt", 1)

    def test_panel_06_view_with_valid_role_dash(self):
        url = '{0}{1}'.format(reverse('user_rolle_af'), '?rollenname=%2B')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erste Neue Rolle", 3)
        self.assertContains(response,
                            'href="/adminrapp/tblrollen/Erste Neue Rolle/change">', 1)


class UserRolleExportCSVTest(TestCase):
    # User / Rolle / AF : Das wird mal die Hauptseite für
    # Aktualisierungen / Ergänzungen / Löschungen von Rollen und Verbindungen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_Beta91_Job_Abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_Beta91_Job_Abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei User: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='Dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='aV13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        # Zwei Rollen, die auf den XV-User vergeben werden
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_Beta91_Job_Abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_Beta91_Job_Abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_Beta91_Job_Abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),
        )

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        # ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='Sollte die AF rva_01219_beta91_job_abst sein',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Eine leere Auswahl
    def test_matrix_online_without_selection(self):
        url = reverse('uhr_matrix')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254", 1)
        self.assertContains(
            response, '<a href="/rapp/user_rolle_af/matrix_csv/?"', 1)
        self.assertContains(
            response, '<a href="/rapp/user_rolle_af/matrix_csv/kompakt/?"', 1)
        self.assertContains(
            response, '<th><small>Erste Neue Rolle</small></th>', 1)
        self.assertContains(
            response, '<th><small>Zweite Neue Rolle</small></th>', 1)
        self.assertContains(response, 'Django-Team-01', 2)
        self.assertContains(response, 'Schwerpunkt', 1)
        self.assertContains(response, 'Vertretung', 1)

    # Eine gültige Auswahl für einen User in einer Gruppe
    def test_matrix_online_with_valid_selection(self):
        url = '{0}{1}'.format(reverse('uhr_matrix'), '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User_xv13254", 1)
        self.assertContains(
            response, '<a href="/rapp/user_rolle_af/matrix_csv/?name=UseR&gruppe=BA-ps&"', 1)
        self.assertContains(
            response, '<a href="/rapp/user_rolle_af/matrix_csv/kompakt/?name=UseR&gruppe=BA-ps&"', 1)
        self.assertContains(
            response, '<th><small>Erste Neue Rolle</small></th>', 1)
        self.assertContains(
            response, '<th><small>Zweite Neue Rolle</small></th>', 1)
        self.assertContains(response, 'Django-Team-01', 2)
        self.assertContains(response, 'Schwerpunkt', 1)
        self.assertContains(response, 'Vertretung', 1)

    # Eine gültige Auswahl für einen User in einer Gruppe, csv-Export Langvariante
    def test_matrix_long_csv_with_valid_selection(self):
        url = '{0}{1}'.format(reverse('uhr_matrix_csv'),
                              '?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "User_xv13254\tDjango-Team-01\txv13254, Dv13254\tSchwerpunkt\tVertretung\tNone\tNone\r\n", 1)
        self.assertContains(
            response, "Name\tTeams\tUserIDs\tErste Neue Rolle\tZweite Neue Rolle\tNPU-Rolle\tNPU-Grund\r\n", 1)

    # Eine gültige Auswahl für einen User in einer Gruppe, csv-Export kurzvariante
    def test_matrix_short_scv_with_valid_selection(self):
        url = '{0}{1}'.format(reverse('uhr_matrix_csv'),
                              'kompakt/?name=UseR&gruppe=BA-ps')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Name\tTeams\tUserIDs\tErste Neue Rolle\tZweite Neue Rolle\tNPU-Rolle\tNPU-Grund\r\n", 1)
        self.assertContains(
            response, "User_xv13254\tDjango-Team-01\txv13254, Dv13254\tS\tV\tNone\tNone\r\n", 1)


class ImportNewCSVSingleRecordTest(TestCase):
    # Tests für den Import neuer CSV-Listen und der zugehörigen Tabellen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        url = reverse('import')
        self.response = self.client.get(url)

        Tblrechteneuvonimport.objects.create(
            identitaet='xv13254',
            nachname='Bestertester',
            vorname='Fester',
            tf_name='supergeheime_TF',
            tf_beschreibung='Die Beschreibung der supergeheimen TF',
            af_anzeigename='rva_12345_geheime_AF',
            af_beschreibung='Beschreibung der Geheim-AF',
            hoechste_kritikalitaet_tf_in_af='k',
            tf_eigentuemer_org='ZI-AI-BA',
            tf_applikation='RUVDE',
            tf_kritikalitaet='u',
            gf_name='rvg_12345_geheime_AF',
            gf_beschreibung='Beschreibung der Geheim-GF',
            direct_connect=False,
            af_zugewiesen_an_account_name='av13254',
            af_gueltig_ab=timezone.now() - timedelta(days=364),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            af_zuweisungsdatum=timezone.now() - timedelta(days=366),
        )

    def test_importpage_table_entry(self):
        num = Tblrechteneuvonimport.objects.filter(vorname='Fester').count()
        self.assertEqual(num, 1)

    def test_importpage_view_status_code(self):
        url = reverse('import')
        response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_importpage_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_importpage_has_cuurent_comments_active(self):
        self.assertContains(self.response,
            'Gruppenzugehörigkeiten')


class SetupDatabase(TestCase):
    # Tests für den Import der Stored Procedures in die Datenbank
    def setUp(self):
        Anmeldung(self.client.login)

    def test_setup_database_view_status_code(self):
        url = reverse('stored_procedures')
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(
            self.response, 'Ansonsten: Finger weg, das bringt hier nichts!')
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class ImportNewIIQSingleRecordTest(TestCase):
    # Tests für den Import neuer CSV-Listen und der zugehörigen Tabellen
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        url = reverse('import')
        self.response = self.client.get(url)
        # Lösche alle Einträge in der Importtabelle
        Tblrechteneuvonimport.objects.all().delete()

        # Zunächst: Behandeln eines einzelnen Records
        Tblrechteneuvonimport.objects.create(
            identitaet='Test_xv13254',
            nachname='Bestertester',
            vorname='Fester',
            tf_name='supergeheime_TF',
            tf_beschreibung='Die Beschreibung der supergeheimen TF',
            af_anzeigename='rva_12345_geheime_AF',
            af_beschreibung='Beschreibung der Geheim-AF',
            hoechste_kritikalitaet_tf_in_af='k',
            tf_eigentuemer_org='ZI-AI-BA',
            tf_applikation='RUVDE',
            tf_kritikalitaet='u',
            gf_name='rvg_12345_geheime_AF',
            gf_beschreibung='Beschreibung der Geheim-GF',
            direct_connect=False,
            af_zugewiesen_an_account_name='Test_av13254',
            af_gueltig_ab=timezone.now() - timedelta(days=364),
            af_gueltig_bis=timezone.now() + timedelta(days=365),
            af_zuweisungsdatum=timezone.now() - timedelta(days=366),
        )

    def test_importpage_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_importpage_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    # hier wird nur ein einzelner Datensatz in die Importtabelle übernommen.
    # Im späteren Testverlauf wird die Tabelle wieder gelöscht.
    def test_importpage_table_entry(self):
        num = Tblrechteneuvonimport.objects.filter(vorname='Fester').count()
        self.assertEqual(num, 1)


class ImportNewIIQFilesNoInputTest(TestCase):
    # Und nun Test des Imports dreier Dateien.
    # Die erste Datei erstellt zwei User mit Rechten
    # Die zweite Datei fügt einen User hinzu, ändert einen zweiten und löscht einen dritten
    # Datei 3 löscht alle User und deren Rechte für die Organisation wieder.
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        url = reverse('import')
        self.response = self.client.post(url, {})

    def test_import_no_input_correct_page(self):
        self.assertContains(
            self.response, 'Auswahl der Organisation und Hochladen der Datei')

    def test_import_no_input_correct_following_page(self):
        # Wir landen wieder auf derselben Seite
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(
            self.response, 'Auswahl der Organisation und Hochladen der Datei')

    def test_import_no_input_form_error(self):
        # Es muss ein Formfehler erkannt werden
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


class ImportNewIIQFilesWrongInputTest(TestCase):
    # Und nun Test des Imports dreier Dateien.
    # Die erste Datei erstellt zwei User mit Rechten
    # Die zweite Datei fügt einen User hinzu, ändert einen zweiten und löscht einen dritten
    # Datei 3 löscht alle User und deren Rechte für die Organisation wieder.
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        data = {
            'organisation': 'foo blabla',
        }
        url = reverse('import')
        self.response = self.client.post(url, data)

    def test_import_wrong_input_correct_page(self):
        self.assertContains(
            self.response, 'Auswahl der Organisation und Hochladen der Datei')

    def test_import_wrong_input_correct_following_page(self):
        # Wir landen wieder auf derselben Seite
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(
            self.response, 'Auswahl der Organisation und Hochladen der Datei')

    def test_import_wrong_input_form_error(self):
        # Es muss ein Formfehler erkannt werden
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


class ImportHelperFunctionsTest(TestCase):
    def test_import_datum_konverter(self):
        datum = patch_datum('07.03.2019')
        self.assertEqual(datum, '2019-03-07 00:00+0100')

    def test_import_datum_konverter_leereingabe(self):
        datum = patch_datum('')
        self.assertEqual(datum, None)

    def test_import_neuer_import(self):
        # Neuer Aufruf sollte keinen Fehler liefern
        (flag, imp) = neuer_import(None, 'AI-BA')
        self.assertFalse(flag)


class NeuAFGFTest(TestCase):
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )
        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        # Drei User: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        # Die nächsten Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester',
            modelliert=timezone.now()
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo2 in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo2 in tblÜbersichtAFGF",
            name_af_neu="AF-foo2 in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        # Eine der AFen ist bekannt - aber das sollte egal sein.
        TblAfliste.objects.create(
            af_name='AF-foo in tblÜbersichtAFGF',
            neu_ab=timezone.now(),
        )

        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Es werden in der Tabelle die vier Rechte vergeben, eines davon gelöscht
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='AF-foo in tblÜbersichtAFGF',
            af_beschreibung='Die geniale AF-Beschreibung',
            gf='GF-foo in tblÜbersichtAFGF',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            datum=timezone.now(),
            geloescht=False,
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='dv13254'),
            tf='foo-TF2',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='AF-foo in tblÜbersichtAFGF',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            gf='GF-foo2 in tblÜbersichtAFGF',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            datum=timezone.now(),
            geloescht=False,
        )

        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av13254'),
            tf='foo-TF3',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            gf='GF-foo2 in tblÜbersichtAFGF',
            enthalten_in_af='AF-foo2 in tblÜbersichtAFGF',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='AF-foo-gelöscht in tblÜbersichtAFGF',
            af_beschreibung='Die 4. geniale AF-Beschreibung',
            gf='GF-foo-gelöscht in tblÜbersichtAFGF',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Eine leere Auswahl
    def test_NeuAFGF_suche(self):
        url = reverse('zeige_neue_afgf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SetzeNPURollen(TestCase):
    # Nur check, ob die Seite da ist
    def test_SetzeNPURollen_seite(self):
        url = reverse('setze_NPU_rollen')
        response = self.client.get(url)
        if response.status_code != 200 and response.status_code != 302:
            self.assertEqual(response.status_code, 200)


"""
Die Dinger hier gehen wieder nicht, weil die SPs nicht geladen sind
class ListenTest(TestCase):

    def test_ungenutzteTeams(self):
        url = reverse('ungenutzteTeams')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(self.response, 'Ungenutzte Teams', 2)
        self.assertContains(self.response,
                            'Auflistung definierter AF-GF-Kombinationen, die keinem User zugeordnet sind')
        self.assertContains(self.response,
                            'Betrachtet werden sowohl die aktiven als auch die historisierten Berechtigungen')


    def test_ungenutzteAFGF(self):
        url = reverse('ungenutzte_afgf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(self.response, 'Ungenutzte AFGF-Kombinationen', 2)
        self.assertContains(self.response,
                            'Auflistung definierter AF-GF-Kombinationen, die keinem User zugeordnet sind')
        self.assertContains(self.response,
                            'Betrachtet werden sowohl die aktiven als auch die historisierten Berechtigungen')

"""


class MussKannTest(TestCase):
    # Test der Seite für die Ermittlung der Muss-/Kann-Rechte
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblOrga.objects.create(
            team='Django-Team-02',
            themeneigentuemer='Ihmchen_02',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst_nicht_zugewiesen',
            neu_ab=timezone.now(),
        )

        # Drei UserIDen für eine Identität: XV und DV aktiv, AV gelöscht
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )
        TblUserIDundName.objects.create(
            userid='av13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=True,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv
        TblUserIDundName.objects.create(
            userid='xv00042',
            name='User_xv00042',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Eine UserID für eine weitere Identität: XV aktiv: Für diesen User gibt es noch keine eingetragene Rolle
        TblUserIDundName.objects.create(
            userid='xv00023',
            name='User_xv00023',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-LS',
        )

        # Zwei Rollen, die auf den ersten XV-User vergeben werden, die zweite wird auch dem m2. User vergeben
        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )
        TblRollen.objects.create(
            rollenname='Zweite Neue Rolle',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Drei AF-Zuordnungen zu Rollen
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(
                af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Auch irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
        )

        # User 12354_ Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Zweite Neue Rolle'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist auch eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Dem zweiten User 00042 wird nur eine Rolle zugeordnet
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv00042'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-LS',
            letzte_aenderung=timezone.now(),
        )
        # Und dem dritten User 00023 keine Rolle

        # Die nächsten beiden Objekte werden für tblGesamt als ForeignKey benötigt
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo in tblÜbersichtAFGF",
            name_af_neu="AF-foo in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="GF-foo-gelöscht in tblÜbersichtAFGF",
            name_af_neu="AF-foo-gelöscht in tblÜbersichtAFGF",
            zielperson='Fester BesterTester'
        )
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

        # Getestet werden soll die Möglichkeit,
        # für einen bestimmten User festzustellen, ob er über eine definierte AF verfügt
        # und diese auch auf aktiv gesetzt ist
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv00042'),
            tf='foo-TF',
            tf_beschreibung='TF-Beschreibung für foo-TF',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Auch eine geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now(),
            geloescht=False,
        )

        # und hier noch ein bereits gelöschtes Recht auf TF-Ebene.
        # ToDo Noch eine komplette AF mit allen GFs als gelöscht markiert vorbereiten
        # ToDo Noch eine komplette AF mit GF und TFD in anderer Rolle vorbereiten
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='foo-TF-gelöscht',
            tf_beschreibung='TF-Beschreibung für foo-TF-gelöscht',
            enthalten_in_af='rva_01219_beta91_job_abst',
            af_beschreibung='Die dritte geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(
                name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(
                tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Ist die Seite da?
    def test_panel_01_view_status_code(self):
        url = reverse('muss_kann_liste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Abschicken ohne Eintrag im Eingabefeld führt zur Infozeile
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, 'Bitte geben Sie das Orgasymbol an, für das die Liste erzeugt werden soll')

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Bitte geben Sie das Orgasymbol an, für das die Liste erzeugt werden soll')

    # Gibt es den Hilfetext?

    def test_panel_01_view_info_line(self):
        url = reverse('muss_kann_liste')
        # Erst mal wird der Hilfetext nicht angezeit
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, 'Bitte geben Sie das Orgasymbol an, für das die Liste erzeugt werden soll')

        # Abschicken ohne Eintrag im Eingabefeld führt zur Infozeile
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Bitte geben Sie das Orgasymbol an, für das die Liste erzeugt werden soll')

    # Angabe nicht vorhandener Gruppierung fürht zu leerer Ausgabe
    """
    # Für POST benötigt man ein CSRF-Token, das steht in irgend einem Cookie, in Verbindung mit der Session ID
    # Dehalb geht der Test hier immer schief:

    def test_panel_01_view_empty_result(self):
        url = reverse('muss_kann_liste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Abschicken mit nicht existentem Eintrag im Eingabefeld sollte zu leerer Treffermenge führen
        response = self.client.post(url, {
            'orgasymbol': 'gibt-es-nicht',
        })
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url)
        schoen(response)
    """
