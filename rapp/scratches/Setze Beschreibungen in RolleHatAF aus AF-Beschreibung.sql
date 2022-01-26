-- Aktualisiere die Bemerkungsfelder in RollaHatAF mit den AF-Beschreibungen der adressierten Berechtigungen

-- Finde die jüngste AF-Verwendung in der Gesamttabelle
-- Damit ist sichergestellt, dass der aktuelle Text genommen wird
-- Damit das nachher schnell geht, wird eine separate Tabelle mit Index auf den AF-Namen angelegt.
--
-- Unten muss eingestellt werden:
--     Die Daten, um die Rollen zu selektieren
--    Ob auch schon vorhandene Beschreibungen aktuialilsiert, oder nur Leerfelder gefüllt werden sollen

DROP TABLE IF EXISTS tbl_AFBeschreibungen;
CREATE TABLE tbl_AFBeschreibungen
    SELECT t.`enthalten_in_af` AS af, t.maxid AS id,
    (SELECT af_beschreibung FROM tblGesamt WHERE tblGesamt.id = t.maxid) AS af_beschreibung
    FROM (
        SELECT `enthalten_in_af`, MAX(id) as maxid
        FROM `tblGesamt`
        WHERE NOT geloescht
        GROUP BY `enthalten_in_af`
    ) t
    -- WHERE t.`enthalten_in_af` LIKE 'rva_00220_kfall%'
    ORDER BY t.`enthalten_in_af`
;

ALTER TABLE tbl_AFBeschreibungen ADD CONSTRAINT uk_af UNIQUE (af);

-- SELECT * from tbl_AFBeschreibungen;

SET @gruppierung = 'HA-DL%';

-- Vergleiche die vorhandenen Daten (Beschreibungen) mit den aktuell geholten Daten
SELECT
    tbl_RolleHatAF.`rollenname`,
    tbl_AFListe.af_name,
    tbl_RolleHatAF.bemerkung,
    tbl_AFBeschreibungen.af_beschreibung
FROM `tbl_RolleHatAF`
    INNER JOIN tbl_AFListe ON `tbl_RolleHatAF`.`af` = tbl_AFListe.id
        INNER JOIN tbl_AFBeschreibungen ON tbl_AFListe.af_name = tbl_AFBeschreibungen.af
WHERE tbl_RolleHatAF.rollenname like @gruppierung
    -- AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung != tbl_AFBeschreibungen.af_beschreibung)
    AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung = '')
;

-- Und Update
BEGIN;
    UPDATE `tbl_RolleHatAF`
        INNER JOIN tbl_AFListe ON `tbl_RolleHatAF`.`af` = tbl_AFListe.id
            INNER JOIN tbl_AFBeschreibungen ON tbl_AFListe.af_name = tbl_AFBeschreibungen.af
    SET tbl_RolleHatAF.bemerkung = tbl_AFBeschreibungen.af_beschreibung
    WHERE tbl_RolleHatAF.rollenname like @gruppierung
        -- AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung != tbl_AFBeschreibungen.af_beschreibung)
        AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung = '')
    ;

    SELECT
        tbl_RolleHatAF.`rollenname`,
        tbl_AFListe.af_name,
        tbl_RolleHatAF.bemerkung,
        tbl_AFBeschreibungen.af_beschreibung
    FROM `tbl_RolleHatAF`
        INNER JOIN tbl_AFListe ON `tbl_RolleHatAF`.`af` = tbl_AFListe.id
            INNER JOIN tbl_AFBeschreibungen ON tbl_AFListe.af_name = tbl_AFBeschreibungen.af
    WHERE tbl_RolleHatAF.rollenname like @gruppierung
        -- AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung != tbl_AFBeschreibungen.af_beschreibung)
        AND (tbl_RolleHatAF.bemerkung is NULL OR tbl_RolleHatAF.bemerkung = '')
    ;
ROLLBACK;
