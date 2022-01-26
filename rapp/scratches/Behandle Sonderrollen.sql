-- Erstelle Tabelle mit Sonderrechten
DROP TABLE IF EXISTS Bastel;
CREATE TABLE Bastel
    SELECT tbl_RolleHatAF.rollenname, tbl_AFListe.af_name
    FROM tbl_RolleHatAF
        INNER JOIN tbl_AFListe
        ON tbl_RolleHatAF.af = tbl_AFListe.id
    WHERE tbl_RolleHatAF.rollenname like "%sonder%"
    ORDER BY tbl_RolleHatAF.rollenname, tbl_AFListe.af_name
;

SELECT * FROM Bastel;


-- Finde alle AFen zu allen Usern der Abteilung,
-- bei denen die AF zu einer der Sonderrollen passt.
-- Das Ergebnis steht dann in Bastel1.

DROP TABLE IF EXISTS Bastel1;
CREATE TABLE Bastel1
    SELECT
        tblUserIDundName.userid,
        tblUserIDundName.name,
        tblUserIDundName.gruppe,
        Bastel.rollenname,
        Bastel.af_name
    FROM tblGesamt

        INNER JOIN tblUserIDundName
        ON tblGesamt.userid_und_name_id = tblUserIDundName.id
            AND NOT tblGesamt.geloescht
            AND NOT tblUserIDundName.geloescht
            AND tblUserIDundName.zi_organisation = "AI-BA"
            INNER JOIN Bastel
            ON tblGesamt.enthalten_in_af = Bastel.af_name
    GROUP BY
        Bastel.af_name,
        tblUserIDundName.gruppe,
        Bastel.rollenname
;


-- Finde alle AFen bei den Sonderrechten,
-- die keinem User (in Abteilung) zugeordnet sind

SELECT
    tblUserIDundName.userid,
    tblUserIDundName.name,
    tblUserIDundName.gruppe,
    tblGesamt.enthalten_in_af AS AF,
    Bastel.rollenname,
    Bastel.af_name
FROM tblGesamt
    INNER JOIN tblUserIDundName
    ON tblGesamt.userid_und_name_id = tblUserIDundName.id
        AND NOT tblGesamt.geloescht
        AND NOT tblUserIDundName.geloescht
        AND tblUserIDundName.zi_organisation = "AI-BA"
    RIGHT JOIN Bastel
    ON tblGesamt.enthalten_in_af = Bastel.af_name
WHERE tblGesamt.enthalten_in_af is null
;
