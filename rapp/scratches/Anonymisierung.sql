-- Anonymisierung der User-, Technik- oder Orga-relevanten Tabellen
use RechteDB; -- die updates werden nach unten immer intensiver - gut für Chache-Einstellungskontrolle
update tblUserIDundName set `name` = SHA(`name`);
update tblGesamt set
                     `gf_beschreibung` = SHA(`gf_beschreibung`),
                     `tf_beschreibung` = SHA(`tf_beschreibung`),
                     `tf_eigentuemer_org` = SHA(`tf_eigentuemer_org`),
                     `enthalten_in_af` = SHA(`enthalten_in_af`),
                     `af_beschreibung` = SHA(`af_beschreibung`),
                     `tf` = SHA(`tf`),
                     `gf` = SHA(`gf`),
                     `tf`=`tf`  -- Nullnummer für das fehlende Komma am Ende
;
