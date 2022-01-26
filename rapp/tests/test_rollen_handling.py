from datetime import timedelta

from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from ..anmeldung import Anmeldung
from ..models import TblOrga
from ..models import TblUebersichtAfGfs
from ..models import TblUserIDundName
from ..models import TblPlattform
from ..models import TblGesamt
from ..models import TblAfliste
from ..models import TblUserhatrolle
from ..models import TblRollehataf
from ..models import TblRollen
from .test_views import SetupDatabase


class RollenUmbenennenTests(TestCase):
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
            af=TblAfliste.objects.get(af_name='rva_01219_beta91_job_abst_nicht_zugewiesen'),
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
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
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
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    def test_panel_status_code(self):
        url = reverse('rolle_umbenennen')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)

    def test_no_params(self):
        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {'alter_name': '', 'neuer_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertContains(response, "Bitte geben Sie den bestehenden Rollennamen an", 1)
        self.assertContains(response, "Bitte geben Sie den zukünftigen Rollennamen an", 1)

    def test_no_first_correct_second_param(self):
        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {'alter_name': '', 'neuer_name': 'Rolle gibt es noch nicht'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertContains(response, "Bitte geben Sie den bestehenden Rollennamen an", 1)
        self.assertNotContains(response, "Bitte geben Sie den zukünftigen Rollennamen an")

    def test_correct_first_no_second_param(self):
        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {
            'alter_name': 'Erste Neue Rolle',
            'neuer_name': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertNotContains(response, "Bitte geben Sie den bestehenden Rollennamen an")
        self.assertContains(response, "Bitte geben Sie den zukünftigen Rollennamen an", 1)

    def test_wrong_first_correct_second_param(self):
        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {
            'alter_name': 'FALSCH Erste Neue Rolle',
            'neuer_name': 'Rolle gibt es noch nicht'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertNotContains(response, "Bitte geben Sie den bestehenden Rollennamen an")
        self.assertNotContains(response, "Bitte geben Sie den zukünftigen Rollennamen an")

        self.assertContains(response, "Der bestehende Rollenname &#x27;FALSCH Erste Neue Rolle&#x27; existiert nicht.", 1)
        self.assertNotContains(response,
                               "Der bestehende Rollenname &#x27;Rolle gibt es noch nicht&#x27; existiert nicht.")
        self.assertNotContains(response, "Der neue Rollenname &#x27;Zweite Neue Rolle&#x27; existiert bereits.")

    def test_wrong_first_wrong_second_param(self):
        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {
            'alter_name': 'FALSCH Erste Neue Rolle',
            'neuer_name': 'Zweite Neue Rolle'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertNotContains(response, "Bitte geben Sie den bestehenden Rollennamen an")
        self.assertNotContains(response, "Bitte geben Sie den zukünftigen Rollennamen an")

        self.assertContains(response, "Der bestehende Rollenname &#x27;FALSCH Erste Neue Rolle&#x27; existiert nicht.", 1)
        self.assertContains(response, "Der neue Rollenname &#x27;Zweite Neue Rolle&#x27; existiert bereits.", 1)

    """
    # Das geht hier alles noch nicht, weil die Stored Procedures nicht geladen sind.
    # Deshalb werden die Tabellen nach dem fehlerhaften Aufruf der SP nicht wieder aufgeräumt
    # und es gibt jede Menge Folgefehler.
    def test_correct_first_correct_second_param(self):
        erg = anzahl_procs()
        self.assertEqual(erg, 13)

        url = reverse('rolle_umbenennen')
        response = self.client.post(url, {
            'alter_name': 'Erste Neue Rolle',
            'neuer_name': 'Ganz neue Rolle'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bestehender Rollenname:", 1)
        self.assertContains(response, "Zukünftiger Rollenname:", 1)
        self.assertContains(response, "Submit", 1)
        self.assertContains(response, "Abbrechen", 1)
        self.assertNotContains(response, "Bitte geben Sie den bestehenden Rollennamen an")
        self.assertNotContains(response, "Bitte geben Sie den zukünftigen Rollennamen an")

        self.assertNotContains(response, "Der bestehende Rollenname &#39;FALSCH Erste Neue Rolle&#39; existiert nicht.")
        self.assertNotContains(response, "Der neue Rollenname &#39;Zweite Neue Rolle&#39; existiert bereits.")

        self.assertContains(response, "Prozedur ausgeführt", 1)
        self.assertContains(response, "Habe folgende Umbenennung durchgeführt", 1)
    """

""" Auch hier ist die SP noch nicht initialisiert - warum auch immer

class UngenutzteTeamsTests(TestCase):
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
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
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
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="GF-foo in tblÜbersichtAFGF"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='GF-foo',
            datum=timezone.now() - timedelta(days=365),
            geloescht=True,
        )

    # Ist die Seite da?
    def test_panel_status_code(self):
        url = reverse('ungenutzteTeams')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ungenutzte Teams", 4)
"""


class UngenutzteRollenTests(TestCase):
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

        TblRollen.objects.create(
            rollenname='Diese eine ungenutzte Rolle soll gefunden werden',
            system='Irgendein System',
            rollenbeschreibung='Das ist auch eine Testrolle',
        )

        # Dem XV-User werden zwei Rollen zugewiesen, dem AV- und DV-User keine
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Erste Neue Rolle'),
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

    def test_panel_status_code(self):
        url = reverse('ungenutzte_rollen')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Anzahl Rollen gesamt: 3, Anzahl genutzte Rollen: 2, Anzahl ungenutzter Rollen: 1", 1)
        self.assertContains(response, "Diese eine ungenutzte Rolle soll gefunden werden", 1)
