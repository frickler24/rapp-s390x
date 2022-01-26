# -*- coding: utf-8 -*-
"""
Dieses Modul enthält alle mysql-Stored Procedures,
die Funktion zum Speichern der SPs,
eine zum Testen auf Vorhandensein spezifischer SPs
und der korrekten Anzahl im mysql
"""
from __future__ import unicode_literals

import sys

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import render


# noinspection PyBroadException
def check_sp(name):
    """
    Prüfe, ob die Stored Procedure <name> in der DB installiert ist
    :param name: Der Name der zu prüfenden Stored Procedure
    :return: '' im Erfolgsfall, sonst eine Fehlermeldung
    """
    sp = """
    SELECT routine_name
    FROM information_schema.routines
    WHERE routine_type = 'PROCEDURE'
        AND routine_name = '{}'
    """.format(
        name
    )

    fehler = ""
    with connection.cursor() as cursor:
        try:
            cursor.execute("select DATABASE()")
            routine_schema = cursor.fetchone()
            sp = "{} AND routine_schema = '{}'".format(sp, routine_schema[0])
            anzahl = cursor.execute(sp)

            if anzahl != 1:
                fehler += "Mismatch SQL-Answer in check_sp: 1 != {}".format(
                    anzahl)
        except:
            e = sys.exc_info()[0]
            fehler = "Details: {}".format(e)

        cursor.close()

        if fehler != "":
            fehler = "Error in check_sp(): {}".format(fehler)
            print(fehler)
        return fehler


# noinspection PyBroadException
def push_sp(name, sp, procs_schon_geladen):
    """
    Speichere eine als Parameter übergebene Stored Procedure

    :param name: Name der zu löschenden Stored_Procedure
    :param sp: Die Stored Procedure, die gespeichert werden soll (SQL-Mengen-String)
    :param procs_schon_geladen: Löschen muss nur erfolgen, wenn die SP gbereits geladen ist.
                                Das wird hiermit angezeigt.
    :return: Fehler (False = kein Fehler)
    """
    # ToDo Das Löschen wirft Warnings im MySQL-Treiber, wenn die SP gar nicht existiert.
    # -> Liste lesen und checken
    fehler = ""
    loeschstring = "DROP PROCEDURE IF EXISTS {}".format(name)
    with connection.cursor() as cursor:
        try:
            if procs_schon_geladen:
                cursor.execute(loeschstring)
            cursor.execute(sp)
        except:
            e = sys.exc_info()[0]
            fehler = "Error in push_sp(): {}".format(e)

        cursor.close()
        return fehler + check_sp(name)


def push_sp_anzahl_import_elemente(procs_schon_geladen):
    """
    Erzeuge die SP 'anzahl_import_elemente',
    die die Menge der Tabelle `tblRechteNeuVonImport` ermittelt
    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE anzahl_import_elemente()
        BEGIN
          SELECT COUNT(*) FROM `tblRechteNeuVonImport`;
        END
    """
    return push_sp("anzahl_import_elemente", sp, procs_schon_geladen)


# noinspection PyBroadException
def call_sp_test():
    """
    Prüfe, ob Stored Procedures installiert sind mit Hilfe der SP "anzahl_import_elemente"
    Wenn die SP installiert ist und einen Wert >0 zurückliefert, sind die ersten Hürden genommen.

    :return: Anzahl der Elemente in `tblRechteNeuVonImport` oder Fehlercode
    """
    fehler = False
    with connection.cursor() as cursor:
        try:
            cursor.execute("CALL anzahl_import_elemente")
            liste = cursor.fetchone()
        except:
            e = sys.exc_info()[0]
            fehler = "Error: {}".format(e)

        cursor.close()
        return fehler or not liste[0] >= 0


def push_sp_vorbereitung(procs_schon_geladen):
    """
    Erzeuge Stored Procedure "vorbereitung"; Das ist der erste Schritt beim Import von IIQ-Daten

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
      create procedure vorbereitung()
      BEGIN
          /*
              Die Daten werden zunächst in eine Hilfstabelle tblRechteNeuVonImport eingelesen
              und dann von dort in die vorher geleerte tblRechteAMNeu kopiert.
              tblRechteAMNeu ist ab dann die Arbeitsdatei für alle weiteren Vorgänge,
              die Hilfsdatei wird nicht mehr benutzt.

              Dieser Zwischenschritt war früher erforderlich,
              weil der gespeicherte Import die Tabelle komplett geloescht hat
              (also eine DROP - CREATE - Sequenz durchlief),
              damit waren die Datentypangaben und Referenzen futsch.
              Heute wird er nur noch genutzt, um die doppelt vorhandenen Zeilen zu entfernen
              und dynamische Werte zu erzeugen.
          */

          /*
              Seit IIQ werden die wirklichen UserIDen nicht mehr unter der Identität gehalten,
              sondern unter `AF zugewiesen an Account-name`. Das müssen wir in die userid
              umkopieren, wo nötig.
          */
          UPDATE tblRechteNeuVonImport
              SET `AF zugewiesen an Account-name` = `Identität`
          WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-name` Is Null
              Or tblRechteNeuVonImport.`AF zugewiesen an Account-name` = "";

          /*
              Da hat es wohl mal andere Konventionen bei Unix mit useriden gegeben:
              Technische User wurden mit anderen useriden angelegt, als XV86-er Nummern.
              Das wird hier gepatcht. Ist eigentlich nicht ganz korrekt,
              soll uns aber erst mal jemand nachweisen.
          */

          UPDATE tblRechteNeuVonImport
              SET tblRechteNeuVonImport.`AF zugewiesen an Account-name` = `Identität`
          WHERE tblRechteNeuVonImport.`Identität` Like 'xv86%'
              AND tblRechteNeuVonImport.`AF zugewiesen an Account-name` Not Like 'xv86%';

          /*
              zum Nachschauen

          select `Identität`, `AF zugewiesen an Account-name` from tblRechteNeuVonImport
          WHERE tblRechteNeuVonImport.`AF zugewiesen an Account-name` Not Like 'xv86%'
              AND `tblRechteNeuVonImport`.`Identität` Like 'xv86%';
          */

          /*
              Löschen und Füllen der eigentlichen Importtabelle
              Einschließlich Herausfiltern der doppelten Zeilen
              (> 1% der Zeilen werden aus IIQ doppelt geliefert)
          */
          drop table if exists rapp_NeuVonImportDuplikatfrei;
          create temporary table rapp_NeuVonImportDuplikatfrei as
              SELECT `AF zugewiesen an Account-name`   AS userid,
                     CONCAT(`Nachname`,', ',`Vorname`) AS name,
                     `tf name`                         AS tf,
                     `tf beschreibung`                 AS tf_beschreibung,
                     `AF Anzeigename`                  AS enthalten_in_af,
                     `AF Beschreibung`                 AS af_beschreibung,
                     `tf kritikalität`                 AS tf_kritikalitaet,
                     `tf eigentümer org`               AS tf_eigentuemer_org,
                     `tf Applikation`                  AS tf_technische_plattform,
                     `GF name`                         AS GF,
                     `af gültig ab`                    AS af_gueltig_ab,
                     `af gültig bis`                   AS af_gueltig_bis,
                     `direct connect`                  AS direct_connect,
                     `höchste kritikalität tf in af`   AS hk_tf_in_af,
                     `gf beschreibung`                 AS gf_beschreibung,
                     `af zuweisungsdatum`              AS af_zuweisungsdatum,
                     `npu_rolle`,
                     `npu_grund`,
                     `iiq_organisation`
              FROM tblRechteNeuVonImport
              GROUP BY `userid`,
                       `tf`,
                       `enthalten_in_af`,
                       `tf_technische_plattform`,
                       `GF`,
                       iiq_organisation;

          /*
              Umkopieren der Daten von einer Tabelle in die andere
          */

          TRUNCATE table tblRechteAMNeu;
          INSERT INTO tblRechteAMNeu (userid, name, tf, `tf_beschreibung`,
                      `enthalten_in_af`, `af_beschreibung`,
                      `tf_kritikalitaet`,
                      `tf_eigentuemer_org`, `tf_technische_plattform`, GF,
                      `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`, `hk_tf_in_af`,
                      `gf_beschreibung`, `af_zuweisungsdatum`,
                      `npu_rolle`, `npu_grund`, `iiq_organisation`,
                      doppelerkennung)
          SELECT rapp_NeuVonImportDuplikatfrei.userid,
                 rapp_NeuVonImportDuplikatfrei.name,
                 rapp_NeuVonImportDuplikatfrei.tf,
                 rapp_NeuVonImportDuplikatfrei.`tf_beschreibung`,
                 rapp_NeuVonImportDuplikatfrei.`enthalten_in_af`,
                 rapp_NeuVonImportDuplikatfrei.`af_beschreibung`,
                 rapp_NeuVonImportDuplikatfrei.`tf_kritikalitaet`,
                 rapp_NeuVonImportDuplikatfrei.`tf_eigentuemer_org`,
                 rapp_NeuVonImportDuplikatfrei.`tf_technische_plattform`,
                 rapp_NeuVonImportDuplikatfrei.GF,
                 rapp_NeuVonImportDuplikatfrei.`af_gueltig_ab`,
                 rapp_NeuVonImportDuplikatfrei.`af_gueltig_bis`,
                 rapp_NeuVonImportDuplikatfrei.`direct_connect`,
                 rapp_NeuVonImportDuplikatfrei.`hk_tf_in_af`,
                 rapp_NeuVonImportDuplikatfrei.`gf_beschreibung`,
                 rapp_NeuVonImportDuplikatfrei.`af_zuweisungsdatum`,
                 rapp_NeuVonImportDuplikatfrei.`npu_rolle`,
                 rapp_NeuVonImportDuplikatfrei.`npu_grund`,
                 rapp_NeuVonImportDuplikatfrei.`iiq_organisation`,
                 0
          FROM rapp_NeuVonImportDuplikatfrei
          ON DUPLICATE KEY UPDATE doppelerkennung = doppelerkennung + 1;

          /*
              Beim Kopieren ist wichtig, dass die Felder,
              die später in JOINs verwendet werden sollen,
              keine NULL-Werte enthalten.
              Das wird durch die nachfolgenden simplen Korrektur-SQLs sichergestellt.
          */

          UPDATE tblRechteAMNeu SET `tf_beschreibung` = 'ka'
            WHERE `tf_beschreibung` Is Null Or `tf_beschreibung` = '';
          UPDATE tblRechteAMNeu SET `enthalten_in_af` = 'ka'
            WHERE `enthalten_in_af` Is Null or `enthalten_in_af`  ='';
          UPDATE tblRechteAMNeu SET `tf` = 'Kein Name'
            WHERE `tf` Is Null or `tf`  = '';
          UPDATE tblRechteAMNeu SET `tf_technische_plattform` = 'Kein Name'
            WHERE `tf_technische_plattform` Is Null or `tf_technische_plattform`  = '';
          UPDATE tblRechteAMNeu SET `tf_kritikalitaet` = 'ka'
            WHERE `tf_kritikalitaet` Is Null or  `tf_kritikalitaet` = '';
          UPDATE tblRechteAMNeu SET `tf_eigentuemer_org` = 'ka'
            WHERE `tf_eigentuemer_org` Is Null or  `tf_eigentuemer_org` = '';
          UPDATE tblRechteAMNeu SET `GF` = 'k.A.'
            WHERE GF Is Null or GF = '';
          UPDATE tblRechteAMNeu SET `hk_tf_in_af` = 'k.A.'
            WHERE `hk_tf_in_af` Is Null or `hk_tf_in_af` = '';
          UPDATE tblRechteAMNeu SET `af_beschreibung` = 'keine geliefert bekommmen'
            WHERE `af_beschreibung` Is Null or `af_beschreibung` = '';
          UPDATE tblRechteAMNeu SET `npu_rolle` = ''
            WHERE `npu_rolle` Is Null;
          UPDATE tblRechteAMNeu SET `npu_grund` = ''
            WHERE `npu_grund` Is Null;

          /*
          -- Sollte nun 0 ergeben:
          select count(*) from tblRechteAMNeu
              WHERE `tf_beschreibung` Is Null Or `tf_beschreibung` = ''
              or `enthalten_in_af` Is Null or `enthalten_in_af`  = ''
              or `tf` Is Null or `tf`  = ''
              or `tf_technische_plattform` Is Null or `tf_technische_plattform`  = ''
              or `tf_kritikalitaet` Is Null or  `tf_kritikalitaet` = ''
              or `tf_eigentuemer_org` Is Null or  `tf_eigentuemer_org` = ''
              or GF Is Null or GF = ''
              or `hk_tf_in_af` Is Null or  `hk_tf_in_af` = ''
              or `af_beschreibung` Is Null or `af_beschreibung` = '';
          */

          /*
              Bis hierhin ging die Vorbereitung.
              Die nächsten Schritte müssen manuell und visuell unterstützt werden:
                  - Sichtung der neu hinzugekommenen useriden,
                  - Übernahme in die userid-Liste
                  - Sichtung der nicht mehr vorhandenen User,
                    deren Einträge im weiteren Verlauf geloescht werden sollen
          */
      END
    """

    return push_sp("vorbereitung", sp, procs_schon_geladen)


def push_sp_neue_user(procs_schon_geladen):
    """
    Erzeuge Stored Procedure "neue_user"; das ist der zweite Schritt beim Import von IIQ-Daten

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        create procedure neueUser (IN orga char(32))
        BEGIN

            /*
                Die nächsten Schritte müssen manuell und visuell unterstützt werden:
                    - Sichtung der neu hinzugekommenen useriden,
                    - Übernahme in die userid-Liste
                    - Sichtung der nicht mehr vorhandenen User,
                      deren Einträge im weiteren Verlauf geloescht werden sollen
            */
            /*
                Zunächst die Suche nach neu hinzugekommenen Usern:
            */

            /*
                Dieses Statement wird aufgerufen,
                nachdem die CSV-Daten eingelesen wurden ('vorbereitung')
                und bevor der "Neue User speichern" Button angeklickt wird.
                Zunächst werden diejenigen User in eine temporäre Tabelle geschrieben,
                die in der Importliste auftauchen und
                    die nicht in der User-Tabelle auftauchen
                        (die beiden ersten Zeilen im WHERE), oder
                    die in der User-Tabelle vorhanden,
                        aber auf "geloescht" gesetzt sind (dritte Zeile im WHERE), oder
                    die in der User-Tabelle vorhanden sind,
                        aber mit einer anderen Abteilung oder Gruppe
                            als in der Importtabelle angegeben, oder
                    bei denen die zweite und dritte Bedingung zutreffen
                        (gelöschter User einer andern Orga) (3.+4. Zeile) oder
                    bei denen sich die npu_details unterscheiden (5.-8. Zeile)

                Dabei wird die Team-Zuordnung "neu" mit der konstanten Nummer 35
                bei völlig neuen Usern eingetragen.
                Der Vergleich erfolgt sowohl über über name als auch userid,
                damit auch erneut vergebene useriden auffallen.

                Gefundene, aber als geloescht markierte User sollen reaktiviert,
                die anderen an die vorhandene User-Tabelle angehängt werden.
                Dies geschieht aber erst im nächsten Schritt 'behandleUser'.
            */

            drop table if exists rapp_neue_user;
            create table rapp_neue_user as
                SELECT DISTINCT tblRechteAMNeu.userid as userid1,
                                tblRechteAMNeu.name as name1,
                                COALESCE(tblUserIDundName.orga_id, 35) AS Ausdr1,
                                orga AS Ausdr2,
                                concat('ZI-', orga) as abteilung,
                                tblRechteAMNeu.iiq_organisation as gruppe,
                                tblRechteAMNeu.npu_rolle,
                                tblRechteAMNeu.npu_grund,
                                tblUserIDundName.userid as userid_alt,
                                tblUserIDundName.name as name_alt,
                                tblUserIDundName.orga_id as team_alt,
                                tblUserIDundName.zi_organisation as zi_orga_alt,
                                tblUserIDundName.abteilung as abteilung_alt,
                                tblUserIDundName.gruppe as gruppe_alt,
                                tblUserIDundName.npu_rolle as npu_rolle_alt,
                                tblUserIDundName.npu_grund as npu_grund_alt,
                                tblUserIDundName.geloescht
                FROM tblRechteAMNeu
                    LEFT JOIN tblUserIDundName
                    ON tblRechteAMNeu.userid = tblUserIDundName.userid
                    -- AND tblUserIDundName.name = tblRechteAMNeu.name

                WHERE (tblRechteAMNeu.userid IS NOT NULL AND tblUserIDundName.userid IS NULL)
                        OR tblRechteAMNeu.name <> tblUserIDundName.name
                        OR (tblRechteAMNeu.name IS NOT NULL AND tblUserIDundName.name IS NULL)
                        OR tblUserIDundName.`geloescht` = TRUE
                        OR (tblRechteAMNeu.iiq_organisation != tblUserIDundName.gruppe
                            AND concat(tblRechteAMNeu.iiq_organisation, '--')
                                != tblUserIDundName.gruppe)
                        OR tblRechteAMNeu.npu_rolle != tblUserIDundName.npu_rolle
                        OR tblRechteAMNeu.npu_rolle not like ""
                            AND tblUserIDundName.npu_rolle is null
                        OR tblRechteAMNeu.npu_grund != tblUserIDundName.npu_grund
                        OR tblRechteAMNeu.npu_grund not like ""
                            AND tblUserIDundName.npu_grund is null
                ;

            /*
                Sichtung der nicht mehr vorhandenen User,
                deren Einträge im weiteren Verlauf geloescht werden sollen
                Erst einmal werden die Rechte der als zu löschen markierten User
                in die Historientabelle verschoben.
            */

            drop table if exists rapp_geloeschte_user;
            create table rapp_geloeschte_user as
            SELECT A.userid, A.name, A.`zi_organisation`
                FROM tblUserIDundName A
                WHERE   A.`zi_organisation` = orga
                    AND COALESCE(A.geloescht, FALSE) = FALSE
                    AND A.userid not in (select distinct userid from tblRechteAMNeu)
                GROUP BY
                    A.userid,
                    A.name,
                    A.`zi_organisation`
            ;

            -- SELECT * from rapp_geloeschte_user;

            -- Ein bisschen Statistik für den Anwender
            select 'Anzahl neuer oder geänderter User' as name, count(*) as wert from rapp_neue_user
            UNION
            select 'Anzahl gelöschter User' as name, count(*) as wert from rapp_geloeschte_user
            UNION
            select 'Anzahl gelesener Rechte' as name, count(*) as wert from tblRechteNeuVonImport
            UNION
            select 'Anzahl Rechte in AM_neu' as name, count(*) as wert from tblRechteAMNeu
            UNION
            select 'orga' as name, cast(orga as char) as wert

            ;
        END
    """
    return push_sp("neueUser", sp, procs_schon_geladen)


def push_sp_behandle_user(procs_schon_geladen):
    """
    Erzeuge Stored Procedure "behandle_user"; das ist der dritte Schritt beim Import von IIQ-Daten

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        create procedure behandleUser (IN update_gruppe char(3))
        BEGIN

            /*
                Merke die als gelöscht markierten User in einer temporären Tabelle,
                damit imm nächsten SAchritt das Join schnell funktioniert.
            */
            drop table if exists tbl_tmpGeloeschte;
            create temporary table tbl_tmpGeloeschte as
                SELECT userid1
                    FROM rapp_neue_user
                    WHERE `geloescht` = True;

            -- select * from tbl_tmpGeloeschte;

            /*
                Markiere die UserIDen wieder als aktiv, die bereits bekannt,
                aber als geloescht markiert sind.
            */
            UPDATE tblUserIDundName
                INNER JOIN tbl_tmpGeloeschte
                    ON tbl_tmpGeloeschte.userid1 = tblUserIDundName.userid
            SET tblUserIDundName.geloescht = False;

            /*
                Nun werden die neuen User an die userid-Tabelle angehängt.
                Für User, die bereits existieren und für die Änderungen identifiziet wurden,
                werden die NPU-Informationen, die ZI-Organisation,
                die Abteilung und - je nach Flag update_gruppe - die Gruppe aktualisiert.

                ToDo: ACHTUNG: Bis auf eine Zeile steht der nachfolgende Code doppelt!
            */
            IF update_gruppe like 'on%' THEN
                INSERT INTO tblUserIDundName (userid, name,
                        orga_id,
                        `zi_organisation`,
                        geloescht,
                        npu_rolle, npu_grund,
                        gruppe, abteilung)
                    SELECT userid1, name1,
                            Ausdr1 AS orga_id,
                            Ausdr2 AS `zi_organisation`,
                            False AS geloescht,
                            npu_rolle, npu_grund,
                            gruppe, abteilung
                        FROM rapp_neue_user
                        WHERE COALESCE(`geloescht`, FALSE) = FALSE
                            AND (userid1 IS NOT NULL OR name1 IS NOT NULL)
                ON DUPLICATE KEY UPDATE `zi_organisation` = Ausdr2,
                    geloescht = 0,
                    tblUserIDundName.npu_rolle = rapp_neue_user.npu_rolle,
                    tblUserIDundName.npu_grund = rapp_neue_user.npu_grund,
                    tblUserIDundName.gruppe = rapp_neue_user.gruppe,
                    tblUserIDundName.abteilung = rapp_neue_user.abteilung;
            ELSE
                INSERT INTO tblUserIDundName (userid, name,
                        orga_id,
                        `zi_organisation`,
                        geloescht,
                        npu_rolle, npu_grund,
                        gruppe, abteilung)
                    SELECT userid1, name1,
                            Ausdr1 AS orga_id,
                            Ausdr2 AS `zi_organisation`,
                            False AS geloescht,
                            npu_rolle, npu_grund,
                            gruppe, abteilung
                        FROM rapp_neue_user
                        WHERE COALESCE(`geloescht`, FALSE) = FALSE
                            AND (userid1 IS NOT NULL OR name1 IS NOT NULL)
                ON DUPLICATE KEY UPDATE `zi_organisation` = Ausdr2,
                    geloescht = 0,
                    tblUserIDundName.npu_rolle = rapp_neue_user.npu_rolle,
                    tblUserIDundName.npu_grund = rapp_neue_user.npu_grund,
                    tblUserIDundName.abteilung = rapp_neue_user.abteilung;
            END IF;


            /*
                Bevor die alten User als geloescht markiert werden,
                müssen deren derzeit vorhandenen Rechte in die Historientabelle verschoben werden.

                ACHTUNG: Das ist derzeit disabled
            * /

            INSERT INTO tblGesamtHistorie (
                        `userid_und_name_id`, tf, `tf_beschreibung`,
                        `enthalten_in_af`, `af_beschreibung`,
                        modell, `tf_kritikalitaet`, `tf_eigentuemer_org`, `af_zuweisungsdatum`,
                        plattform_id, GF, geloescht, gefunden, wiedergefunden, geaendert,
                        loeschdatum, neueaf, datum, `id_alt`,
                        `hk_tf_in_af`, `letzte_aenderung`
                    )
            SELECT `tblGesamt`.`userid_und_name_id`,
                   `tblGesamt`.tf,
                   `tblGesamt`.`tf_beschreibung`,
                   `tblGesamt`.`enthalten_in_af`,
                   `tblGesamt`.`af_beschreibung`,
                   `tblGesamt`.modell,
                   `tblGesamt`.`tf_kritikalitaet`,
                   `tblGesamt`.`tf_eigentuemer_org`,
                   `tblGesamt`.`af_zuweisungsdatum`,
                   `tblGesamt`.plattform_id,
                   `tblGesamt`.GF,
                   `tblGesamt`.`geloescht`,
                   `tblGesamt`.gefunden,
                   `tblGesamt`.wiedergefunden,
                   `tblGesamt`.`geaendert`,
                   Now() AS Ausdr1,
                   `tblGesamt`.neueaf,
                   `tblGesamt`.datum,
                   `tblGesamt`.id,
                   `hk_tf_in_af`,
                   `tblGesamt`.`letzte_aenderung`
                FROM `tblGesamt`
                INNER JOIN (tblUserIDundName
                            inner join rapp_geloeschte_user
                            on rapp_geloeschte_user.userid = tblUserIDundName.userid)
                    ON tblUserIDundName.id = `tblGesamt`.`userid_und_name_id`
                WHERE tblUserIDundName.userid IN (SELECT userid FROM `rapp_geloeschte_user`)
                    AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE;
            */

            -- Setzen der Löschflags in der Gesamttabelle für jedes Recht
            -- jeder nicht mehr vorhandenen userid
            -- ToDo Mal überlegen, wann Historisierung und wann auf gelöscht Setzen sinnvoller ist

            UPDATE
                tblGesamt
                INNER JOIN (tblUserIDundName
                            inner join rapp_geloeschte_user
                            on rapp_geloeschte_user.userid = tblUserIDundName.userid)
                    ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id
                SET tblGesamt.geloescht = TRUE,
                    tblGesamt.`loeschdatum` = Now()
                WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE;

            -- Die zu löschenden User werden in der User-Tabelle nun auf "geloescht" gesetzt

            UPDATE tblUserIDundName
                INNER JOIN rapp_geloeschte_user
                    ON rapp_geloeschte_user.userid = tblUserIDundName.userid
                SET `geloescht` = TRUE
                WHERE COALESCE(`geloescht`, FALSE) = FALSE;

            /*
                Nun werden für alle UserIDen, die in der rapp_neue_user Tabelle stehen,
                die Abteilung und die Gruppe in der Usertabelle aktualisiert.
                Das führt dazu, dass User, die in der Organisation umziehen,
                endlich richtig behandelt werden.

                Berücksichtigt wird der Sonderfall, dass Bereichs- udn Abteilungskürzel
                - wo sinnvoll -- mit '--' terminiert werden.
                Das wird überall dort benötigt,
                wo die Suche "enthält" zu viele Treffer findet (bspw. beim BL)
            */
            if update_gruppe like 'on%' THEN
                UPDATE tblUserIDundName
                INNER JOIN rapp_neue_user
                    ON tblUserIDundName.userid = rapp_neue_user.userid1
                        and tblUserIDundName.gruppe != rapp_neue_user.gruppe
                        and tblUserIDundName.gruppe != concat(rapp_neue_user.gruppe, '--')
                SET tblUserIDundName.abteilung = rapp_neue_user.abteilung,
                    tblUserIDundName.gruppe = rapp_neue_user.gruppe;
            END IF;

            /*
                Abschließend werden alle gefundenen EInträge aus IIQ zur Organisation
                (in unserem SInn die Gruppe)
                in das entsprechende Feld kopiert - unabhängig von Update-Flag.

                Das hat zum Zweck, dass anschließend dauerhaft Abfragen
                zu Inkonsistenzen durchgeführt werden können.
                Dazu wird es mindestens eine Liste geben,
                in der die Abweichungen dargestellt werden.
            */

            UPDATE tblUserIDundName
            INNER JOIN tblRechteAMNeu
                ON tblUserIDundName.userid = tblRechteAMNeu.userid
            SET tblUserIDundName.iiq_organisation = tblRechteAMNeu.iiq_organisation
            WHERE not tblUserIDundName.geloescht;
        END
    """
    return push_sp("behandleUser", sp, procs_schon_geladen)


def push_sp_behandle_rechte(procs_schon_geladen):
    """
    Erzeuge Stored Procedure "behandle_rechte"; das ist der vierte Schritt beim Import von IIQ-Daten

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        create procedure behandleRechte (IN orga char(32))
        BEGIN

            /*
                Nun folgt der komplexere Block:
                Die neuen, evtl. unveränderten und auch nicht mehr vorhandenen
                einzelnen Berechtigungen müssen schrittweise
                in die Gesamttabelle eingetragen werden.
            */

            -- Markiere zunächst Plattform-Namen,
            -- die in der Gesamttabelle nicht mehr auftauchen, als gelöscht
            -- (manchmal werden Plattformen einfach umbenannt).
            -- Das echte Löschen muss bei Bedarf in Schritten erfolgen,
            -- weil in der Historientabelle weiterhin Referenzen
            -- auf die nicht mehr aktuellen PlattformIDs stehen können.
            drop table if exists bloed;
            CREATE TEMPORARY TABLE bloed as
                SELECT tblPlattform.`tf_technische_plattform` as x
                    FROM tblPlattform
                    LEFT JOIN tblGesamt ON tblPlattform.id = tblGesamt.plattform_id
                    WHERE tblGesamt.plattform_id IS NULL
                        AND not tblPlattform.geloescht;

            UPDATE tblPlattform SET geloescht = true
            WHERE `tf_technische_plattform` IN (SELECT x FROM bloed);

            -- Ergänze alle Plattformen, die bislang nur in tblRechteAMNeu bekannt sind
            INSERT INTO tblPlattform (`tf_technische_plattform`)
                SELECT DISTINCT tblRechteAMNeu.`tf_technische_plattform`
                FROM tblRechteAMNeu
                    LEFT JOIN tblPlattform
                    ON tblRechteAMNeu.`tf_technische_plattform`
                        = tblPlattform.`tf_technische_plattform`
                WHERE COALESCE(tblPlattform.geloescht is null, not tblPlattform.geloescht)
                    AND tblPlattform.`tf_technische_plattform` IS NULL;

            /*
                Der Status "gefunden" dient dazu,
                später die Selektion neuer Rechte zu vereinfachen
                und übriggebliebene Rechte zu löschen.
                Er wird sowohl in der Gesamt-Tabelle, als auch in der Importtabelle zurückgesetzt.
                Gleichzeitig wird der Status "geaendert" in beiden Tabellen zurückgesetzt.
            */

            UPDATE tblGesamt
                INNER JOIN tblUserIDundName
                ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id
            SET tblGesamt.gefunden = FALSE,
                tblGesamt.geaendert = FALSE
            WHERE tblGesamt.gefunden = TRUE OR tblGesamt.`geaendert` = TRUE;

            -- Dies hier nur zur Sicherheit - eigentlich müssten die null sein
            UPDATE tblRechteAMNeu
            SET tblRechteAMNeu.gefunden = FALSE,
                tblRechteAMNeu.geaendert = FALSE
            WHERE tblRechteAMNeu.gefunden = TRUE
                OR tblRechteAMNeu.geaendert = TRUE;

            /*
                Nun wird die "flache" Tabelle "rapp_Gesamt_komplett" erzeugt.
                Dort sind die Referenzen zu den derzeit existierenden, aktiven
                User-, Berechtigungs- und Orga-Tabellen aufgelöst,
                allerdings in dieser Implementierung ausschließlich für die benötigten UserIDen
                (früher wirklich komplett).
            */

            drop table if exists uids;
            create table uids as
                select distinct userid as uid from tblRechteAMNeu;

            drop table if exists rapp_Gesamt_komplett;
            create table rapp_Gesamt_komplett as
                SELECT tblGesamt.id,
                       tblUserIDundName.userid,
                       tblUserIDundName.name,
                       tblGesamt.tf,
                       tblGesamt.`tf_beschreibung`,
                       tblGesamt.`enthalten_in_af`,
                       tblGesamt.`af_beschreibung`,
                       tblUEbersichtAF_GFs.`name_gf_neu`,
                       tblUEbersichtAF_GFs.`name_af_neu`,
                       tblGesamt.`tf_kritikalitaet`,
                       tblGesamt.`tf_eigentuemer_org`,
                       tblPlattform.`tf_technische_plattform`,
                       tblGesamt.GF,
                       tblGesamt.modell,
                       tblUserIDundName.orga_id,
                       tblUserIDundName.`zi_organisation`,
                       tblGesamt.`af_gueltig_ab`,
                       tblGesamt.`af_gueltig_bis`,
                       tblGesamt.`direct_connect`,
                       tblGesamt.`hk_tf_in_af`,
                       tblGesamt.`gf_beschreibung`,
                       tblGesamt.`af_zuweisungsdatum`,
                       tblGesamt.datum,
                       tblGesamt.`geloescht`,
                       tblGesamt.`letzte_aenderung`
                FROM tblGesamt
                    INNER JOIN tblUEbersichtAF_GFs
                    ON tblGesamt.modell = tblUEbersichtAF_GFs.id

                    INNER JOIN tblPlattform
                    ON tblPlattform.id = tblGesamt.plattform_id

                    INNER JOIN tblUserIDundName
                    ON tblGesamt.`userid_und_name_id` = tblUserIDundName.id

                WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
                    AND tblUserIDundName.userid in (select uid from uids)
                ORDER BY tblGesamt.tf,
                         tblUserIDundName.userid;

            /*
                Markieren der Flags Gefunden in tblRechteAMNeu sowie tblGesamt.
                In letzterer wird auch das wiedergefunden-Datum eingetragen,
                wann das Recht wiedergefunden wurde.

                Zusätzlich werden alle Felder, die hier nicht zum Vergleich der Rechte-Gleichheit
                genutzt wurden, in der Gesamttabelle aktualisiert.

                Das hat früher mal zu Problemen geführt (Umbenennung ovn Rechten und -Eigentümern),
                in letzter Zeit aber eher nicht mehr.

            */

            -- Zunächst das Setzen und Kopieren der Daten im Fall "Wiedergefunden"
            UPDATE tblRechteAMNeu
                INNER JOIN tblGesamt
                ON tblRechteAMNeu.tf = tblGesamt.tf
                    AND tblRechteAMNeu.GF = tblGesamt.GF
                    AND tblRechteAMNeu.`enthalten_in_af` = tblGesamt.`enthalten_in_af`

                INNER JOIN tblUserIDundName
                ON tblUserIDundName.userid = tblRechteAMNeu.userid
                    AND tblUserIDundName.id = tblGesamt.`userid_und_name_id`

                INNER JOIN tblPlattform
                ON tblPlattform.`tf_technische_plattform`
                    = tblRechteAMNeu.`tf_technische_plattform`
                    AND tblPlattform.id = tblGesamt.plattform_id

            SET tblGesamt.gefunden = TRUE,
                tblGesamt.Wiedergefunden = Now(),
                tblRechteAMNeu.Gefunden = TRUE,
                tblGesamt.`tf_beschreibung`     = `tblRechteAMNeu`.`tf_beschreibung`,
                tblGesamt.`af_beschreibung`     = `tblRechteAMNeu`.`af_beschreibung`,
                tblGesamt.`tf_kritikalitaet`    = `tblRechteAMNeu`.`tf_kritikalitaet`,
                tblGesamt.`tf_eigentuemer_org`  = `tblRechteAMNeu`.`tf_eigentuemer_org`,
                tblGesamt.`af_gueltig_ab`       = `tblRechteAMNeu`.`af_gueltig_ab`,
                tblGesamt.`af_gueltig_bis`      = `tblRechteAMNeu`.`af_gueltig_bis`,
                tblGesamt.`direct_connect`      = `tblRechteAMNeu`.`direct_connect`,
                tblGesamt.`hk_tf_in_af`         = `tblRechteAMNeu`.`hk_tf_in_af`,
                tblGesamt.`gf_beschreibung`     = `tblRechteAMNeu`.`gf_beschreibung`,
                tblGesamt.`af_zuweisungsdatum`  = `tblRechteAMNeu`.`af_zuweisungsdatum`,
                tblGesamt.`letzte_aenderung`    = now()

            WHERE COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
                AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE;


            /*
                Dies implementiert den Fall der geänderten AF aber ansonsten gleichen Daten
            */

            UPDATE tblRechteAMNeu
                INNER JOIN tblGesamt
                ON tblRechteAMNeu.tf = tblGesamt.tf
                    AND tblRechteAMNeu.GF = tblGesamt.GF

                INNER JOIN tblUserIDundName
                ON tblUserIDundName.userid = tblRechteAMNeu.userid
                    AND tblUserIDundName.id = tblGesamt.`userid_und_name_id`

                INNER JOIN tblPlattform
                ON tblPlattform.`tf_technische_plattform`
                    = tblRechteAMNeu.`tf_technische_plattform`
                    AND tblPlattform.id = tblGesamt.plattform_id

            SET tblGesamt.geaendert = TRUE,
                tblRechteAMNeu.geaendert = TRUE,
                tblGesamt.neueaf = `tblRechteAMNeu`.`enthalten_in_af`,
                tblGesamt.letzte_aenderung = now()

            WHERE   tblGesamt.`enthalten_in_af` <> tblRechteAMNeu.`enthalten_in_af`
                AND tblGesamt.gefunden = FALSE
                AND tblRechteAMNeu.Gefunden = FALSE
                AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
                AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
                ;

            /*
                In die Historientabelle werden die zur Änderung vorgemerkten Einträge
                aus der Gesamttabelle kopiert.
            */

            INSERT INTO tblGesamtHistorie (`userid_und_name_id`, tf, `tf_beschreibung`,
                        `enthalten_in_af`,`af_beschreibung`, modell, `tf_kritikalitaet`,
                        `tf_eigentuemer_org`, plattform_id, GF, geloescht, gefunden,
                        wiedergefunden, geaendert, neueaf,
                        datum, `id_alt`, loeschdatum, `hk_tf_in_af`
        )
            SELECT tblGesamt.`userid_und_name_id`,
                   tblGesamt.tf,
                   tblGesamt.`tf_beschreibung`,
                   tblGesamt.`enthalten_in_af`,
                   tblGesamt.`af_beschreibung`,
                   tblGesamt.modell,
                   tblGesamt.`tf_kritikalitaet`,
                   tblGesamt.`tf_eigentuemer_org`,
                   tblGesamt.plattform_id,
                   tblGesamt.GF,
                   tblGesamt.geloescht,
                   tblGesamt.gefunden,
                   Now() AS Ausdr1,
                   tblGesamt.geaendert,
                   tblGesamt.neueaf,
                   tblGesamt.datum,
                   tblGesamt.id,
                   tblGesamt.loeschdatum,
                   tblGesamt.`hk_tf_in_af`

            FROM tblUserIDundName
                INNER JOIN tblGesamt
                ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`

            WHERE tblGesamt.`geaendert` = TRUE
                   AND tblUserIDundName.`zi_organisation` LIKE orga;
                   -- ToDo: Wird die Einschränkung wirklich benötigt?
            -- ToDo: Es sollte ja nicht kopiert, sondern verschoben werden.
            -- Es fehlt hier also das Löschen.


            /*
                Anschließend können die geaenderten Werte in die GesamtTabelle übernommen werden.
                Dazu wird der Inhalt des kommentarfelds in die AF-alt-Spalte eingetragen.
                Damit müsste das erledigt sein :-)
            */

            -- ToDo: Später noch mal das geaendert-Flag zurücksetzen, dann entfällt das ToDo vorher

            UPDATE tblUserIDundName
                INNER JOIN tblGesamt
                ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`
            SET tblGesamt.`enthalten_in_af` = tblGesamt.`neueaf`

            WHERE tblGesamt.`geaendert` = TRUE
                AND tblUserIDundName.`zi_organisation` = orga;


            /*
                Als nächstes kann es sein, dass in der Importliste noch tf mit NEUEN AF stehen,
                die zwar bereits in der Gesamtliste bezogen auf die Uid bekannt sind,
                dort aber bereits mit den ALTEN AF-Bezeichnungen gefunden wurden.
                Damit nun nicht bei jedem wiederholten Import die AF-Bezeichnungen
                umgeschossen werden, hängen wir diese Zeilen nun hinten an die Gesamttabelle an.

                Dazu werden im ersten Schritt in der Importtabelle die Zeilen markiert
                (angehaengt_bekannt), die anzuhängen sind.
                Das sieht zwar umständlich aus, erleichtert aber später die Bewertung.
                ob noch irgendwelche Einträge in der Importtabelle nicht bearbeitet wurden.
                Die Flags kann man eigentlich auch zusammenfassen,
                dann müssten aber bearbeitete Zeilen separat umgeschossen werden...

                Beim Einfügen der neuen tf-AF-Kombinationen
                wird in der Gesamttabelle "gefunden" gesetzt,
                damit das Recht später nicht gleich wieder geloescht wird.

                qryF5_FlaggetfmitNeuenAFinImportTabelle
            */

            UPDATE tblRechteAMNeu
                INNER JOIN rapp_Gesamt_komplett
                ON (tblRechteAMNeu.GF = rapp_Gesamt_komplett.GF)
                    AND (tblRechteAMNeu.`enthalten_in_af` = rapp_Gesamt_komplett.`enthalten_in_af`)
                    AND (tblRechteAMNeu.userid = rapp_Gesamt_komplett.userid)
                    AND (tblRechteAMNeu.tf = rapp_Gesamt_komplett.tf)
                    AND (tblRechteAMNeu.`tf_technische_plattform`
                        = rapp_Gesamt_komplett.`tf_technische_plattform`)
                SET tblRechteAMNeu.`angehaengt_bekannt` = TRUE
                WHERE tblRechteAMNeu.Gefunden = TRUE
                    AND tblRechteAMNeu.`geaendert` = FALSE;

            /*
                Zum Gucken:

            SELECT COUNT(*) FROM tblRechteAMNeu
                INNER JOIN rapp_Gesamt_komplett
                ON (tblRechteAMNeu.GF = rapp_Gesamt_komplett.GF)
                    AND (tblRechteAMNeu.`enthalten_in_af` = rapp_Gesamt_komplett.`enthalten_in_af`)
                    AND (tblRechteAMNeu.userid = rapp_Gesamt_komplett.userid)
                    AND (tblRechteAMNeu.tf = rapp_Gesamt_komplett.tf)
                    AND (tblRechteAMNeu.`tf_technische_plattform`
                        = rapp_Gesamt_komplett.`tf_technische_plattform`)
                WHERE tblRechteAMNeu.Gefunden = TRUE
                    AND tblRechteAMNeu.`geaendert` = FALSE;
            */

            /*
                Anschließend werden diese selektierten Zeilen an die Gesamttabelle angehängt.
                Dabei wird in der Gesamttabelle das Flag "gefunden" gesetzt,
                um diese Einträge erkennbar zu machen für das nachfolgende Löschen alter Einträge.

                qryF5_HaengetfmitNeuenAFanGesamtTabelleAn
            */

            INSERT INTO tblGesamt (tf, `tf_beschreibung`, `enthalten_in_af`, `af_beschreibung`,
                        datum, modell, `userid_und_name_id`,
                        plattform_id, Gefunden, `geaendert`, `tf_kritikalitaet`,
                        `tf_eigentuemer_org`, GF,
                        `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`, `hk_tf_in_af`,
                        `gf_beschreibung`, `af_zuweisungsdatum`, letzte_aenderung)
            SELECT  tblRechteAMNeu.tf,
                    tblRechteAMNeu.`tf_beschreibung`,
                    tblRechteAMNeu.`enthalten_in_af`,
                    tblRechteAMNeu.`af_beschreibung`,
                    Now() AS datumNeu,
                    (
                        SELECT DISTINCT modell
                        FROM `tblGesamt`
                        WHERE `tblGesamt`.`userid_und_name_id` = (
                            SELECT DISTINCT id
                            FROM tblUserIDundName
                            WHERE userid = tblRechteAMNeu.userid
                        )
                        AND `tblGesamt`.`tf` = `tblRechteAMNeu`.`tf`
                        LIMIT 1
                    ) AS modellNeu,

                    (SELECT id FROM tblUserIDundName WHERE userid
                        = tblRechteAMNeu.userid) AS UidnameNeu,

                    (SELECT id FROM tblPlattform
                        WHERE `tf_technische_plattform` = tblRechteAMNeu.`tf_technische_plattform`)
                            AS PlattformNeu,
                    TRUE AS Ausdr1,
                    tblRechteAMNeu.`geaendert`,
                    tblRechteAMNeu.`tf_kritikalitaet`,
                    tblRechteAMNeu.`tf_eigentuemer_org`,
                    tblRechteAMNeu.GF,
                    tblRechteAMNeu.`af_gueltig_ab`,
                    tblRechteAMNeu.`af_gueltig_bis`,
                    tblRechteAMNeu.`direct_connect`,
                    tblRechteAMNeu.`hk_tf_in_af`,
                    tblRechteAMNeu.`gf_beschreibung`,
                    tblRechteAMNeu.`af_zuweisungsdatum`,
                    now() as letzte_aenderung

            FROM tblRechteAMNeu
            WHERE tblRechteAMNeu.Gefunden = FALSE
                AND tblRechteAMNeu.`angehaengt_bekannt` = TRUE;

            /*
                Nun werden noch die Rechte derjenigen User behandelt,
                die bislang in der Importtabelle nicht berücksichtigt worden sind.
                Dies können nur noch Rechte bislang unbekannter User
                oder unbekannte Rechte bekannter User sein.
                Dazu werden diese Rechte zunächst mit dem Flag "angehaengt_sonst" markiert:
            */

            /*
            select * from tblRechteAMNeu
            WHERE COALESCE(Gefunden, FALSE) = FALSE
                AND COALESCE(geaendert, FALSE) = FALSE
                AND COALESCE(angehaengt_bekannt, FALSE) = FALSE;
            */

            UPDATE tblRechteAMNeu
            SET `angehaengt_sonst` = TRUE
            WHERE COALESCE(Gefunden, FALSE) = FALSE
                AND COALESCE(geaendert, FALSE) = FALSE
                AND COALESCE(angehaengt_bekannt, FALSE) = FALSE;

            /*
            select * from tblRechteAMNeu
            WHERE angehaengt_sonst = TRUE;
            */

            /*
                Ist doch ganz zu Beginn der SP schon geschehen.
                Wenn keine Merkwürdigkeiten auftreten, kann das mal ganz gelöscht werden
                Jetzt sehen wir uns die Plattform an, die in der Importliste auftauchen
                und hängen gegebenenfalls fehlende Einträge an die Plattform-Tabelle an.

                qryF5_AktualisierePlattformListe

            INSERT INTO tblPlattform (`tf_technische_plattform`)
                SELECT DISTINCT tblRechteAMNeu.`tf_technische_plattform`
                FROM tblRechteAMNeu
                    LEFT JOIN tblPlattform
                    ON tblRechteAMNeu.`tf_technische_plattform`
                        = tblPlattform.`tf_technische_plattform`
                WHERE not tblPlattform.geloescht
                    AND tblPlattform.`tf_technische_plattform` IS NULL;
            */


            /*
                Nun werden alle neuen Rechte aller User an die Gesamttabelle angehängt.
                Der alte query-name weist irrtümlich darauf hin,
                dass nur neue User hier behandelt würden,
                das ist aber definitiv nicht so.

                qryF5_HaengetfvonNeuenUsernAnGesamtTabelleAn
            */

            INSERT INTO tblGesamt (tf, `tf_beschreibung`, `enthalten_in_af`,  `Af_beschreibung`,
                        datum, modell, `userid_und_name_id`,
                        plattform_id, Gefunden, `geaendert`, `tf_kritikalitaet`,
                        `tf_eigentuemer_org`, geloescht, GF,
                        `af_gueltig_ab`, `af_gueltig_bis`, `direct_connect`,
                        `hk_tf_in_af`, `gf_beschreibung`, `af_zuweisungsdatum`, letzte_aenderung)
                SELECT  tblRechteAMNeu.tf,
                        tblRechteAMNeu.`tf_beschreibung`,
                        tblRechteAMNeu.`enthalten_in_af`,
                        tblRechteAMNeu.`af_beschreibung`,
                        Now() AS datumNeu,

                        (SELECT `id` FROM `tblUEbersichtAF_GFs` WHERE `name_af_neu`
                            LIKE 'Neues Recht noch nicht eingruppiert') AS modellNeu,

                        (SELECT id FROM tblUserIDundName WHERE userid = tblRechteAMNeu.userid)
                            AS UidnameNeu,

                        (SELECT id FROM tblPlattform
                            WHERE `tf_technische_plattform`
                                = tblRechteAMNeu.`tf_technische_plattform`) AS PlattformNeu,

                        TRUE AS Ausdr1,
                        FALSE AS Ausdr2,
                        tblRechteAMNeu.`tf_kritikalitaet`,
                        tblRechteAMNeu.`tf_eigentuemer_org`,
                        FALSE AS Ausdr3,
                        tblRechteAMNeu.GF,
                        tblRechteAMNeu.`af_gueltig_ab`,
                        tblRechteAMNeu.`af_gueltig_bis`,
                        tblRechteAMNeu.`direct_connect`,
                        tblRechteAMNeu.`hk_tf_in_af`,
                        tblRechteAMNeu.`gf_beschreibung`,
                        tblRechteAMNeu.`af_zuweisungsdatum`,
                        now() as letzte_aenderung
                FROM tblRechteAMNeu
                WHERE tblRechteAMNeu.`angehaengt_sonst` = TRUE;


            /*
                Importiert und angehängt haben wir alles.
                Was noch fehlt, ist das Markieren derjenigen Einträge,
                die bislang bekannt waren, aber in der Importtabelle nicht mehr auftauchen.

                Dabei handelt es sich um geloeschte Rechte oder geloeschte User.

                Um die Nachvollziehbarkeit erhalten zu können,
                wird in der nachfolgenden Abfrage nur das "geloescht"-Flag gesetzt,
                aber kein Eintrag entfernt.
                Da wir nicht wissen, ab wann das Element geloescht wurde,
                sondern wir nur den Tagesstand des Importabzugs kennen,
                wird ein separates loeschdatum gesetzt.
                Damit bleiben im Datensatz das Einstellungsdatum
                und das letzte Wiederfinde-datum erhalten, das muss reichen.

                Die Abfrage greift nur auf TFs von Usern zurück,
                die sich auch in der Importtabelle befinden
                (sonst würden u.U. Rechte von anderen User ebenfalls auf "geloescht" gesetzt).
                Das führt dazu, dass TFs von nicht mehr existenten Usern
                hiervon nicht markiert werden.
                Dazu gibt es aber die Funktion "geloeschte User entfernen",
                die vorher genutzt wurde.
            */

            UPDATE tblUserIDundName
                INNER JOIN tblGesamt
                ON tblUserIDundName.id = tblGesamt.`userid_und_name_id`
                    AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE
                    AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE
                    AND COALESCE(tblGesamt.gefunden, FALSE) = FALSE
                    AND COALESCE(tblGesamt.`geaendert`, FALSE) = FALSE
                    AND COALESCE(tblUserIDundName.`geloescht`, FALSE) = FALSE

            SET tblGesamt.geloescht = TRUE,
                tblGesamt.loeschdatum = Now()

            WHERE tblUserIDundName.userid IN (
                    SELECT `userid`
                    FROM `tblRechteAMNeu`
                    WHERE `userid` = `tblUserIDundName`.`userid`
                );


            /*
                Dann werden noch die Standardwerte für die rvm_ und RVA_00005
                Einträge auf "Bleibt (Control-SA)" gesetzt,
                denn das ist Vorgabe von BM.

                Was eigentlich auch automatisch gesetzt werden sollte, sind die rvo_ Rechte,
                aber die sind extrem fehlerhaft modelliert.
                Deshalb lassen wir bis auf das AI-Recht erst mal die Finger davon.

                qryF5_AktualisiereRVM_

                qryF5_AktualisiereRVO_00005 wurde nicht mit übernommen,
                weil die rvo_Rechte nun in der neuen modellierung berücksichtigt werden
            */

            UPDATE tblGesamt,
                   tblUEbersichtAF_GFs
            SET tblGesamt.modell = `tblUEbersichtAF_GFs`.`id`
            WHERE tblGesamt.`enthalten_in_af` LIKE "rvm_*"
                AND tblUEbersichtAF_GFs.`name_gf_neu` = "Bleibt (Control-SA)"
                AND COALESCE(tblGesamt.`geloescht`, FALSE) = FALSE;

            /*
                Jetzt müssen zum Abschluss noch in denjenigen importierten Zeilen,
                bei denen die TFs unbekannt sind, das modell auf "neues Recht" gesetzt werden.
                Die sind daran zu erkennen, dass das modell NULL ist.
            */

            UPDATE tblGesamt,
                   tblUEbersichtAF_GFs
            SET tblGesamt.modell = `tblUEbersichtAF_GFs`.`id`
            WHERE tblUEbersichtAF_GFs.`name_gf_neu` = "Neues Recht noch nicht eingruppiert"
               AND tblGesamt.modell IS NULL;


        /*
            Und fertig wir sind.
        */
        END
    """
    return push_sp("behandleRechte", sp, procs_schon_geladen)


def push_sp_loesche_doppelte_rechte(procs_schon_geladen):
    """
    Prozedur zum Finden und Löschen doppelt vorhandener Einträge in der Gesamttabelle.
    Auch wenn das eigentlich ie vorkommen dürfte, passiert das dennoch ab und an.
    Hauptgruind sind falsch formatierte Eingatelisten.

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        create procedure loescheDoppelteRechte (IN nurLesen bool)
        BEGIN
            drop table if exists qryF3_DoppelteElementeFilterAusGesamtTabelle;
            CREATE temporary table qryF3_DoppelteElementeFilterAusGesamtTabelle as
                SELECT DISTINCT b.id,
                    b.tf,
                    a.geloescht as RechtGeloescht,
                    b.geloescht as UserGeloescht,
                    tblUserIDundName.userid,
                    tblUserIDundName.name,
                    a.GF

                    FROM tblGesamt AS b,
                        tblUserIDundName
                        INNER JOIN tblGesamt AS a
                            ON tblUserIDundName.id = a.userid_und_name_id
                    WHERE a.id < b.id
                        AND COALESCE(a.geloescht, FALSE) = FALSE
                        AND COALESCE(a.geloescht, FALSE) = FALSE
                        AND a.GF = b.gf
                        AND a.userid_und_name_id =b.userid_und_name_id
                        AND a.tf = b.tf
                        AND a.enthalten_in_af = b.enthalten_in_af
                        AND a.tf_beschreibung = b.tf_beschreibung
                        AND a.plattform_id = b.plattform_id
                        AND a.tf_kritikalitaet = b.tf_kritikalitaet
                        AND a.tf_eigentuemer_org = b.tf_eigentuemer_org;

            IF (COALESCE(nurlesen, false) = True)
            THEN
                select count(*) from qryF3_DoppelteElementeFilterAusGesamtTabelle;
            ELSE
                UPDATE tblGesamt
                    INNER JOIN qryF3_DoppelteElementeFilterAusGesamtTabelle
                    ON tblGesamt.id = qryF3_DoppelteElementeFilterAusGesamtTabelle.id

                    SET tblGesamt.geloescht = True,
                        tblGesamt.patchdatum = Now()
                    WHERE COALESCE(tblGesamt.geloescht, FALSE) = False;
            END IF;
        END
    """
    return push_sp("loescheDoppelteRechte", sp, procs_schon_geladen)


def push_sp_erzeuge_af_liste(procs_schon_geladen):
    """
    Erzeuge die Liste der erlaubten Arbeitsplatzfunktionen.
    Sie wird später in der Rollenbehandlung benötigt.

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE erzeuge_af_liste()
        BEGIN
             INSERT INTO tbl_AFListe ( `af_name`, neu_ab )
                SELECT `tblUEbersichtAF_GFs`.`name_af_neu` AS af_name, now() AS neu_ab
                    FROM tblUEbersichtAF_GFs
                        LEFT JOIN tbl_AFListe
                        ON tblUEbersichtAF_GFs.`name_af_neu` = tbl_AFListe.`af_name`
                    WHERE (((tblUEbersichtAF_GFs.modelliert) Is Not Null)
                        AND ((tbl_AFListe.`af_name`) Is Null))
                GROUP BY tblUEbersichtAF_GFs.`name_af_neu`;
        END
    """
    return push_sp("erzeuge_af_liste", sp, procs_schon_geladen)


def push_sp_ueberschreibe_modelle(procs_schon_geladen):
    """
    Finde alle Einträge, bei denen ein manuell gesetztes Modell
    nicht zu den aktuell bereits freigegebenen Modell passt.
    Der Fall tritt ein, wenn
    - eine GF/AF-Kombination neut freigegeben wird
    und diese Kombination ehemals mit einem manuellen Modell versehen worden ist
    - wenn eine Rechteliste neeu eingelesen wird und der Importer versucht,
    unnötig intelligent zu sein

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE ueberschreibeModelle()
        BEGIN
            drop table if exists auchBloed;
            CREATE TEMPORARY TABLE auchBloed
              SELECT
                      tblGesamt.id as diffID,
                    tblGesamt.modell as gewaehltes_Modell,
                    tblUEbersichtAF_GFs.id as freigegebenes_Modell
              FROM `tblGesamt`
                INNER JOIN tblUEbersichtAF_GFs
                ON (
                    tblUEbersichtAF_GFs.name_af_neu = tblGesamt.enthalten_in_af
                    AND tblUEbersichtAF_GFs.name_gf_neu = tblGesamt.gf
                )
              WHERE tblGesamt.modell <> tblUEbersichtAF_GFs.id;

            UPDATE     tblGesamt
                INNER JOIN auchBloed
                ON tblGesamt.id = auchBloed.diffID
            SET tblGesamt.modell = auchBloed.freigegebenes_Modell;
        END
    """
    return push_sp("ueberschreibeModelle", sp, procs_schon_geladen)


def push_sp_direct_connects(procs_schon_geladen):
    """
    Suche nach Direct Connections innerhalb der Abteilung
    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        CREATE PROCEDURE directConnects()
        -- Suche nach Direct Connections innerhalb der Abteilung
        --
        -- Teil 1: Finde alle aktiven Direct Connects der Abteilung,
        -- die nicht zu SAP gehören
        -- und die nicht zu Test-CICS gehören
        BEGIN
            DROP TABLE IF EXISTS dircon_dircons;
            CREATE TABLE dircon_dircons
            SELECT
                tblUserIDundName.userid,
                tblUserIDundName.name,
                tblUserIDundName.gruppe,
                tblPlattform.tf_technische_plattform as `Plattform`,
                tblGesamt.tf,
                tblGesamt.tf_beschreibung,
                tblGesamt.tf_kritikalitaet,
                tblGesamt.tf_eigentuemer_org,
                tblGesamt.af_gueltig_ab,
                tblGesamt.af_gueltig_bis,
                tblGesamt.direct_connect,
                tblGesamt.af_zuweisungsdatum

            FROM `tblGesamt`
                INNER JOIN tblUserIDundName
                    ON tblGesamt.userid_und_name_id = tblUserIDundName.id
                INNER JOIN tblPlattform
                    ON tblGesamt.plattform_id = tblPlattform.id

            WHERE NOT tblGesamt.geloescht
                AND NOT tblUserIDundName.geloescht
                AND tblGesamt.direct_connect = "ja"
                AND tblPlattform.tf_technische_plattform NOT LIKE "%test%"
                AND tblPlattform.tf_technische_plattform NOT LIKE "CICS - T"
                AND tblPlattform.tf_technische_plattform NOT LIKE "%SAP%"

            ORDER BY tblUserIDundName.name, tblUserIDundName.userid, tblGesamt.tf
            ;

            -- Teil 2: Zeige zu allen AFs die Anzahl der darin befindlichen TFs

            -- Hole erst mal alle Kombinationen aus AF, TF und Plattform.
            DROP TABLE IF EXISTS dircon_aftfplatt;
            CREATE TABLE dircon_aftfplatt
            SELECT
                tblGesamt.enthalten_in_af as af,
                tblGesamt.tf as tf,
                tblPlattform.tf_technische_plattform as plattform,
                0 as Anzahl

            FROM `tblGesamt`
                INNER JOIN tblUserIDundName
                    ON tblGesamt.userid_und_name_id = tblUserIDundName.id
                INNER JOIN tblPlattform
                    ON tblGesamt.plattform_id = tblPlattform.id

            WHERE tblGesamt.enthalten_in_af != "ka"
                AND tblGesamt.enthalten_in_af != "AV"
                AND tblGesamt.enthalten_in_af != "XV"
                AND tblGesamt.enthalten_in_af != "DV"

            GROUP BY tblGesamt.enthalten_in_af, tblGesamt.tf
            ORDER BY tf, plattform, af
            ;

            -- Zähle die TFs, die zu einer AF gehören
            DROP TABLE IF EXISTS dircon_numtfs;
            CREATE TABLE dircon_numtfs
            SELECT
                af,
                count(tf) as `Anzahl`
            FROM dircon_aftfplatt
            GROUP BY af
            ORDER BY Anzahl ASC
            ;

            -- Und ergänze die Anzahl in der aftfplatt

            UPDATE dircon_aftfplatt
                INNER JOIN dircon_numtfs
                    ON dircon_aftfplatt.AF = dircon_numtfs.AF
            SET dircon_aftfplatt.Anzahl = dircon_numtfs.Anzahl
            ;

            -- Teil 3: Verbinde die Informationen geeignet für die TFen, die es in der AF-Liste gibt

            DROP TABLE IF EXISTS dircon_vorschlagsliste;
            CREATE TABLE dircon_vorschlagsliste
            SELECT     dircon_dircons.`name`,
                dircon_dircons.`userid`,
                dircon_dircons.`gruppe`,
                dircon_dircons.`tf`,
                dircon_dircons.`Plattform`,
                dircon_dircons.`tf_beschreibung`,
                "   " as leerfeld,
                dircon_aftfplatt.af as 'Vorschlag für AF',
                dircon_aftfplatt.Anzahl as 'Anzahl TFen in AF'

            FROM `dircon_dircons`
               INNER JOIN dircon_aftfplatt
                  ON dircon_dircons.tf = dircon_aftfplatt.tf
                     AND dircon_dircons.Plattform = dircon_aftfplatt.plattform

            ORDER BY
                dircon_dircons.`gruppe`,
                dircon_dircons.`name`,
                dircon_dircons.`userid`,
                dircon_dircons.`tf`,
                dircon_dircons.`Plattform`
            ;


            -- Teil 4: Finde die TFen, die es NICHT in der AF-Liste gibt

            DROP TABLE IF EXISTS dircon_nichtModelliert;
            CREATE TABLE dircon_nichtModelliert
            SELECT     dircon_dircons.`name`,
                dircon_dircons.`userid`,
                dircon_dircons.`gruppe`,
                dircon_dircons.`tf`,
                dircon_dircons.`Plattform`,
                dircon_dircons.`tf_beschreibung`,
                "   " as leerfeld,
                dircon_aftfplatt.af as 'Vorschlag für AF',
                dircon_aftfplatt.Anzahl as 'Anzahl TFen in AF'

            FROM `dircon_dircons`
                LEFT JOIN dircon_aftfplatt
                ON dircon_dircons.tf = dircon_aftfplatt.tf
                    AND dircon_dircons.Plattform = dircon_aftfplatt.plattform

            WHERE dircon_aftfplatt.af is null
            ORDER BY
                dircon_dircons.`gruppe`,
                dircon_dircons.`name`,
                dircon_dircons.`userid`,
                dircon_dircons.`tf`,
                dircon_dircons.`Plattform`
            ;
        END
    """
    return push_sp("directConnects", sp, procs_schon_geladen)


def push_sp_af_umbenennen(procs_schon_geladen):
    """
    Mit der SP kann eine Menge an AFs konsistent umbenannt werden.
    Das ist bspw. interessant, wenn Organisaationen neu durchnummeriert werden.
    Derzeit wird diese SP nur manuell genutzt.

    Die SP erhält drei Parameter:
    altliste:  Liste der alten AF-Namen
    neuliste:  Liste der neuen Namen
    statusgedoens: InOutput-Parameter - Welche Umbenennungen haben geklappt, welche nicht
    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE af_umbenennen (
            INOUT altliste VARCHAR(16000),
            INOUT neuliste VARCHAR(16000),
            INOUT statusgedoens VARCHAR(16000)
        )
        proclabel: BEGIN
            DECLARE finished INTEGER DEFAULT 0;
            DECLARE AFalt TINYTEXT DEFAULT "";
            DECLARE AFneu TINYTEXT DEFAULT "";
            DECLARE intid BIGINT;
            DECLARE status int(1);

            -- declare cursor for change lines
            DEClARE curLine
                CURSOR FOR
                    SELECT id, alt, neu FROM altnachneu;

            -- declare NOT FOUND handler
            DECLARE CONTINUE HANDLER
                FOR NOT FOUND SET finished = 1;
            OPEN curLine;

            getLine: LOOP
                -- Leider werden die Variablen nicht auf null gesetzt,
                -- wenn eines der Selects unten fehlschlägt
                SET @check1 = null, @check3 = null;

                -- Zeile holen aus der Umsetz-Tabelle
                FETCH curLine INTO intid, AFalt, AFneu;
                IF finished = 1 THEN
                    LEAVE getLine;
                END IF;

                -- build list - Das kann dann irgendwann mal wieder weg, kostet nur RAM
                SET statusgedoens = CONCAT(statusgedoens, "S1: ");
                SET altliste = CONCAT(altliste, ",", AFalt);
                SET neuliste = CONCAT(neuliste, ",", AFneu);

                -- Wird das Element in den Tabellen gefunden?
                SELECT id INTO @check1 FROM `tblGesamt` WHERE `enthalten_in_af` = AFalt LIMIT 1;
                SELECT id INTO @check3 FROM `tbl_AFListe` WHERE `af_name` = AFalt LIMIT 1;

                SET statusgedoens = CONCAT(statusgedoens,
                    'check1 = ', IFNULL(@check1, 'false'),
                    ', check3 = ', IFNULL(@check3, 'false'),
                    '\n'
                );

                SET @allesok = IFNULL(@check1, false)
                    AND IFNULL(@check3, false);
                SET statusgedoens = CONCAT(statusgedoens, "S2:, allesok = ", @allesok, ', ');

                IF @allesok THEN
                    -- Hier kommen jetzt die SQLs rein
                    UPDATE tblGesamt
                    SET `enthalten_in_af` = AFneu
                    WHERE `enthalten_in_af` = AFalt;

                    UPDATE tbl_AFListe
                    SET `af_name` = AFneu
                    WHERE `af_name` = AFalt;

                    SET @check1 = -1, @check3 = -1;
                    SELECT id INTO @check1 FROM `tblGesamt` WHERE `enthalten_in_af` = AFalt LIMIT 1;
                    SELECT id INTO @check3 FROM `tbl_AFListe` WHERE `af_name` = AFalt LIMIT 1;

                    -- set "Status-Flags"
                    INSERT INTO altnachneu_status
                        SET status = CONCAT('Ok für ', AFalt,
                            ', check1 = ', IFNULL(@check1, 'false'),
                            ', check3 = ', IFNULL(@check3, 'false'),
                            ', intŝid = ', intid),
                            id = intid;
                ELSE
                    INSERT INTO altnachneu_status
                        SET status = CONCAT('Fehler in Abfrage für ', AFalt,
                            ', check1 = ', IFNULL(@check1, 'false'),
                            ', check3 = ', IFNULL(@check3, 'false'),
                            ', intŝid = ', intid),
                            id = intid;
                END IF;
                -- SET statusgedoens = CONCAT(statusgedoens, "7 ");

            SET finished = 0; -- Der Status bezieht sich nur auf das Nicht-Finden des Suchstrings
            END LOOP getLine;
            CLOSE curLine;

            UPDATE altnachneu INNER JOIN altnachneu_status ON altnachneu.id = altnachneu_status.id
            SET altnachneu.status = altnachneu_status.status;

            INSERT INTO altnachneuHistorie
                SELECT 0 as `id`, `alt`, `neu`, `status` FROM altnachneu;

        END
    """
    return push_sp("AF_umbenennen", sp, procs_schon_geladen)


def push_sp_ungenutzte_teams(procs_schon_geladen):
    """
    Ermittle die Liste von Teams, denen keinen User zugeordnet sind.
    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE ungenutzteTeams()
        BEGIN
            DROP TABLE IF EXISTS genutzte;
            CREATE TEMPORARY TABLE genutzte
                SELECT orga_id, tblOrga.team FROM `tblUserIDundName`
                INNER JOIN tblOrga
                    ON tblUserIDundName.orga_id = tblOrga.id
                GROUP BY orga_id;

            SELECT tblOrga.id, tblOrga.team from tblOrga
            LEFT JOIN genutzte
                ON tblOrga.id = genutzte.orga_id

            WHERE
                (tblOrga.teamliste = "" OR tblOrga.teamliste is null)
                AND (tblOrga.freies_team = "" OR tblOrga.freies_team is null)
                AND genutzte.orga_id is null;
        END
    """
    return push_sp("ungenutzteTeams", sp, procs_schon_geladen)


def push_sp_rolle_umbenennen(procs_schon_geladen):
    """
    Benenne eine Rolle konsisten um
    Die SP erhält zwei Parameter:
    von:    alter Name - muss als Rolle vorhanden sein
    nach:   neuer Name: Darf als Rolle aktuell nicht vorhanden sein
    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
    CREATE PROCEDURE rolle_umbenennen (
        IN von VARCHAR(100),
        IN nach VARCHAR(100)
    )
    BEGIN
        START TRANSACTION;
            SET FOREIGN_KEY_CHECKS = 0;
            UPDATE tbl_Rollen
            SET rollenname = nach
            WHERE rollenname = von;

            UPDATE tbl_RolleHatAF
            SET rollenname = nach
            WHERE rollenname = von;

            UPDATE tbl_UserHatRolle
            SET rollenname = nach
            WHERE rollenname = von;

            SET FOREIGN_KEY_CHECKS = 1;
        COMMIT;
    END
    """
    return push_sp("Rolle_umbenennen", sp, procs_schon_geladen)


def push_sp_ungenutzte_afgf(procs_schon_geladen):
    """
    Finde alle ungenutzten AFen, also solche, die nicht in mindestens einer Rolle eingesetzt sind.

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """
    sp = """
        CREATE PROCEDURE ungenutzteAFGF()
        BEGIN
            DROP TABLE IF EXISTS alleAFGF;

            CREATE TEMPORARY TABLE alleAFGF
                SELECT DISTINCT `enthalten_in_af`,
                    `gf`,
                    modell,
                    geloescht
                FROM `tblGesamt`
                UNION
                SELECT DISTINCT `enthalten_in_af`,
                    `gf`,
                    modell,
                    geloescht
                FROM `tblGesamtHistorie`
                GROUP BY enthalten_in_af, gf;

            ALTER TABLE `RechteDB`.`alleAFGF` ADD INDEX `modell` (modell);

            SELECT
                tblUEbersichtAF_GFs.id,
                tblUEbersichtAF_GFs.name_af_neu,
                tblUEbersichtAF_GFs.name_gf_neu,
                alleAFGF.geloescht as 'tf_geloescht',
                tblUEbersichtAF_GFs.geloescht as 'afgf_ungenutzt'
            FROM tblUEbersichtAF_GFs
            LEFT JOIN alleAFGF
                ON alleAFGF.modell = tblUEbersichtAF_GFs.id

            WHERE alleAFGF.enthalten_in_af is null
            ORDER BY name_af_neu, name_gf_neu;
        END
    """
    return push_sp("ungenutzteAFGF", sp, procs_schon_geladen)


def push_sp_rollen_fuer_NPU(procs_schon_geladen):
    """
    erzeuge Rollen für jeden NPU und hänge alle AF ders NPU an diese Rolle

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        CREATE PROCEDURE rollen_fuer_NPU()
        BEGIN
            -- -----------------------------------------------------
            -- -----------------------------------------------------
            -- -----------------------------------------------------
            --
            -- Aktualisiere Spezialrollen für Technische User
            --
            -- -----------------------------------------------------
            -- -----------------------------------------------------
            -- -----------------------------------------------------

            --
            -- Erzeuge neue Rollen für neue Technische User
            -- Diese Rollen sind dann erst einmal "leer", haben also keine AFs zugeordnet.
            -- Die Länge der Rollennamen wird auf 90 begrenzt,
            -- damit ist noch Platz für 10 UTF-Sonderzeichen > 1Byte
            --

            START TRANSACTION;
                TRUNCATE `rapp_setze_npu_namen_status`;

                Insert INTO rapp_setze_npu_namen_status
                    SELECT
                        0 as id,
                        "Anzahl Rollen bei Transaktionsstart" as "Anzeige",
                        COUNT(*) as "Wert",
                        now() as Stamp
                    FROM tbl_Rollen
                    ;

                INSERT INTO tbl_Rollen
                    SELECT LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                            tblUserIDundName.name), 90) AS `rollenname`,
                        "Technischer User" AS `system`,
                        "" AS `rollenbeschreibung`,
                        now() AS `datum`
                        FROM `tblUserIDundName`
                        LEFT JOIN tbl_Rollen
                        ON LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                            tblUserIDundName.name), 90) = tbl_Rollen.rollenname

                    WHERE
                        tblUserIDundName.userid like "xv86%"
                            AND NOT tblUserIDundName.geloescht
                            AND tbl_Rollen.rollenname is null

                    ORDER BY tblUserIDundName.name
                ON DUPLICATE KEY UPDATE tbl_Rollen.`datum` = now()
                ;

                Insert INTO rapp_setze_npu_namen_status
                    SELECT
                        0 as id,
                        "Anzahl Rollen nach Erzeugung" as "Anzeige",
                        COUNT(*) as "Wert",
                        now() as Stamp
                    FROM tbl_Rollen
                    ;

                --
                -- Finde die AF je Technischem User
                --
                DROP TABLE IF EXISTS patchTU_alleAF;
                CREATE TABLE patchTU_alleAF
                SELECT DISTINCT LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                        tblUserIDundName.name), 90) AS `rollenname`,
                    tblUserIDundName.userid, tblUserIDundName.name,
                    tblGesamt.enthalten_in_af,
                    tbl_AFListe.id as af
                FROM tblGesamt
                    INNER JOIN `tblUserIDundName`
                    ON tblGesamt.userid_und_name_id = tblUserIDundName.id
                    LEFT JOIN tbl_AFListe
                    ON tblGesamt.enthalten_in_af = tbl_AFListe.af_name
                WHERE
                    tblUserIDundName.userid like "xv86%"
                        AND NOT tblUserIDundName.geloescht
                        AND NOT tblGesamt.geloescht
                        AND NOT tblGesamt.enthalten_in_af = "ka"
                ORDER BY tblUserIDundName.name
                ;

                --
                -- Finde vorhandene AFen zu Rollen technischer User
                --
                DROP TABLE IF EXISTS patchTU_bekannteTUAFKombinationen;
                CREATE TABLE patchTU_bekannteTUAFKombinationen
                SELECT DISTINCT tblUserIDundName.name,
                    tblUserIDundName.userid,
                    tbl_Rollen.rollenname,
                    tbl_RolleHatAF.af,
                    tbl_AFListe.af_name
                FROM `tblUserIDundName`
                INNER JOIN tbl_Rollen
                    ON LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                        tblUserIDundName.name), 90) = tbl_Rollen.rollenname
                    INNER JOIN tbl_RolleHatAF
                        ON tbl_Rollen.rollenname = tbl_RolleHatAF.rollenname
                        LEFT JOIN tbl_AFListe
                            ON tbl_RolleHatAF.af = tbl_AFListe.id
                ;

                /*
                --
                -- Finde die Unterschiede (Nur Anzeige zum Checken)
                --
                SELECT patchTU_alleAF.*,
                    patchTU_bekannteTUAFKombinationen.*
                FROM `patchTU_alleAF`
                LEFT JOIN patchTU_bekannteTUAFKombinationen
                    ON patchTU_alleAF.rollenname = patchTU_bekannteTUAFKombinationen.rollenname
                        AND patchTU_alleAF.enthalten_in_af
                            = patchTU_bekannteTUAFKombinationen.af_name
                    INNER JOIN tbl_AFListe
                        ON patchTU_alleAF.enthalten_in_af = tbl_AFListe.af_name
                WHERE patchTU_bekannteTUAFKombinationen.af_name is null
                ;
                */

                --
                -- Und jetzt das schnelle Update
                --
                TRUNCATE Patch_tbl_RolleHatAF;
                INSERT INTO Patch_tbl_RolleHatAF
                SELECT
                            0 AS rollenmappingid,
                            1 AS mussfeld,
                            concat("Generiertes Recht für ", patchTU_alleAF.name) AS bemerkung,
                            patchTU_alleAF.af AS af,
                            patchTU_alleAF.rollenname AS rollenname,
                            4 AS einsatz
                FROM `patchTU_alleAF`
                            LEFT JOIN patchTU_bekannteTUAFKombinationen
                    ON patchTU_alleAF.rollenname = patchTU_bekannteTUAFKombinationen.rollenname
                            AND patchTU_alleAF.enthalten_in_af
                                = patchTU_bekannteTUAFKombinationen.af_name
                                        INNER JOIN tbl_AFListe
                                        ON patchTU_alleAF.enthalten_in_af = tbl_AFListe.af_name
                WHERE patchTU_bekannteTUAFKombinationen.af_name is null
                ;


                -- Update Statustabelle
                Insert INTO rapp_setze_npu_namen_status
                SELECT
                    0 as id,
                    "Anzahl einzutragender Werte" as "Anzeige",
                    COUNT(*) as "Wert",
                    now() as Stamp
                FROM Patch_tbl_RolleHatAF
                ;

                Insert INTO rapp_setze_npu_namen_status
                SELECT
                    0 as id,
                    "Anzahl in tbl_RolleHatAF vorher" as "Anzeige",
                    COUNT(*) as "Wert",
                    now() as Stamp
                FROM tbl_RolleHatAF
                ;



                INSERT INTO tbl_RolleHatAF
                    SELECT
                        0 AS rollenmappingid,
                        Patch_tbl_RolleHatAF.mussfeld,
                        Patch_tbl_RolleHatAF.bemerkung,
                        Patch_tbl_RolleHatAF.af,
                        Patch_tbl_RolleHatAF.rollenname,
                        Patch_tbl_RolleHatAF.einsatz
                    FROM `Patch_tbl_RolleHatAF`
                ON DUPLICATE KEY UPDATE tbl_RolleHatAF.bemerkung
                    = concat("Doppeleintrag: ", tbl_RolleHatAF.bemerkung);

                Insert INTO rapp_setze_npu_namen_status
                SELECT
                    0 as id,
                    "Anzahl nicht eingetragener Werte" as "Anzeige",
                    COUNT(*) as "Wert",
                    now() as Stamp
                FROM `Patch_tbl_RolleHatAF`
                LEFT JOIN tbl_Rollen
                    ON Patch_tbl_RolleHatAF.rollenname = tbl_Rollen.rollenname
                WHERE tbl_Rollen.rollenname is null
                ;


                Insert INTO rapp_setze_npu_namen_status
                SELECT
                    0 as id,
                    "Anzahl in tbl_RolleHatAF nach Inserts" as "Anzeige",
                    COUNT(*) as "Wert",
                    now() as Stamp
                FROM tbl_RolleHatAF
                ;

                DROP TABLE IF EXISTS patchTU_bekannteTUAFKombinationen;
                DROP TABLE IF EXISTS patchTU_alleAF;

                --
                -- Aktualisiere Spezialrollen für Technische User
                --   Rollen müssen bereits bestehen und mit AFen verknüpft sein
                --

                INSERT INTO tbl_UserHatRolle
                    SELECT 0 as userundrollenid,
                        "Schwerpunkt" AS schwerpunkt_vertretung,
                        "Spezifische Rolle für Technischen User" AS `bemerkung`,
                        now() AS `letzte_aenderung`,
                        LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                            tblUserIDundName.name), 90) AS `rollenname`,
                        tblUserIDundName.userID,
                        null as id

                        FROM `tblUserIDundName`
                        LEFT JOIN tbl_Rollen
                            ON LEFT(concat("NPU: ", tblUserIDundName.userID, "-",
                                tblUserIDundName.name), 90) = tbl_Rollen.rollenname

                    WHERE
                        tblUserIDundName.userid like "xv86%"
                            AND NOT tblUserIDundName.geloescht
                            AND tbl_Rollen.rollenname is not null
                    ORDER BY tblUserIDundName.name
                ON DUPLICATE KEY UPDATE tbl_UserHatRolle.`letzte_aenderung` = now()
                ;

                Insert INTO rapp_setze_npu_namen_status
                SELECT
                    0 as id,
                    "Anzahl in tbl_UserHatRolle nach Verbindung der Rollen mit den Usern"
                        as "Anzeige",
                    COUNT(*) as "Wert",
                    now() as Stamp
                FROM tbl_UserHatRolle
                ;

                SELECT * FROM rapp_setze_npu_namen_status;
            COMMIT;
        END
    """
    return push_sp("rollen_fuer_NPU", sp, procs_schon_geladen)


def push_sp_muss_kann_liste(procs_schon_geladen):
    """
    Erzeuge eine Liste mit allen Rollen für eine angegebene Organisation.
    Zu den Rollen führe alle AFen auf sowie die aktuelle Vergabesituation
    dieser AFen für die einzelnen User der Organisation.
    Weiterhin zeige die aktuelle Muss-/Kann-Einstellung für die AF ind er Rolle an.

    :param procs_schon_geladen: wird transparent an push_sp weitergereicht
    :return: den Returnwert von push_sp
    """

    sp = """
        CREATE PROCEDURE muss_kann_rechte(
            IN gruppierung VARCHAR(100)
        )
        BEGIN
            DROP TABLE IF EXISTS lookformust_rau;
            CREATE TABLE lookformust_rau
                SELECT 	tbl_RolleHatAF.rollenname,
                        af_name,
                        mussfeld,
                        CONCAT('_', RIGHT(tbl_UserHatRolle.userid,
                            LENGTH(tbl_UserHatRolle.userid)-1)) as wcUserid,
                        (SELECT tblUserIDundName.name
                            FROM tblUserIDundName WHERE tblUserIDundName.userid
                                = tbl_UserHatRolle.userid) as name,
                        tbl_UserHatRolle.userundrollenid,
                        tbl_RolleHatAF.rollenmappingid
                FROM tbl_RolleHatAF
                    INNER JOIN tbl_AFListe ON tbl_RolleHatAF.af = tbl_AFListe.id
                    INNER JOIN tbl_UserHatRolle ON tbl_RolleHatAF.rollenname
                            = tbl_UserHatRolle.rollenname
                        AND tbl_UserHatRolle.userid in (
                            SELECT tblUserIDundName.userid FROM tblUserIDundName
                            WHERE NOT tblUserIDundName.geloescht
                                AND NOT (tblUserIDundName.userid LIKE 'xv86%'
                                    OR tblUserIDundName.userid LIKE 'xv84%')
                                AND tblUserIDundName.gruppe LIKE gruppierung
                    )
                GROUP BY rollenname, af_name, wcUserid
            ;

            -- Nun folgt die Liste der vorhandenen AFen aus der Gesamttabelle,
            -- die zu lookformust_rau passen
            DROP TABLE IF EXISTS lookformust_ist;
            CREATE TABLE lookformust_ist
                SELECT lookformust_rau.rollenname,
                    tblGesamt.enthalten_in_af,
                    tblUserIDundName.userid,
                    tblUserIDundName.name
                FROM tblGesamt
                    INNER JOIN tblUserIDundName
                    ON tblGesamt.userid_und_name_id = tblUserIDundName.id
                        AND NOT (tblUserIDundName.userid LIKE 'xv86%'
                            OR tblUserIDundName.userid LIKE 'xv84%')
                    INNER JOIN lookformust_rau
                        ON tblUserIDundName.userid like lookformust_rau.wcUserid
                        AND tblGesamt.enthalten_in_af = lookformust_rau.af_name
                GROUP BY lookformust_rau.rollenname, tblGesamt.enthalten_in_af,
                    tblUserIDundName.userid
                ORDER BY lookformust_rau.rollenname, tblGesamt.enthalten_in_af,
                    tblUserIDundName.name, tblUserIDundName.userid DESC
            ;

            -- Das Delta: Welche Rollen/AF-Kombinationen fehlt ein User, der aber die Rolle hat?
            DROP TABLE IF EXISTS lookformust_erg;
            CREATE TABLE lookformust_erg
                SELECT
                    lookformust_rau.rollenname,
                    lookformust_rau.af_name,
                    lookformust_ist.enthalten_in_af,
                    lookformust_rau.wcUserid,
                    lookformust_ist.userid,
                    lookformust_ist.name,
                    lookformust_rau.mussfeld,
                    (SELECT tblUserIDundName.name FROM tblUserIDundName
                        WHERE tblUserIDundName.userid
                            LIKE lookformust_rau.wcUserid LIMIT 1) as name_vn,
                    lookformust_rau.userundrollenid,
                    lookformust_rau.rollenmappingid
                FROM `lookformust_rau`
                    LEFT JOIN lookformust_ist
                        ON lookformust_ist.userid LIKE lookformust_rau.wcUserid
                        AND lookformust_ist.rollenname = lookformust_rau.rollenname
                        AND lookformust_ist.enthalten_in_af = lookformust_rau.af_name
                GROUP BY
                    lookformust_rau.rollenname,
                    lookformust_rau.af_name,
                    lookformust_rau.wcUserid,
                    lookformust_ist.name
                ORDER BY
                    lookformust_rau.rollenname,
                    lookformust_rau.af_name,
                    lookformust_ist.userid,
                    lookformust_ist.name
            ;
        END
    """
    return push_sp("muss_kann_rechte", sp, procs_schon_geladen)


# noinspection PyBroadException
def anzahl_procs() -> int:
    """
    Suche nach Stored Procedures in der aktuellen Datenbank.

    :return: Anzahl an derzeit geladenen Stored Procedures
    """
    anzahl = 0
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "show procedure status where db like (select DATABASE())")
            anzahl = cursor.rowcount
        except:
            e = sys.exc_info()[0]
            print("Error in finde_procs(): {}".format(e))

        cursor.close()
    return anzahl


def finde_procs() -> bool:
    """
    Bewerte, ob mindestens eine Stored Procedure geladen ist.

    :return: True, gdw mindestens eine SP geladen ist
    """
    return anzahl_procs() > 0


def finde_procs_exakt() -> bool:
    """
    Vergleiche die Zahl geladener SPs mit der Zahl aktuell geforderter SPs.

    :return: True gdw die beiden Zahlen gleich sind
    """
    return anzahl_procs() == soll_procs()


def soll_procs() -> int:
    """
    Liefere die Zahl an SPs, die aktuell definiert sind.

    :return: Eben diese Zahl
    """
    return len(sps)


"""Hier stehen die Namen der Stored Procedures. Darüber wird die Zahl aktueller SPs ermittelt."""
sps = {
    1: push_sp_anzahl_import_elemente,
    2: push_sp_vorbereitung,
    3: push_sp_neue_user,
    4: push_sp_behandle_user,
    5: push_sp_behandle_rechte,
    6: push_sp_loesche_doppelte_rechte,
    7: push_sp_erzeuge_af_liste,
    8: push_sp_ueberschreibe_modelle,
    9: push_sp_direct_connects,
    10: push_sp_af_umbenennen,
    11: push_sp_ungenutzte_teams,
    12: push_sp_rolle_umbenennen,
    13: push_sp_ungenutzte_afgf,
    14: push_sp_rollen_fuer_NPU,
    15: push_sp_muss_kann_liste,
}


@login_required
def handle_stored_procedures(request):
    """
    Behandle den Import von Stored-Procedures in die Datenbank.

    :param request: Der HTTP-Request, mit dem die Funktion gerufen wurde
    :return: Das gerenderte HTML mit dem Ergebnis
    """
    daten = {}

    if request.method == "POST":
        procs_schon_geladen = finde_procs()

        for i in range(len(sps)):
            daten[sps[i + 1].__name__] = sps[i + 1](procs_schon_geladen)

    return render(
        request,
        "rapp/stored_procedures.html",
        {
            "daten": daten,
        },
    )
