-- ------------------------------------------------------------
-- Hilfstabelle nutzen zum Mengenimport von Usern
--
-- Hilfstabelle wird nach dem Tabellenblatt der Importdatei benannt
-- In dieser Version liegt der Username bereits in der Form Nachname, Vorname vor.
-- ------------------------------------------------------------
BEGIN;

INSERT INTO tblUserIDundName
    SELECT
        0 as id,
        NeueUserXA.UserID as userid,
        concat(NeueUserXA.Nachname, ', ', NeueUserXA.Vorname) as name,
        NeueUserXA.orga as zi_organisation,
        0 as geloescht,
        NeueUserXA.Abteilung as abteilung,
        NeueUserXA.Gruppe as gruppe,
        35 as orga_id
    FROM NeueUserXA
ON DUPLICATE KEY UPDATE
    name = concat(NeueUserXA.Nachname, ', ', NeueUserXA.Vorname),
    zi_organisation = NeueUserXA.orga,
    geloescht = 0,
    abteilung = NeueUserXA.Abteilung,
    gruppe = NeueUserXA.Gruppe;


SELECT *
    FROM tblUserIDundName
    ORDER BY id DESC
    LIMIT 500;

SELECT COUNT(*) FROM tblUserIDundName
    WHERE geloescht = false AND zi_organisation = 'AI-XA';

ROLLBACK;
-- COMMIT
