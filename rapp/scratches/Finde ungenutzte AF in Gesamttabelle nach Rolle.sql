-- First commet line against Drop-Sec question

DROP PROCEDURE IF EXISTS af_check;
DELIMITER $$
CREATE PROCEDURE af_check(
	IN flag BOOLEAN,
	OUT anzahl1 INT,
	OUT anzahl2 INT
)
BEGIN
    -- Zweck der Gesamtübunbg:
    -- Ermittlung von AFen, die
    --   Rollen zugewiesenen sind,
    --   welche an die betrachtete Oragnisation vegeben sind,
    --   bei denen aber die jeweiligen AFen keinem der Mitglieder der Organisation vergeben sind
    --
    -- Damit lassen sich beispielsweise alte, umbenannte AFen finden.

    -- Schritt 1:
    -- Welche AFen sind in einer Org.Einheit vergeben?
	DROP TABLE IF EXISTS Bastel_ist;
	CREATE TABLE Bastel_ist
		SELECT `enthalten_in_af` AS af
		FROM `tblGesamt`
			INNER JOIN tblUserIDundName ON tblGesamt.userid_und_name_id = tblUserIDundName.id
			AND NOT tblUserIDundName.geloescht
			AND NOT tblGesamt.geloescht
		GROUP BY `enthalten_in_af`
	;

	-- Schritt 2:
	-- Welche AFen stehen in der Liste der zugewiesenen Rollen?

	DROP TABLE IF EXISTS Bastel_soll;
	CREATE TABLE Bastel_soll
		SELECT tbl_RolleHatAF.rollenname, tbl_AFListe.af_name
		FROM tbl_RolleHatAF
			INNER JOIN tbl_AFListe ON tbl_RolleHatAF.af = tbl_AFListe.id

		WHERE tbl_RolleHatAF.rollenname in (SELECT tbl_UserHatRolle.rollenname
			FROM tbl_UserHatRolle
				INNER JOIN tblUserIDundName ON tbl_UserHatRolle.userid = tblUserIDundName.userid
					AND NOT tblUserIDundName.geloescht
		)
		GROUP BY tbl_RolleHatAF.rollenname, tbl_AFListe.af_name
	;

	-- SELECT * FROM Bastel_soll;

	-- Schritt 3:
	-- Verbinden der beiden Tabellen

	DROP TABLE IF EXISTS Bastel_diff;
	CREATE TEMPORARY TABLE Bastel_diff
		SELECT `Bastel_soll`.`rollenname`,
			Bastel_soll.af_name AS 'VorgabeAF',
			Bastel_ist.af AS 'vergebeneAF'
		FROM `Bastel_soll`
			LEFT JOIN Bastel_ist ON Bastel_soll.af_name = Bastel_ist.af
		WHERE Bastel_ist.af is null
		ORDER BY VorgabeAF, rollenname
	;

	-- Entfernen der Einträge, die definitiv nicht gelöscht werden sollen
	-- Bspw. für Neumodellierungen, manuelle Vergabe besonderer Elemente etc.
	-- Auch wenn man das eigentlich vorher schon hätte machen können

	DELETE FROM Bastel_diff
		WHERE VorgabeAF = 'Direktverbindungen'
			OR VorgabeAF LIKE 'Manuell_%'
	;

	-- Nun noch optional das Löschen der überflüssigen AFen.
	-- Erst mal gucken: Die Zahl der gefundenen Einträge muss mit der Zahl der Einträge in Bastel_diff übereinstimmen
	DROP TABLE IF EXISTS Bastel_erg;
	CREATE TABLE Bastel_erg
		SELECT tbl_RolleHatAF.rollenmappingid, tbl_RolleHatAF.rollenname, tbl_AFListe.af_name, Bastel_diff.VorgabeAF
		FROM `tbl_RolleHatAF`
			INNER JOIN tbl_AFListe ON tbl_RolleHatAF.af = tbl_AFListe.id
			INNER JOIN Bastel_diff ON tbl_RolleHatAF.rollenname = Bastel_diff.rollenname
				AND tbl_AFListe.af_name = Bastel_diff.VorgabeAF;
	ALTER TABLE `RechteDB`.`Bastel_erg` ADD PRIMARY KEY (`rollenmappingid`);

	-- Zeige die Ergebniszahlen
	SET anzahl1 = (SELECT COUNT(*) AS anzahl1 FROM Bastel_diff);
	SET anzahl2 = (SELECT COUNT(*) AS anzahl2 FROM Bastel_erg);

-- Und dasselbe als DELETE:

	IF flag THEN
		DELETE FROM tbl_RolleHatAF
		WHERE tbl_RolleHatAF.rollenmappingid in (SELECT Bastel_erg.rollenmappingid FROM Bastel_erg);
	END IF;

END$$
DELIMITER ;


-- Ausführen und hinterher aufräumen
-- Flag: False = nur ansehen, true = Löschen durchführen
CALL af_check(false, @out1, @out2);
SELECT Bastel_logbuch.*, @out1, @out2 FROM Bastel_logbuch;
DROP PROCEDURE IF EXISTS af_check;
-- DROP TABLE IF EXISTS Bastel_erg;
