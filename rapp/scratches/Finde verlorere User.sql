-- hier ein scheinbar sinnfreier Kommentar gegen die Abfrage zum Löschen

drop table if exists Bastel1;
create table Bastel1
    SELECT tblUserIDundName.userid, tblUserIDundName.name FROM `tblGesamt`
    inner join tblUserIDundName
        on tblGesamt.userid_und_name_id = tblUserIDundName.id
    where tblGesamt.geloescht = false and tblUserIDundName.geloescht = false
        and tblUserIDundName.zi_organisation = 'ai-ha'
    group by tblUserIDundName.userid;

drop table if exists Bastel2;
create table Bastel2
    SELECT `AF zugewiesen an Account-Name`, `Identität`, `Nachname`, `Vorname`
    FROM `tblRechteNeuVonImport`
    GROUP BY `AF zugewiesen an Account-Name`;

SELECT Bastel2.*, Bastel1.*
FROM Bastel2
    left join Bastel1 on Bastel2.`AF zugewiesen an Account-Name` = Bastel1.userid
WHERE Bastel1.userid is null
;
