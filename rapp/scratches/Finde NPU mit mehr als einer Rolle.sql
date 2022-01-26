-- Erzeuge die Kontroll-Tabelle

DROP TABLE IF EXISTS RollenCheck;
CREATE TABLE RollenCheck
	SELECT a.userundrollenid, t.Anzahl, a.userid, a.rollenname
    FROM tbl_UserHatRolle a
    INNER JOIN (
            SELECT userid, rollenname, COUNT(*) AS Anzahl
            FROM `tbl_UserHatRolle`
            WHERE userid LIKE "xv86%"
            GROUP BY userid
            HAVING Anzahl > 1
            ORDER BY Anzahl, userid
        ) t ON a.userid = t.userid
;
ALTER TABLE `RollenCheck` ADD PRIMARY KEY( `userundrollenid`);
