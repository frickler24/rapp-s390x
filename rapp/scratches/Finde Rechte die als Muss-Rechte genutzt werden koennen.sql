
-- Finde alle Kombinationen aus Rolle und AF_Name mit zugehöriger _V-Nummer

SET @gruppierung = 'ZI-AI-BA--';

DROP TABLE IF EXISTS lookformust_rau;
CREATE TABLE lookformust_rau
    SELECT 	tbl_RolleHatAF.rollenname,
            af_name,
            mussfeld,
            CONCAT('_', RIGHT(tbl_UserHatRolle.userid, LENGTH(tbl_UserHatRolle.userid)-1)) as wcUserid,
			(SELECT tblUserIDundName.name FROM tblUserIDundName WHERE tblUserIDundName.userid = tbl_UserHatRolle.userid) as name,
            tbl_UserHatRolle.userundrollenid,
            tbl_RolleHatAF.rollenmappingid
    FROM tbl_RolleHatAF
        INNER JOIN tbl_AFListe ON tbl_RolleHatAF.af = tbl_AFListe.id
        INNER JOIN tbl_UserHatRolle ON tbl_RolleHatAF.rollenname = tbl_UserHatRolle.rollenname
            AND tbl_UserHatRolle.userid in (
                SELECT tblUserIDundName.userid FROM tblUserIDundName
                WHERE NOT tblUserIDundName.geloescht
					AND NOT (tblUserIDundName.userid LIKE 'xv86%' OR tblUserIDundName.userid LIKE 'xv84%')
                    AND tblUserIDundName.gruppe LIKE @gruppierung
        )
	-- WHERE tbl_RolleHatAF.rollenname = 'AI-HA Cosmos+AIB' AND tbl_AFListe.af_name = 'rva_00763_web_log_p'
    GROUP BY rollenname, af_name, wcUserid
;

-- Nun folgt die Liste der vorhandenen AFen aus der Gesamttabelle, die zu lookformust_rau passen

DROP TABLE IF EXISTS lookformust_ist;
CREATE TABLE lookformust_ist
	SELECT lookformust_rau.rollenname,
		tblGesamt.enthalten_in_af,
		tblUserIDundName.userid,
		tblUserIDundName.name
	FROM tblGesamt
		INNER JOIN tblUserIDundName ON tblGesamt.userid_und_name_id = tblUserIDundName.id
			AND NOT (tblUserIDundName.userid LIKE 'xv86%' OR tblUserIDundName.userid LIKE 'xv84%')
		INNER JOIN lookformust_rau
			ON tblUserIDundName.userid like lookformust_rau.wcUserid
			AND tblGesamt.enthalten_in_af = lookformust_rau.af_name
			-- AND tblGesamt.enthalten_in_af = 'rva_00763_web_log_p'
	GROUP BY lookformust_rau.rollenname, tblGesamt.enthalten_in_af, tblUserIDundName.userid
	ORDER BY lookformust_rau.rollenname, tblGesamt.enthalten_in_af, tblUserIDundName.name, tblUserIDundName.userid DESC
-- LIMIT 100
;

-- Das Delta: Welche Rollen/AF-Kombinationen fehlt ein User, der aber die Rolle hat?
DROP TABLE IF EXISTS lookformust_erg;
CREATE TABLE lookformust_erg
    SELECT
        lookformust_rau.rollenname,
        lookformust_rau.af_name,
        lookformust_ist.enthalten_in_af,
        lookformust_rau.wcUserid,
        lookformust_ist.userid,
        lookformust_ist.name,
        lookformust_rau.mussfeld,
		(SELECT tblUserIDundName.name FROM tblUserIDundName WHERE tblUserIDundName.userid LIKE lookformust_rau.wcUserid LIMIT 1) as name_vn,
        lookformust_rau.userundrollenid,
        lookformust_rau.rollenmappingid

    FROM `lookformust_rau`
        LEFT JOIN lookformust_ist
            ON lookformust_ist.userid LIKE lookformust_rau.wcUserid
            AND lookformust_ist.rollenname = lookformust_rau.rollenname
            AND lookformust_ist.enthalten_in_af = lookformust_rau.af_name
    GROUP BY
        lookformust_rau.rollenname,
        lookformust_rau.af_name,
        lookformust_rau.wcUserid,
        lookformust_ist.name

    ORDER BY
        lookformust_rau.rollenname,
        lookformust_rau.af_name,
        lookformust_ist.userid,
        lookformust_ist.name
;

SELECT * FROM lookformust_erg;
