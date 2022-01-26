-- Erzeuge Team-Zuordnungen
--   für Externe User
--   für Technische User und Schulungsuser
--   für interne User
-- Die User werden jeweils einer Gruppe zugeordnet.
-- Sollen die Tema feiner unterschieden werden, muss das SQL gegebenenfalls angepasst werden.


SELECT * FROM `tblUserIDundName`
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND(`userid` like "xv86%" OR `userid` like "xv84%");

UPDATE `tblUserIDundName`
    SET tblUserIDundName.orga_id = SPECIAL_TEAM
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND(`userid` LIKE "xv86%" OR `userid` LIKE "xv84%")
;


SELECT * FROM `tblUserIDundName`
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND `userid` like "xv88%";

UPDATE `tblUserIDundName`
    SET tblUserIDundName.orga_id = EXTERNES_TEAM
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND `userid` like "xv88%";

SELECT * FROM `tblUserIDundName`
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND `userid` not like "xv8%";

UPDATE `tblUserIDundName`
    SET tblUserIDundName.orga_id = INTERNES_TEAM
WHERE `gruppe` = "ZI-AI-ST-AK"
    AND `userid` not like "xv8%";
