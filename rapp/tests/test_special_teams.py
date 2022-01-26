# from django.core.files.base import ContentFile
import re

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..anmeldung import Anmeldung
from ..models import TblOrga, TblUebersichtAfGfs, TblUserIDundName, TblPlattform, TblGesamt, \
    TblAfliste, TblUserhatrolle, TblRollehataf, TblRollen
from ..tests.test_views import SetupDatabase


def schoen(s):
    print(str(s).replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t'))


class SpecialTeamTests(TestCase):
    def setUp(self):
        Anmeldung(self.client.login)
        SetupDatabase()

        # Die Teams: Es gibt 3 normale Teams,
        TblOrga.objects.create(team='KleinTeam A', themeneigentuemer='Icke')
        TblOrga.objects.create(team='KleinTeam B', themeneigentuemer='Icke')
        TblOrga.objects.create(team='KleinTeam C', themeneigentuemer='Icke')

        #  zwei mit angegebener Teammliste
        TblOrga.objects.create(team='GrossTeam 1', themeneigentuemer='Icke', teamliste="KleinTeam A,KleinTeam B")
        TblOrga.objects.create(team='GrossTeam 2', themeneigentuemer='Blubb', teamliste="KleinTeam B,KleinTeam C")

        # und ein freies Team. Füra da benötigen wir drei fixe User User_xv13254, User_98765 und User44444
        TblOrga.objects.create(team='SpecTeam X', themeneigentuemer='Blubb',
                               freies_team="User_xv13254:komplett|User_98765:SpecTeam X|User44444:SpecTeam X")

        """
        Insgesamt legen wir die folgenden User an
        User          XV  AV  BV  CV  DV  gelöscht    Team    Gruppe      AF1 AF2 DF3 AF4 AF5     R1  R2  R3
        User_xv13254  x               x               A       AB-CD-XY-01 x   x   x               S
        User_xv98765  x   x                           B       AB-CD-XY-01 x       -   x           S   V
        User_xv44444  x       x       x               C       AB-CD-XY-01 x   x   x   x               S
        User_xv55555  x   x   x   x                   A       AB-CD-XY-01 x               x               S
        User_xv66666  x               x               B       AB-CD-XY-02 x   x   x   x   x       S   V   V
        User_xv77777  x   x   x   x   x   x           C       AB-CD-XY-01 x       x                       S
        
        DF3 ist eine AF nur für DV-User
        
        Anzahl TFen je AF
                TF1 TF2 TF3 TF4 TF5 TF6
        AF1 3   x   x       x
        AF2 3               x   x   x
        DF3 1           x
        AF4 4       x       x   x
        AF5 5   x   x       x   x   x
       
        
        Rolle   AF1 AF2 AF3 AF4 AF5
        R1      x   x   x
        R2                  x   x
        R3      x

        """
        self.createUser()
        self.createAF()
        self.createRoles()
        self.createRolleHatAF()
        self.createUserHatRolle()
        self.createPlattform()
        self.createTFs()

    def createTFs(self):
        # 1. User
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='dv13254'),
            tf='TF3',
            tf_beschreibung='TF-Beschreibung für TF3',
            enthalten_in_af='Sollte die rvz_09876_df3 sein',
            af_beschreibung='Die geniale AF-Beschreibung nur für DV-User',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_09876_df3"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_09876_df3',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv13254'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )

        # 2. User
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv98765'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung nur für DV-User',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv98765'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv98765'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av98765'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av98765'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av98765'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )

        # 3. User
        # xv, AF1 = TF 1,2,4
        # xv, AF2 = TF 4,5,6
        # xv, AF4 = TF 2,4,5
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF2:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF4:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv44444'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # bv, AF2 = TF 4,5,6
        # AF2:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv44444'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv44444'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv44444'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        # dv, AF3 = TF 3
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='dv44444'),
            tf='TF3',
            tf_beschreibung='TF-Beschreibung für TF3',
            enthalten_in_af='Sollte die rvz_09876_df3 sein',
            af_beschreibung='Die geniale AF-Beschreibung nur für DV-User',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_09876_df3"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_09876_df3',
            datum=timezone.now(),
            geloescht=False,
        )

        # 4. User
        # xv, AF1 = TF 1,2,4
        # xv, AF5 = TF 1,2,4,5,6
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF5:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv55555'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        # av, AF1 = TF 1,2,4
        # av, AF5 = TF 1,2,4,5,6
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF5:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='av55555'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        # bv, AF1 = TF 1,2,4
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='bv55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # cv, AF5 = TF 1,2,4,5,6
        # AF5:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='cv55555'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='cv55555'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='cv55555'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='cv55555'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='cv55555'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )

        # 5. User
        # xv, AF1 = TF 1,2,4
        # xv, AF2 = TF 4,5,6
        # xv, AF4 = TF 2,4,5
        # xv, AF5 = TF 1,2,4,5,6
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF2:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF4:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=False,
        )
        # AF5:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv66666'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=False,
        )
        # dv, AF3 = TF 3
        # AF3:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='dv66666'),
            tf='TF3',
            tf_beschreibung='TF-Beschreibung für TF3',
            enthalten_in_af='Sollte die rvz_09876_df3 sein',
            af_beschreibung='Die geniale AF-Beschreibung nur für DV-User',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_09876_df3"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_09876_df3',
            datum=timezone.now(),
            geloescht=False,
        )

        # 6. User (Alle Rechte auf gelöscht setzen!!)
        # xv, AF1 = TF 1,2,4
        # AF 1:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af1"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af1',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af1 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=True,
        )
        # av, AF2 = TF 4,5,6
        # AF2:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af2 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af2"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af2',
            datum=timezone.now(),
            geloescht=True,
        )
        # bv, AF4 = TF 2,4,5
        # AF4:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_77777_af4 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_77777_af4"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_77777_af4',
            datum=timezone.now(),
            geloescht=True,
        )
        # cv, AF5 = TF 1,2,4,5,6
        # AF5:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF1',
            tf_beschreibung='TF-Beschreibung für TF1',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF2',
            tf_beschreibung='TF-Beschreibung für TF2',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF4',
            tf_beschreibung='TF-Beschreibung für TF4',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF5',
            tf_beschreibung='TF-Beschreibung für TF5',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=True,
        )
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='xv77777'),
            tf='TF6',
            tf_beschreibung='TF-Beschreibung für TF6',
            enthalten_in_af='Sollte die rva_01234_af5 sein',
            af_beschreibung='Die geniale AF-Beschreibung',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_01234_af5"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_01234_af5',
            datum=timezone.now(),
            geloescht=True,
        )
        # dv, AF3 = TF3
        # AF3:
        TblGesamt.objects.create(
            userid_name=TblUserIDundName.objects.get(userid='dv77777'),
            tf='TF3',
            tf_beschreibung='TF-Beschreibung für TF3',
            enthalten_in_af='Sollte die rvz_09876_df3 sein',
            af_beschreibung='Die geniale AF-Beschreibung nur für DV-User',
            modell=TblUebersichtAfGfs.objects.get(name_gf_neu="rvg_09876_df3"),
            plattform=TblPlattform.objects.get(tf_technische_plattform='Test-Plattform'),
            gf='rvg_09876_df3',
            datum=timezone.now(),
            geloescht=True,
        )

    def createPlattform(self):
        """
        Eine einzige Plattform reicht für unsere Zwecke hier aus
        :return:
        """
        TblPlattform.objects.create(
            tf_technische_plattform='Test-Plattform'
        )

    def createUserHatRolle(self):
        """
        s. Tabelle in Hauptmethode
        :return:
        """
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv13254'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist für Rolle R1',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv98765'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist für Rolle R1',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv98765'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R2'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist Rolle R2',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv44444'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R2'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist Rolle R2',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv55555'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R3'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist Rolle R3',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv66666'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist für Rolle R1',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv66666'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R2'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist Rolle R2',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv66666'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R3'),
            schwerpunkt_vertretung='Vertretung',
            bemerkung='Das ist Rolle R3',
            letzte_aenderung=timezone.now(),
        )
        TblUserhatrolle.objects.create(
            userid=TblUserIDundName.objects.get(userid='xv77777'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R3'),
            schwerpunkt_vertretung='Schwerpunkt',
            bemerkung='Das ist Rolle R3',
            letzte_aenderung=timezone.now(),
        )

    def createRolleHatAF(self):
        """
        s. Tabelle in Hauptmethode
        :return:
        """
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Irgend eine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01234_af1'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
        )
        TblRollehataf.objects.create(
            mussfeld=False,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung='Keine halbwegs sinnvolle Beschreibung',
            af=TblAfliste.objects.get(af_name='rva_01234_af2'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_NURDV,
            bemerkung=None,
            af=TblAfliste.objects.get(af_name='rvz_09876_df3'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R1'),
        )

        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_XABCV,
            bemerkung=None,
            af=TblAfliste.objects.get(af_name='rva_77777_af4'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R2'),
        )
        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_NURDV,
            bemerkung=None,
            af=TblAfliste.objects.get(af_name='rva_01234_af5'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R2'),
        )

        TblRollehataf.objects.create(
            mussfeld=True,
            einsatz=TblRollehataf.EINSATZ_NURDV,
            bemerkung=None,
            af=TblAfliste.objects.get(af_name='rvz_09876_df3'),
            rollenname=TblRollen.objects.get(rollenname='Rolle R3'),
        )

    def createRoles(self):
        """
        s. Tabelle in Hauptmethode
        :return:
        """
        TblRollen.objects.create(
            rollenname='Rolle R1',
            system='Testsystem',
            rollenbeschreibung='Das ist Testrolle R1',
        )
        TblRollen.objects.create(
            rollenname='Rolle R2',
            system='Blubbersystem',
            rollenbeschreibung='Das ist Testrolle R2',
        )
        TblRollen.objects.create(
            rollenname='Rolle R3',
            system='Bla-System',
            rollenbeschreibung='Das ist Testrolle R3',
        )

    def createAF(self):
        """
        s. Tabelle in Hauptmethode
        :return:
        """
        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01234_af1",
            name_af_neu="rva_01234_af1",
            zielperson='Fester BesterTester'
        )
        TblAfliste.objects.create(
            af_name='rva_01234_af1',
            neu_ab=timezone.now(),
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01234_af2",
            name_af_neu="rva_01234_af2",
            zielperson='Fester BesterTester'
        )
        TblAfliste.objects.create(
            af_name='rva_01234_af2',
            neu_ab=timezone.now(),
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_09876_df3",
            name_af_neu="rvz_09876_df3",
            zielperson='Fester BesterTester'
        )
        TblAfliste.objects.create(
            af_name='rvz_09876_df3',
            neu_ab=timezone.now(),
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_77777_af4",
            name_af_neu="rva_77777_af4",
            zielperson='Fester BesterTester'
        )
        TblAfliste.objects.create(
            af_name='rva_77777_af4',
            neu_ab=timezone.now(),
        )

        TblUebersichtAfGfs.objects.create(
            name_gf_neu="rvg_01234_af5",
            name_af_neu="rva_01234_af5",
            zielperson='Fester BesterTester'
        )
        TblAfliste.objects.create(
            af_name='rva_01234_af5',
            neu_ab=timezone.now(),
        )

    def createUser(self):
        """
        s. Tabelle in Hauptmethode
        :return:
        """
        TblUserIDundName.objects.create(
            userid='xv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='dv13254',
            name='User_xv13254',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='xv98765',
            name='User_xv98765',
            orga=TblOrga.objects.get(team='KleinTeam B'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='av98765',
            name='User_xv98765',
            orga=TblOrga.objects.get(team='KleinTeam B'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='xv44444',
            name='User_xv44444',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='bv44444',
            name='User_xv44444',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='dv44444',
            name='User_xv44444',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='xv55555',
            name='User_xv55555',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='av55555',
            name='User_xv55555',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='bv55555',
            name='User_xv55555',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='cv55555',
            name='User_xv55555',
            orga=TblOrga.objects.get(team='KleinTeam A'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='xv66666',
            name='User_xv66666',
            orga=TblOrga.objects.get(team='KleinTeam B'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-02',
        )
        TblUserIDundName.objects.create(
            userid='dv66666',
            name='User_xv66666',
            orga=TblOrga.objects.get(team='KleinTeam B'),
            zi_organisation='AB-CD',
            geloescht=False,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-02',
        )
        TblUserIDundName.objects.create(
            userid='xv77777',
            name='User_xv77777',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=True,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='av77777',
            name='User_xv77777',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=True,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='bv77777',
            name='User_xv77777',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=True,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='cv77777',
            name='User_xv77777',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=True,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )
        TblUserIDundName.objects.create(
            userid='dv77777',
            name='User_xv77777',
            orga=TblOrga.objects.get(team='KleinTeam C'),
            zi_organisation='AB-CD',
            geloescht=True,
            abteilung='AB-CD-XY',
            gruppe='AB-CD-XY-01',
        )

    def test_teamlist_view_content(self):
        url = reverse('teamliste')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'KleinTeam A', 2)
        self.assertContains(response, 'KleinTeam B', 3)
        self.assertContains(response, 'KleinTeam C', 2)
        self.assertContains(response, 'GrossTeam 1', 1)
        self.assertContains(response, 'GrossTeam 2', 1)

    def test_all_avaliable_A(self):
        id = TblOrga.objects.get(team='KleinTeam A').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'KleinTeam A', 1)
        self.assertContains(response, 'xv13254', 1)
        self.assertContains(response, 'xv55555', 1)
        self.assertNotContains(response, 'xv98765')
        self.assertNotContains(response, 'xv44444')
        self.assertNotContains(response, 'xv66666')
        self.assertNotContains(response, 'xv77777')

    def test_all_avaliable_B(self):
        id = TblOrga.objects.get(team='KleinTeam B').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'KleinTeam B', 1)
        self.assertNotContains(response, 'xv13254')
        self.assertNotContains(response, 'xv55555')
        self.assertContains(response, 'xv98765', 1)
        self.assertNotContains(response, 'xv44444')
        self.assertContains(response, 'xv66666', 1)
        self.assertNotContains(response, 'xv77777')

    def test_all_avaliable_C(self):
        id = TblOrga.objects.get(team='KleinTeam C').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'KleinTeam C', 1)
        self.assertNotContains(response, 'xv13254')
        self.assertNotContains(response, 'xv55555')
        self.assertNotContains(response, 'xv98765')
        self.assertContains(response, 'xv44444', 1)
        self.assertNotContains(response, 'xv66666')
        self.assertNotContains(response, 'xv77777')  # Sind alle gelöscht, auch der User!

    def test_all_avaliable_G1(self):
        id = TblOrga.objects.get(team='GrossTeam 1').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'GrossTeam 1', 1)
        self.assertContains(response, 'KleinTeam A', 1)
        self.assertContains(response, 'xv13254', 1)
        self.assertContains(response, 'xv55555', 1)
        self.assertContains(response, 'xv98765', 1)
        self.assertNotContains(response, 'xv44444')
        self.assertContains(response, 'xv66666', 1)
        self.assertNotContains(response, 'xv77777')

    def test_all_avaliable_G2(self):
        id = TblOrga.objects.get(team='GrossTeam 2').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'GrossTeam 2', 1)
        self.assertContains(response, 'KleinTeam B', 1)
        self.assertNotContains(response, 'xv13254')
        self.assertNotContains(response, 'xv55555')
        self.assertContains(response, 'xv98765', 1)
        self.assertContains(response, 'xv44444', 1)
        self.assertContains(response, 'xv66666', 1)
        self.assertNotContains(response, 'xv77777')

    def test_KinderSeidIhrAlleDa(self):
        url = '{0}{1}'.format(reverse('panel'), '?geloescht=unknown&userid_name__geloescht=unknown&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'xv13254', 13)
        self.assertContains(response, 'xv98765', 9)
        self.assertContains(response, 'xv44444', 22)
        self.assertContains(response, 'xv55555', 32)
        self.assertContains(response, 'xv66666', 29)
        self.assertContains(response, 'xv77777', 29)

    def test_matrix_G1(self):
        id = TblOrga.objects.get(team='GrossTeam 1').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'GrossTeam 1', 1)

        url = '{0}{1}{2}{3}'.format(reverse('uhr_matrix'), '?name=&orga=', id, '&pagesize=100')
        response = self.client.get(url)

        self.assertContains(response, 'GrossTeam 1', 1)
        self.assertContains(response, 'GrossTeam 2', 1)

        con = str(response.content).replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
        self.assertTrue(bool(re.search(
            '<thead>\s*<tr class="bg-primary text-left">\s*<th width="10%">Name</th>\s*<th width="10%">Teams</th>\s*<th width="10%">UserIDs</th>\s*<th><small>Rolle R1</small></th>\s*<th><small>Rolle R2</small></th>\s*<th><small>Rolle R3</small></th>\s*<th width="5%">NPU-Rolle</th>\s*<th width="10%">NPU-Grund</th>\s*</tr>\s*</thead>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv13254\s*</td>\s*<td>\s*<small>\s*KleinTeam A\s*</small>\s*</td>\s*<td>\s*<small>\s*xv13254,<br />\s*</small>\s*<small>\s*dv13254\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv55555\s*</td>\s*<td>\s*<small>\s*KleinTeam A\s*</small>\s*</td>\s*<td>\s*<small>\s*xv55555,<br />\s*</small>\s*<small>\s*cv55555,<br />\s*</small>\s*<small>\s*bv55555,<br />\s*</small>\s*<small>\s*av55555\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv66666\s*</td>\s*<td>\s*<small>\s*KleinTeam B\s*</small>\s*</td>\s*<td>\s*<small>\s*xv66666,<br />\s*</small>\s*<small>\s*dv66666\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv98765\s*</td>\s*<td>\s*<small>\s*KleinTeam B\s*</small>\s*</td>\s*<td>\s*<small>\s*xv98765,<br />\s*</small>\s*<small>\s*av98765\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )

    def test_matrix_G2(self):
        id = TblOrga.objects.get(team='GrossTeam 2').id
        url = '{0}{1}{2}{3}'.format(reverse('user_rolle_af'), '?name=&orga=', id, '&gruppe=&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'GrossTeam 2', 1)

        url = '{0}{1}{2}{3}'.format(reverse('uhr_matrix'), '?name=&orga=', id, '&pagesize=100')
        response = self.client.get(url)
        self.assertContains(response, 'GrossTeam 1', 1)
        self.assertContains(response, 'GrossTeam 2', 1)

        con = str(response.content).replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
        # schoen(response.content)

        self.assertTrue(bool(re.search(
            '<thead>\s*<tr class="bg-primary text-left">\s*<th width="10%">Name</th>\s*<th width="10%">Teams</th>\s*<th width="10%">UserIDs</th>\s*<th><small>Rolle R1</small></th>\s*<th><small>Rolle R2</small></th>\s*<th><small>Rolle R3</small></th>\s*<th width="5%">NPU-Rolle</th>\s*<th width="10%">NPU-Grund</th>\s*</tr>\s*</thead>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )

        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv44444\s*</td>\s*<td>\s*<small>\s*KleinTeam C\s*</small>\s*</td>\s*<td>\s*<small>\s*xv44444,<br />\s*</small>\s*<small>\s*dv44444,<br />\s*</small>\s*<small>\s*bv44444\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv66666\s*</td>\s*<td>\s*<small>\s*KleinTeam B\s*</small>\s*</td>\s*<td>\s*<small>\s*xv66666,<br />\s*</small>\s*<small>\s*dv66666\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
        self.assertTrue(bool(re.search(
            '<tr>\s*<td>\s*User_xv98765\s*</td>\s*<td>\s*<small>\s*KleinTeam B\s*</small>\s*</td>\s*<td>\s*<small>\s*xv98765,<br />\s*</small>\s*<small>\s*av98765\s*</small>\s*</td>\s*<td>\s*<small>\s*Schwerpunkt\s*</small>\s*</td>\s*<td>\s*<small>\s*Vertretung\s*</small>\s*</td>\s*<td>\s*<small>\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*<td>\s*<small>\s*None,<br />\s*</small>\s*<small>\s*None\s*</small>\s*</td>\s*</tr>',
            con,
            re.MULTILINE | re.IGNORECASE | re.UNICODE)
        )
        )
