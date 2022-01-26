SET @gruppierung = "ZI-AI-HA-DS";

-- Finde alle UserIDen der Technischen User, die mehr als eine Rolle zugeordnet haben
SELECT COUNT(*) as ct, `tbl_UserHatRolle`.`userid`, `rollenname` FROM `tbl_UserHatRolle`
    INNER JOIN tblUserIDundName
        ON tbl_UserHatRolle.userid = tblUserIDundName.userid
        AND (tblUserIDundName.zi_organisation LIKE @gruppierung OR tblUserIDundName.gruppe LIKE @gruppierung)
        AND `tbl_UserHatRolle`.`userid` like "xv86%"
GROUP BY `userid`
HAVING ct > 1
ORDER BY ct DESC, `rollenname` ASC
LIMIT 1000;


-- Gegebenenfalls hier erst mal aufräumen und doppelte Rollen entfernen
-- ToDo

-- Sammeln der betroffenen Rollen
DROP TABLE IF EXISTS clear_npu_quelle;
CREATE TABLE clear_npu_quelle
    SELECT `rollenname`,
        `tbl_UserHatRolle`.`userid`,
        tblUserIDundName.name,
        tblUserIDundName.zi_organisation,
        tblUserIDundName.gruppe
    FROM `tbl_UserHatRolle`
        INNER JOIN tblUserIDundName
            ON tbl_UserHatRolle.userid = tblUserIDundName.userid
            AND tblUserIDundName.userid LIKE 'xv86%'
            AND (tblUserIDundName.zi_organisation LIKE @gruppierung OR tblUserIDundName.gruppe LIKE @gruppierung)
;

-- Und erst mal zählen, was wir anrichten würden
-- Und erst mal zählen, was wir anrichten würden
SELECT COUNT(*) FROM clear_npu_quelle;


-- Entfernen der Rolle sowie der abhängigen Elemente user_hat_Rolle und Rolle_hat_AF.
-- Dazu müssen die Contraints der beiden abhängigen Tabellen entsprechend auf CASCADE gesetzt worden sein.

DELETE FROM tbl_Rollen
WHERE tbl_Rollen.rollenname in (
    SELECT clear_npu_quelle.rollenname FROM clear_npu_quelle
);

SELECT COUNT(*)
FROM `tbl_UserHatRolle`
    INNER JOIN tblUserIDundName
        ON tbl_UserHatRolle.userid = tblUserIDundName.userid
        AND tblUserIDundName.userid LIKE 'xv86%'
        AND (tblUserIDundName.zi_organisation LIKE @gruppierung OR tblUserIDundName.gruppe LIKE @gruppierung)
;
