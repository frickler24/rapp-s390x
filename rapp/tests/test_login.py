from django.urls import reverse, resolve
from django.test import TestCase
from ..anmeldung import Anmeldung

from ..models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
    TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen

from datetime import datetime, timedelta
from django.utils import timezone

from ..tests.test_views import SetupDatabase


# Ist das Login.-Panel verfügbar?
class LoginTests(TestCase):
    def setUp(self):
        url = reverse('login')
        self.response = self.client.get(url)

    def test_login_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

# Werden alle Seiten abgewiesen außer der Hauptseite, wenn kein User angemeldet ist?


class LoginRequiredGesamtTests(TestCase):
    def setUp(self):
        self.url = reverse('gesamtliste')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredGesamtDetailTests(TestCase):
    def setUp(self):
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

        self.url = reverse('gesamt-detail',
                           kwargs={'pk': TblGesamt.objects.get(tf='Die superlange schnuckelige TF2').id})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserlisteTests(TestCase):
    def setUp(self):
        self.url = reverse('userliste')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserlisteTests(TestCase):
    def setUp(self):
        self.url = reverse('userliste')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserCreateTests(TestCase):
    def setUp(self):
        self.url = reverse('user-create')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserUpdateTests(TestCase):
    def setUp(self):
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
        self.url = reverse('user-update', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserDeleteTests(TestCase):
    def setUp(self):
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
        self.url = reverse('user-delete', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUserToggleGeloeschtTests(TestCase):
    def setUp(self):
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
        self.url = reverse('user-toggle-geloescht', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredTeamlisteTests(TestCase):
    def setUp(self):
        self.url = reverse('teamliste')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredTeamCreateTests(TestCase):
    def setUp(self):
        self.url = reverse('team-create')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredTeamUpdateTests(TestCase):
    def setUp(self):
        TblOrga.objects.create(team='MeinTeam', themeneigentuemer='Icke')
        self.url = reverse('team-update', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredTeamDeleteTests(TestCase):
    def setUp(self):
        TblOrga.objects.create(team='MeinTeam', themeneigentuemer='Icke')
        self.url = reverse('team-delete', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredSuchPanelTests(TestCase):
    def setUp(self):
        self.url = reverse('panel')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUhRPanelTests(TestCase):
    def setUp(self):
        self.url = reverse('user_rolle_af')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUhRCreateTests(TestCase):
    def setUp(self):
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )

        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )

        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),

        )

        # Die nächsten beiden Objekte werden wür tblGesamt als ForeignKey benötigt
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
        self.url = reverse('user_rolle_af-create',
                           kwargs={'userid': 'xv13254'})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUhRDeleteTests(TestCase):
    def setUp(self):
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )

        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )

        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),

        )

        # Die nächsten beiden Objekte werden wür tblGesamt als ForeignKey benötigt
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
        self.url = reverse('user_rolle_af-delete', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredUhRUpdateTests(TestCase):
    def setUp(self):
        TblOrga.objects.create(
            team='Django-Team-01',
            themeneigentuemer='Ihmchen_01',
        )

        TblAfliste.objects.create(
            af_name='rva_01219_beta91_job_abst',
            neu_ab=timezone.now(),
        )

        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='Django-Team-01'),
            zi_organisation='AI-BA',
            geloescht=False,
            abteilung='ZI-AI-BA',
            gruppe='ZI-AI-BA-PS',
        )

        TblRollen.objects.create(
            rollenname='Erste Neue Rolle',
            system='Testsystem',
            rollenbeschreibung='Das ist eine Testrolle',
        )

        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
        )

        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.first(),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist eine Testrolle für ZI-AI-BA-PS',
            letzte_aenderung=timezone.now(),

        )

        # Die nächsten beiden Objekte werden wür tblGesamt als ForeignKey benötigt
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
        self.url = reverse('user_rolle_af_parm', kwargs={'id': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredImportTests(TestCase):
    def setUp(self):
        self.url = reverse('import')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredImport2Tests(TestCase):
    def setUp(self):
        self.url = reverse('import2')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredImport2QTests(TestCase):
    def setUp(self):
        self.url = reverse('import2_quittung')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredImport3QTests(TestCase):
    def setUp(self):
        self.url = reverse('import3_quittung')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))


class LoginRequiredImportStatusTests(TestCase):
    def setUp(self):
        self.url = reverse('import_status')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(
            login_url=login_url, url=self.url))

# Dies ist der erste Test zum Aufruf einer Login-gebundenen Seite nach erfolgreichem Login


class LoginRequiredAndExistingGesamtTests(TestCase):
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()
        self.url = reverse('gesamtliste')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertEqual(self.response.status_code, 200)
