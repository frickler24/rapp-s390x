
SELECT tblRechteNeuVonImport.`id`, tblRechteNeuVonImport.`Identität`, tblRechteNeuVonImport.`Nachname`,
	tblRechteNeuVonImport.`Vorname`, tblRechteNeuVonImport.`TF Name`, tblRechteNeuVonImport.`AF Anzeigename`,
    tblRechteNeuVonImport.`GF Name`,
    dup.`id`, dup.`Identität`, dup.`Nachname`,
	dup.`Vorname`, dup.`TF Name`, dup.`AF Anzeigename`,
    dup.`GF Name`
FROM tblRechteNeuVonImport
INNER JOIN (
    SELECT `id`, `Identität`, `Nachname`, `Vorname`,
             `TF Name`,
             `AF Anzeigename`,
             `TF Applikation`,
             `GF Name`
    FROM tblRechteNeuVonImport
    GROUP BY `Identität`,
             `TF Name`,
             `AF Anzeigename`,
             `TF Applikation`,
             `GF Name`
    HAVING COUNT(`Identität`) > 1
) dup
	on tblRechteNeuVonImport.`Identität` = dup.`Identität`
    AND tblRechteNeuVonImport.`TF Name` = dup.`TF Name`
    AND tblRechteNeuVonImport.`AF Anzeigename` = dup.`AF Anzeigename`
    AND tblRechteNeuVonImport.`TF Applikation` = dup.`TF Applikation`
    AND tblRechteNeuVonImport.`GF Name` = dup.`GF Name`
;
