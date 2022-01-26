-- Alle Einsatz-Felder werden uaf "Nur DV-User" gesetzt, sobald das Recht einen rvz_% Namen hat

UPDATE `tbl_RolleHatAF`
            INNER JOIN tbl_AFListe
    ON tbl_RolleHatAF.af = tbl_AFListe.id
            AND tbl_AFListe.af_name like "rvz_%"
SET `einsatz` = 1
WHERE NOT `einsatz` = 1
;

-- Bei der Gelegenheit gleich mal GV-User und FV, HV etc. ergänzen
