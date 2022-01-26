-- ------------------------------------------------------------
-- Umbenennen von Arbeitsplatzfunktionen
--
-- Diese Funktionen werden benötigt, wenn in größerem Stil AFen umbenannt werden sollen.
-- Das ist insbesondere dann interessant, wenn sich die Organummern in den AF-Namen ändern,
-- bspw. bei Organisationsveränderungen oder Verschiebungen von Rechten zwischen den Organisationen.
--
-- Idee:
--  Es gibt eine Liste von Rechten mit altem und neuem Nammen
--  Diese Liste wird in den folgenden Tabellen angepasst:
--      tblGesamt
--          (nicht auch in der Historie, denn da waren die Namen ja noch korrekt;
--          Eventuelle sollte dort ein weiteres Feld eingefügt werden mit dem jewils aktuellen Namen)
--      tbl_AFListe
--      tblUEbersichtAF_GFs
-- ------------------------------------------------------------

-- Importiere die Liste der angeblich neuen Arbeitsplatzfunktionen mit ihren (evtl auch neuen) GFen.
-- Ein Beispiel ist dazu die other_files/neue_AFGF-AI-BA nach erster Umbenennung 20200222.ods

USE RechteDB;

--
-- Tabellenstruktur für Tabelle `Umb_AFGFListe`
--

DROP TABLE IF EXISTS `Umb_AFGFListe`;
CREATE TABLE `Umb_AFGFListe` (
  `AF` varchar(35) NOT NULL,
  `GF` varchar(35) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Daten für Tabelle `Umb_AFGFListe`
--

INSERT INTO `Umb_AFGFListe` (`AF`, `GF`) VALUES
('rva_00771_schaden', 'rvg_00005_#tsosegm'),
('rva_00771_schaden', 'rvg_00023_#gse0002'),
('rva_01858_45pclebenbpm', 'rvg_00028_bpm_user11'),
('rva_00051_ejm_pzg', 'rvg_00051_ejm_pzg'),
('rva_00771_schaden', 'rvg_00279_a_cc_t_kb'),
('rva_00411_magazin', 'rvg_00411_magazin'),
('rva_00770_Personen', 'rvg_00458_07amunfall'),
('rva_00770_Personen', 'rvg_00458_45amblu'),
('rva_00770_Personen', 'rvg_00458_45amlebenbpm'),
('rva_00770_Personen', 'rvg_00458_46amllei-rbm'),
('rva_00770_Personen', 'rvg_00458_4xampersueg'),
('rva_00458_cam_r_ws_kp_dl_antwort', 'rvg_00458_cam_r_ws_kp_dl_antwort'),
('rva_00458_cam_s_ws_kp_dl_antwort', 'rvg_00458_cam_s_ws_kp_dl_antwort'),
('rva_00458_cam_t_ws_kp_dl_antwort', 'rvg_00458_cam_t_ws_kp_dl_antwort'),
('rva_00771_55pckfz', 'rvg_00626_ppnm010_1'),
('rva_00771_12ewsadtfs', 'rvg_00742_d_assad'),
('rva_00771_schaden', 'rvg_00742_edm6115_3'),
('rva_00771_12schadenbpm', 'rvg_00742_kumul_verw_t'),
('rva_01858_kranken', 'rvg_00763_web_log_r'),
('rva_01858_kranken', 'rvg_00763_web_log_s'),
('rva_00770_#opct97', 'rvg_00770_#opct97'),
('rva_00770_#qpdb97r', 'rvg_00770_#qpdb97r'),
('rva_00770_#qpdb97u', 'rvg_00770_#qpdb97u'),
('rva_00770_#qpse482', 'rvg_00770_#qpse482'),
('rva_00770_#qpse974', 'rvg_00770_#qpse974'),
('rva_00770_#qrse451', 'rvg_00770_#qrse451'),
('rva_00770_#qrse482', 'rvg_00770_#qrse482'),
('rva_00770_#qrse974', 'rvg_00770_#qrse974'),
('rva_00770_#qsse451', 'rvg_00770_#qsse451'),
('rva_00770_#qsse482', 'rvg_00770_#qsse482'),
('rva_00770_#qsse974', 'rvg_00770_#qsse974'),
('rva_00770_#qtse482', 'rvg_00770_#qtse482'),
('rva_00770_#qtse974', 'rvg_00770_#qtse974'),
('rva_00770_#quse45a', 'rvg_00770_#quse45a'),
('rva_00770_#quse97a', 'rvg_00770_#quse97a'),
('rva_00770_Personen', 'rvg_00770_07ewunfall'),
('rva_00770_Personen', 'rvg_00770_40ewrkv'),
('rva_00770_40PCRKV', 'rvg_00770_40pcrkv'),
('rva_00770_Personen', 'rvg_00770_42ewlebenma'),
('rva_00770_42PCLebenMA', 'rvg_00770_42pclebenma'),
('rva_00770_Personen', 'rvg_00770_44ewlgp_marz'),
('rva_00770_44PCLGP_Marz', 'rvg_00770_44pclgp_marz'),
('rva_00770_Personen', 'rvg_00770_45ewblu'),
('rva_00770_45ewblukiss', 'rvg_00770_45ewblukiss'),
('rva_00770_45PCBLU', 'rvg_00770_45pcblu'),
('rva_00770_Personen', 'rvg_00770_46ewllei-rbm'),
('rva_00770_46PCLLei-RBM', 'rvg_00770_46pcllei-rbm'),
('rva_00770_Personen', 'rvg_00770_48ewveritas'),
('rva_00770_48PCVeritas', 'rvg_00770_48pcveritas'),
('rva_00770_Personen', 'rvg_00770_49ewlebendiv'),
('rva_00770_49PCLebenDiv', 'rvg_00770_49pclebendiv'),
('rva_00770_4xPCPersUeG', 'rvg_00770_4xpcpersueg'),
('rva_00770_79ewqlikview', 'rvg_00770_79ewqlikview'),
('rva_00770_Personen', 'rvg_00770_80ewpension'),
('rva_00770_80PCPension', 'rvg_00770_80pcpension'),
('rva_00770_97pcgdv', 'rvg_00770_97pcgdv'),
('rva_00770_97pcpvducato', 'rvg_00770_97pcpvducato'),
('rva_00770_97tupms_ftp', 'rvg_00770_97tupms_ftp'),
('rva_00770_ftp_badia_t', 'rvg_00770_ftp_badia_t'),
('rva_00770_lebm207_1', 'rvg_00770_lebm207_1'),
('rva_00770_mqsm040_1', 'rvg_00770_mqsm040_1'),
('rva_00771_schaden', 'rvg_00771_#a12ko01'),
('rva_00771_schaden', 'rvg_00771_#a12mvs'),
('rva_00771_12pcschaden', 'rvg_00771_#a12stg'),
('rva_00771_schaden', 'rvg_00771_#a67ko01'),
('rva_00771_#lgkneu', 'rvg_00771_#lgkneu'),
('rva_00771_schaden', 'rvg_00771_#qpse121'),
('rva_00771_schaden', 'rvg_00771_#qrse121'),
('rva_00771_schaden', 'rvg_00771_#qsse121'),
('rva_00771_schaden', 'rvg_00771_#qtse121'),
('rva_00771_12schaden', 'rvg_00771_#quse12a'),
('rva_00771_kfz', 'rvg_00771_#quse34a'),
('rva_00771_kfz', 'rvg_00771_#quse39a'),
('rva_00771_kfz', 'rvg_00771_#quse55a'),
('rva_00771_schaden', 'rvg_00771_#se1200e'),
('rva_00771_schaden', 'rvg_00771_#se6700e'),
('rva_00771_schaden', 'rvg_00771_#t12gr0'),
('rva_00771_schaden', 'rvg_00771_#t12gr4'),
('rva_00771_schaden', 'rvg_00771_#t67duv'),
('rva_00771_schaden', 'rvg_00771_#txt125'),
('rva_00771_schaden', 'rvg_00771_#txt675'),
('rva_00771_12amsadtfsbld', 'rvg_00771_12amsadtfsbld'),
('rva_00771_12schadenbpm', 'rvg_00771_12amschadbpm'),
('rva_00771_12schaden', 'rvg_00771_12amschaden'),
('rva_00771_12ewsadtfs', 'rvg_00771_12ewsadtfs'),
('rva_00771_12schadenbpm', 'rvg_00771_12ewschadbpm'),
('rva_00771_12schaden', 'rvg_00771_12ewschaden'),
('rva_00771_12ewschdx4we', 'rvg_00771_12ewschdx4we'),
('rva_00771_12pcsadtfs', 'rvg_00771_12pcsadtfs'),
('rva_00771_12pcschadenbpm', 'rvg_00771_12pcschadbpm'),
('rva_00771_12pcschaden', 'rvg_00771_12pcschaden'),
('rva_00771_kfz', 'rvg_00771_34ewhuh'),
('rva_00771_34pchuh', 'rvg_00771_34pchuh'),
('rva_00771_kfz', 'rvg_00771_39ammoped'),
('rva_00771_kfz', 'rvg_00771_39ewmoped'),
('rva_00771_39pcmoped', 'rvg_00771_39pcmoped'),
('rva_00771_kfz', 'rvg_00771_55amkfz'),
('rvz_00771_55dvkfz_bonip', 'rvg_00771_55dvkfz_bonip'),
('rvz_00771_55dvkfz_bonis', 'rvg_00771_55dvkfz_bonis'),
('rva_00771_kfz', 'rvg_00771_55ewkfz'),
('rva_00771_55pckfz', 'rvg_00771_am_kfz'),
('rva_00771_12pcschaden', 'rvg_00771_gks_admin_prod'),
('rva_00771_12schadenbpm', 'rvg_00771_gks_admin_test'),
('rva_00771_pmsharvkomp', 'rvg_00771_pmsharvkomp'),
('rvz_00771_pms_control', 'rvg_00771_pms_control'),
('rva_00771_pms_harvest_l', 'rvg_00771_pms_harvest_l'),
('rvz_00771_sadadmin', 'rvg_00771_sadadmin'),
('rva_00771_sdx_kfz_trust', 'rvg_00771_sdx_kfz_trust'),
('rva_00771_schaden', 'rvg_00788_#se9298e'),
('rva_01858_kranken', 'rvg_00788_jenkg_puser03'),
('rva_01045_kolumbus_admin', 'rvg_01045_kolumbus_admin'),
('rva_01045_kolumbus_batch', 'rvg_01045_kolumbus_batch'),
('rva_01045_kolumbus_kbvip', 'rvg_01045_kolumbus_kbvip'),
('rva_01045_kolumbus_r_kbvip', 'rvg_01045_kolumbus_r_kbvip'),
('rva_01045_kolumbus_s_admin', 'rvg_01045_kolumbus_s_admin'),
('rva_01045_kolumbus_s_batch', 'rvg_01045_kolumbus_s_batch'),
('rva_01045_kolumbus_s_kbvip', 'rvg_01045_kolumbus_s_kbvip'),
('rva_01045_kolumbus_t_admin', 'rvg_01045_kolumbus_t_admin'),
('rva_01045_kolumbus_t_batch', 'rvg_01045_kolumbus_t_batch'),
('rva_01045_kolumbus_t_kbvip', 'rvg_01045_kolumbus_t_kbvip'),
('rva_00771_kfz', 'rvg_01219_#opct55'),
('rva_01219_betaejm_linux', 'rvg_01219_betaejm_linux'),
('rva_00771_schaden', 'rvg_01299_a_cc_kb'),
('rva_00771_schaden', 'rvg_01299_edmz107_3'),
('rva_00771_schaden', 'rvg_01375_adrm004_1'),
('rva_01427_sdx_hpbs', 'rvg_01427_sdx_hpbs'),
('rva_01569_elk_t_stagemonitor_reader', 'rvg_01569_elk_t_stagemonitor_reader'),
('rva_01799_kurse_bloomb', 'rvg_01799_kurse_bloomb'),
('rva_01799_sp_t_be01000090', 'rvg_01799_sp_t_be01000090'),
('rva_01858_#qpdb60u', 'rvg_01858_#qpdb60u'),
('rva_01858_#txt605', 'rvg_01858_#txt605'),
('rva_01858_se_sg6000e', 'rvg_01858_#txt605'),
('rva_01858_07PCUnfall', 'rvg_01858_07pcunfall'),
('rva_01858_45pclebenbpm', 'rvg_01858_45pclebenbpm'),
('rvz_01858_60dvkvtstserv', 'rvg_01858_60dvkvtstserv'),
('rvz_01858_60dvkv_pkvcon', 'rvg_01858_60dvkv_pkvcon'),
('rva_01858_kranken', 'rvg_01858_60ewkv'),
('rva_01858_60ewkv_consql', 'rvg_01858_60ewkv_consql'),
('rva_01858_60ewkv_sqltst', 'rvg_01858_60ewkv_sqltst'),
('rva_01858_60ewkv_unix', 'rvg_01858_60ewkv_unix'),
('rva_01858_kranken', 'rvg_01858_60ewkv_unix'),
('rva_01858_60pckv', 'rvg_01858_60pckv'),
('rva_01858_60pckv', 'rvg_01858_60pckv_unix'),
('rvz_01858_buz_admin', 'rvg_01858_buz_admin'),
('rva_01858_buz_dbadmin', 'rvg_01858_buz_dbadmin'),
('rva_01858_buz_user01', 'rvg_01858_buz_user01'),
('rva_01858_buz_user02', 'rvg_01858_buz_user02'),
('rva_01858_elster', 'rvg_01858_elster'),
('rva_01858_fw_personen_dezentral', 'rvg_01858_fw_personen_dezentral'),
('rva_01858_linux96', 'rvg_01858_linux96'),
('rva_01858_linux97', 'rvg_01858_linux97'),
('rva_01858_60pckv', 'rvg_01858_linux_vespucci'),
('rva_01858_linux_vespucci', 'rvg_01858_linux_vespucci'),
('rva_01858_mqsm060_1', 'rvg_01858_mqsm060_1'),
('rva_01858_p_zabas', 'rvg_01858_p_zabas'),
('rva_01858_se_sg6000c', 'rvg_01858_se_sg6000c'),
('rva_01858_se_sg6000e', 'rvg_01858_se_sg6000e'),
('rva_01858_t_tzabas', 'rvg_01858_t_tzabas'),
('rvz_01858_zmv_admin', 'rvg_01858_zmv_admin'),
('rva_01858_zmv_user02', 'rvg_01858_zmv_user02');

ALTER TABLE `Umb_AFGFListe`
  ADD PRIMARY KEY (`GF`,`AF`),
  ADD KEY `afind` (`AF`);

-- Zähle die Menge der neuen AFen darin
-- SELECT COUNT(AF) FROM `Umb_AFGFListe` GROUP BY AF;

-- Ersetze die _ZZZZZ_ im AF-Namen durch 00000
-- SELECT REGEXP_REPLACE(AF, '_[0-9]{5}_', '_00000_') FROM `Umb_AFGFListe` GROUP BY AF;

-- Finde für jede AF in dieser Liste alle möglicherweise dazu passenden AFen in tblGesamt
-- für alle gelöschten AFen (die nicht gelöschten sind ja frisch importiert und deshalb in tblGesamt bereits korrekt).
-- Filtere alle heraus, die identisch sind (das sind dann völlig neue Rechte)

DROP TABLE IF EXISTS altnachneu;
CREATE TABLE IF NOT EXISTS altnachneu (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT ,
    `alt` TINYTEXT NOT NULL COMMENT 'Der alte AF-Name' ,
    `neu` TINYTEXT NOT NULL COMMENT 'Der neue AF-Name' ,
    `istgleich` INT NOT NULL COMMENT 'Flag, ob alter Name = neuer Name' ,
    `status` TINYTEXT NULL DEFAULT NULL COMMENT 'null = noch nicht behandelt; "ok" oder Fehlermeldung' ,
     PRIMARY KEY (`id`)
) ENGINE = InnoDB
COMMENT = 'Die Tabelle dient dem automatisierten Umbenennen von AFen';

DROP TABLE IF EXISTS altnachneuHistorie;
CREATE TABLE IF NOT EXISTS altnachneuHistorie (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT ,
    `alt` TINYTEXT NOT NULL COMMENT 'Der alte AF-Name' ,
    `neu` TINYTEXT NOT NULL COMMENT 'Der neue AF-Name' ,
    `status` TINYTEXT NULL DEFAULT NULL COMMENT 'null = noch nicht behandelt; "ok" oder Fehlermeldung' ,
     PRIMARY KEY (`id`)
) ENGINE = InnoDB
COMMENT = 'Die Tabelle dient dem Archivieren umbenannter AFen';

-- Murks wegen Timeout zur DB
DROP TABLE IF EXISTS B1;
CREATE TEMPORARY TABLE B1
SELECT REGEXP_REPLACE(AF, '_[0-9]{5}_', '_00000_') FROM Umb_AFGFListe as neu;
SELECT COUNT(*) FROM B1;

DROP TABLE IF EXISTS B2;
CREATE TEMPORARY TABLE B2
SELECT enthalten_in_af, REGEXP_REPLACE(enthalten_in_af, '_[0-9]{5}_', '_00000_') as alt
FROM tblGesamt
WHERE tblGesamt.geloescht and tblGesamt.enthalten_in_af != "ka"
GROUP BY enthalten_in_af;

SELECT COUNT(*) FROM B2;

INSERT INTO altnachneu
    SELECT
            0 as `id`,
        B2.alt,
        B1.neu,
        B1.neu = B2.alt as 'istgleich',
        null as `status`
    FROM B1
    INNER JOIN B2
        ON B1.neu = B2.enthalten_in_af
    WHERE B1.neu != B2.enthalten_in_af
    GROUP BY B1.neu, B2.alt
    ORDER BY B1.neu, B2.alt
;
SELECT * FROM altnachneu;

-- Wenn es in einem Schwung geht, ist das hier besser:

INSERT INTO altnachneu
    SELECT
            0 as `id`,
        tblGesamt.enthalten_in_af as `alt`,
        Umb_AFGFListe.AF as `neu`,
        tblGesamt.enthalten_in_af = Umb_AFGFListe.AF as 'istgleich',
        null as `status`
    FROM Umb_AFGFListe
    INNER JOIN tblGesamt
        ON REGEXP_REPLACE(Umb_AFGFListe.AF, '_[0-9]{5}_', '_00000_') = REGEXP_REPLACE(tblGesamt.enthalten_in_af, '_[0-9]{5}_', '_00000_')
    WHERE tblGesamt.geloescht AND tblGesamt.enthalten_in_af != Umb_AFGFListe.AF
    GROUP BY Umb_AFGFListe.AF, tblGesamt.enthalten_in_af
    ORDER BY Umb_AFGFListe.AF, tblGesamt.enthalten_in_af
;
SELECT * FROM altnachneu;

-- Filtere Spezailfälle heraus, bei denen die alte AF bereits mehrere Nummern hat (Historien-Kram!)
SELECT * FROM `altnachneu` as a
inner join `altnachneu` as b
            ON a.neu = b.neu
    AND b.alt != b.neu
    AND a.alt != b.neu
    AND REGEXP_REPLACE(a.alt, '_[0-9]{5}_', '_00000_') = REGEXP_REPLACE(b.neu, '_[0-9]{5}_', '_00000_')
    AND a.id < b.id
    ORDER BY a.alt
    LIMIT 1000;

-- Nun haben wir die Umbenenungstabelle alter Name -> neuer Name und bauen eine Status-Tabelle
-- Das ist nur erforderlich, weil das Schreiben auf eine Tabelle, die man per Cursor geöffnet hat, schief geht.

DROP TABLE IF EXISTS altnachneu_status;
CREATE TABLE IF NOT EXISTS altnachneu_status (
    `id` BIGINT UNSIGNED NOT NULL ,
    `status` TINYTEXT NULL DEFAULT NULL COMMENT 'null = noch nicht behandelt; "ok" oder Fehlermeldung' ,
     PRIMARY KEY (`id`)
) ENGINE = InnoDB
COMMENT = 'Die Tabelle dient als Cache für den "umbenennen-Status"';

-- Vor dem Umbenennen müssen alle Elemente aus AFListe entfernt werden, die mit den letzten AF-Abgleichen
-- hinzugefügt wurden. Alternativ kann mman genau die AFNeu-Namen in der AFListe löschen (es gibt sonst dupkey-Fehler)

SELECT * FROM `tbl_RolleHatAF`
INNER JOIN tbl_AFListe
            ON tbl_RolleHatAF.af = tbl_AFListe.id
    INNER JOIN altnachneu
            ON tbl_AFListe.af_name = altnachneu.neu
LIMIT 1000;

-- Alle gefundenen RolleHatAF-Elemente auf die 1 setzen und die IDs sowie die ehemaligen Ziele merken!
-- ----------------------------------------------- erledigt? ------------------------------------

-- Nachdem alle Rollen-Referenzen gelöscht sind, kommt das hier:
DELETE FROM tbl_AFListe
WHERE tbl_AFListe.af_name in (SELECT DISTINCT neu FROM altnachneu)


SET @altliste = "";
SET @neuliste = "";
SET @Statusgedoens = "Status: ";
BEGIN;
    CALL af_umbenennen(@altliste, @neuliste, @Statusgedoens);
    SELECT @altliste, @neuliste, @Statusgedoens;
    SELECT * FROM altnachneu_status LIMIT 1000;

    SELECT 'Gelungen' as status, count(*) as Anzahl FROM altnachneu WHERE status like 'Ok%'
    UNION
    SELECT 'Misslungen' as status, count(*) as Anzahl FROM altnachneu WHERE status not like 'Ok%';
ROLLBACK;

INSERT INTO altnachneuHistorie
    SELECT 0 as `id`, `alt`, `neu`, `status` FROM altnachneu;
