SET @gruppe = 'ZI-AI-HA-IN';

SELECT `rollenmappingid`, `rollenname`, tbl_AFListe.af_name, `bemerkung`, `mussfeld`, `einsatz`
FROM tbl_RolleHatAF
	INNER JOIN tbl_AFListe ON tbl_RolleHatAF.af = tbl_AFListe.id
WHERE rollenname in (
    SELECT `rollenname` FROM tbl_UserHatRolle
    WHERE `userid` in (
        SELECT userid FROM `tblUserIDundName`
            WHERE `gruppe` = @gruppe
                AND NOT (`userid` like "_v86%" OR `userid` like "_v84%")
                AND `userid` like "xv%"
    )
    GROUP BY `rollenname`
)
ORDER BY `rollenname`, `af`
LIMIT 500
;
