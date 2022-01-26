-- ----------------------------------------------------------
-- Alte, gelöschte Rechte in die Historie verlagern
-- ----------------------------------------------------------
BEGIN;
    SELECT COUNT(*) FROM tblGesamtHistorie
    INNER JOIN tblUserIDundName
        ON tblGesamtHistorie.userid_und_name_id = tblUserIDundName.id
    WHERE tblUserIDundName.zi_organisation = 'AI-XA';

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
        INNER JOIN tblUserIDundName
            ON tblGesamt.userid_und_name_id = tblUserIDundName.id

        WHERE tblUserIDundName.zi_organisation = 'AI-XA'
            AND tblGesamt.geloescht
    ;

    SELECT COUNT(*) FROM tblGesamtHistorie
    INNER JOIN tblUserIDundName
        ON tblGesamtHistorie.userid_und_name_id = tblUserIDundName.id
    WHERE tblUserIDundName.zi_organisation = 'AI-XA';

    DELETE tblGesamt.* FROM tblGesamt
    INNER JOIN tblUserIDundName
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
    WHERE tblUserIDundName.zi_organisation = 'AI-XA'
        AND tblGesamt.geloescht;

    SELECT COUNT(*) FROM tblGesamt
    INNER JOIN tblUserIDundName
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
    WHERE tblUserIDundName.zi_organisation = 'AI-XA'
        AND tblGesamt.geloescht;

    SELECT COUNT(*) FROM tblGesamt
    INNER JOIN tblUserIDundName
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
    WHERE tblUserIDundName.zi_organisation = 'AI-XA'
    ;

ROLLBACK;
-- COMMIT;
