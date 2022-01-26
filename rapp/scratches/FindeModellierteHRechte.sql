CREATE TEMPORARY TABLE foo
    SELECT DISTINCT `enthalten_in_af`, `af_beschreibung`,
        `gf`, `gf_beschreibung`,
        `tf`, `tf_beschreibung`, `tf_kritikalitaet`,
        `zi_organisation`
    from tblGesamt
    INNER JOIN tblUserIDundName
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
    where not tblGesamt.geloescht AND not tblUserIDundName.geloescht
        AND tblUserIDundName.zi_organisation = 'AI-BA'
        AND enthalten_in_af in (SELECT DISTINCT `enthalten_in_af` FROM `tblGesamt` WHERE  `hk_tf_in_af` = 'h');

CREATE TEMPORARY TABLE sammlung
    SELECT COUNT(*) AS Anzahl, foo.* FROM foo GROUP BY foo.enthalten_in_af
    ORDER BY Anzahl DESC;

DROP TABLE IF EXISTS Bastel;
CREATE TABLE Bastel
    SELECT foo.* FROM foo
    INNER JOIN sammlung
        ON foo.enthalten_in_af = sammlung.enthalten_in_af
        AND sammlung.Anzahl > 1
    ORDER BY foo.enthalten_in_af, foo.gf, foo.tf
;
