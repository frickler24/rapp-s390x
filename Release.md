# RApp Release-Information

## 1.14.6 Erweiterte Import- und Exportfunktionalitäten
Die Version macht einen großen Sprung, weil in diesem Release etliche neue Features 
mit ein paar Datenbankerweiterungen implementiert sind:
- **Exportfunktionen** für die Sichten in "User und Rollen"  
Wie immer werden die Daten im TSV Format exportiert 
und müssen in Excel als Text geladen werden (UTF-8)
  - Bei der Betrachtung von Rollenvarianten (**'-'** als Rollenname)
  - Bei der gesamtheitlichen Betrachtung von Rollenvarianten (**'*'** als Rollenname)
  - Für die Selektion ungenutzte Arbeitsplatzfunktionen 
  in den angegebenen Rollen (**'+'** als Rollenname)
- Das IIQ-Attribut "**Organisation**" wird nun importiert  
Bei natürlichen Usern steckt dahinter die **Gruppe**, 
der die User angehören.
Bei Technischen Usern kann es ebenfalls die Gruppe sein, 
häufig sind es aber auch technische Organisationen.
Diese beginnen immer mit der 5-stelligen Organummer und sind daran leicht zu erkennen.  
Die Idee dahinter ist folgende:
  - User, die eine abweichende aktuelle Gruppe und IIQ-Organisation haben 
**und** bei denen die IIQ-Organisation **keine** technische Gruppierung ist, 
können eine Aktualisierung ihrer Gruppenzugehörigkeit erfahren.
Dazu gibt es auf der Import-Einstiegsseite eine **neue Checkbox** 
(standardmäßg deaktiviert).  
  - Wird sie aktiviert, 
werden die Organisationsveränderungen zwischen zweitem und dritten Import-Schritt aktualisiert. 
Damit können sie über die bekannten User-Links kontrolliert und gegebenenfalls weiter verändert werden.
  - Wird die Checkbox nicht aktiviert, erfolgen keine Anpassungen an den Inhalten der Gruppe.
Damit regelmäßige Abgleiche erfolgen können,
wird jede IIQ-Organisation in einem neuen Attribut bei der UserID abgelegt (**iiq_organisation**).  
Abgleich-Abfragen stehen noch zur Entwicklung an.
  - Alle technischen Organisationen werden ebenfalls in das neue Feld iiq_organisation eingetragen,
allerdings führen Abweichungen zwischen der Gruppe und der iiq_organisation **nicht** zu einer Anzeige des Users als "neu oder geändert".  
Das hat den Zweck, 
dass diese Unterschiede nicht ständig zu notwendigen Prüfungen bei Datenimporten führen.  
Näheres dazu im [Pull Request](https://github.com/frickler24/RechteDB/pull/233).  
- Um den öfter mal problembehafteten "Umzug" 
von Identitäten zwischen Organisationseinheiten besser abzubilden,
wird nun auch die Abteilung generiert - sie wird nun aus der beim Import angegebenen Orga abgeleitet.
- Die **Matrix** ist **erweitert** um **Userid-Liste**, **NPU-Rolle** und **NPU-Grund**  
Sowohl im Dialog als auch in beiden TSV-Exporten (Kurz- und Langform)
werden drei neue Spalten erzeugt:
  - die **kommaseparierte Liste der UserIDs je Identität** wird zwischen Team und erster Rolle in fallender alphabetischer Reihenfolge angezeigt (damit zuerst immer die XV-Nummer gezeigt wird)
  - die **NPU-Rolle** wird als vorletzte Spalte gezeigt
  - der **NPU-Grund** als derzeit letzte Spalte.  
Der NPU-Grund kann auffällig lang sein und wir sollten noch festlegen, ob das wirklich Sinn hat. 
Aber um es entscheiden zu können, sollte man es erst einmal gesehen haben.
- So ganz nebenbei hatte sich unser **Fortschrittsbalken** beim Import verabschiedet - 
bei Firefox ging wenigstens noch der Import, bei Chrome und chromium ging gar nichts mehr.
Ist jetzt repariert und schöner als vorher - er sieht jetzt auch bei Chrome gut aus.

## 1.9.1 Kann nun auch reverse Tests
- Bislang konnten reverse-Tests nicht ausgeführt werden, weil mehrere Probleme im Zusammenhang mit den Stored Procedures existierten. Diese Probleme sind nun behoben, sodass sowohl `manage.py test` als auch `manage.py test -r` funktionieren.
## 1.9.0 Auswahl verschiedener Konzept-Inhalte
- Das Konzept kann nun in verschiedenen Formen erzeugt werden:
  - Kurzform: Dabei wird nur das reine Rollenkonzept erzeugt (Rolle -> AF)
  - Mittellang: Kurzform, ergänzt um AF -> TF
  - Langform: Mit allen in der Datenbak enthaltenen Details
## 1.8.8 Nutzung von docker-compose für die x86-Konfiguration
- Das muss noch auf die s390x-Konfig angepasst werden (wenn dort docker-compose existiert)
## 1.8.4 Umstellung auf `django 3.0.4`
- Da `django 3` bereits seit längerem released ist, habe ich nun die Umstellung darauf vollzogen.

- Ein wesentlicher Unterschied scheint im Generieren von Strings zu liegen:
  - Sonderzeichen werden nun nicht mehr in dezimaler Form `&#ddd` angegeben,
sondern hexadezimal `&#xhh`.
Das führte bislang nur zu zwei Fehlern im Test, die bereinigt wurden.  
Aber dennoch bitte etwas aufpassen in der nächsten Zeit, ob es Merkwürdigkeiten gibt.
## 1.8.2 Neue Listen: Ungenutzte AF/GF und ungenutzte Rollen
- Die Liste der ungenutzten Rollen kann verwendet werden, 
  - um bei Neuerstellung von Rollen einen Quercheck zu bekommen
  - und um zu prüfen, ob es obsolete Rollendefinitionen gibt
(bspw. durch doppelte Modellierung mit leicht verschiedenen Namen)

![grafik](https://user-images.githubusercontent.com/6292952/76168612-b68b4280-6171-11ea-9992-5ea88266fdbc.png)

- Die Liste der ungenutzten AF/GF-Kombinationen bezieht sich 
auf die "Genehmigungstabelle" tblUebersicht_AFGFs.  
Alle dort gefundenen Einträge, 
die weder in der aktuellen Gesamttabelle, 
noch in der Historientabelle aufgeführt sind, 
werden dort gelistet.
## 1.7.4 Neue Liste: Ungenutzte Teams
- Diese Liste wird wir gewohnt über den Menüpunkt `Listen` aufgerufen. 
Sie zeigt an, welchen Teams bislang oder nicht mehr User zugeordnet sind.  
Hier kann noch ein Link eingefügt werden, über den das Teamlöschen direkt angesprochen werden kann.
## 1.7.2 Umbenennen von Arbeitsplatzfunktionen
- Für das massenhafte Umbenennen von AFen (bspw. weil siuch die Orga-Nummer geändert hat)
wurden einige Stored Procedures implementiert.
Sie sollten aber weiterhin per Hand ausgeführt werden, weil die ganze Angelegenheit äußerst sensibel ist.
## 1.7.0 Löschmarkierung für nicht mehr direkt genutzte Plattformen
- Das Problem beim Import der AI-Rechte war, dass zuvor eine Aufräumaktion der veralteten Berechtigungen aus SE und AI-XA erfolgte.
Bei dieser Aufräumaktion wurde eine Plattform invalide, allerdings wurde sie weiterhin aus der Historientabelle referenziert.
Das beim Import gewünschte Löschen der Plattform konnte aufgrund der RI nicht erfolgen und die SP brach kommentarlos ab.  
Mit diesem PR wird das Löschen der Plattforn ersetzt durch eine Löschmarkierung.
## 1.6.0 Verbesserte Infos in Hauptansicht
- Da nun doch wieder mehrere Organisation in der RApp verwaltet werden,
erfolgen auch verschiedene Imports zu unterschiedlichen Zeiten.
Damit war die Anzeige des letzten Imports nicht mehr wirklich aussagefähig,
weil zwar der korrekte letzte Zeitpunkt erkennbar war,
aber nicht die Organisation,
für die der Import erfolgte.  
Das ist nun mit dieser Version behoben. 
Sowohl Orga als auch Importeuer sind nun verzeichnet. 
Dargestellt werden nun auch nur noch erfolgreiche Importe:  

![grafik](https://user-images.githubusercontent.com/6292952/72684224-0a1cd080-3adf-11ea-9d98-4fdbf7a99337.png)

Zur Installation: Minor-Release wurde angegeben wegen der Erweiterung des Datenbankmodells. Ein makemigrations und migrate sind im Manager erforderlich, sonst gibt es Laufzeitfehler.

## 1.5.7 Testverbesserungen und Mini-Fixes
## Mit 1.5.5 Anpassung Network- und Zugriffskonfiguration auf die Datenbank
- Seit einiger Zeit ist auffällig geworden, dass einfache Abfragen in der RApp manchmal schnell beantwortet werden, manchmal langsam. Zunächst wurde das auf vermehrte Nutzung der Anwendung durch mehrere, parallel arbeitende User zurückgeführt. Genauere Beobachtungen der Container und deren Last haben aber gezeigt, dass unregelmäßig aber häufig Anfragen eine Wartezeit von genau 5 Sekunden haben, bevor sie die ersten HTTP-Antworten liefern.  
Aufgrund der reproduzierbaren 5 Sekunden lag der Verdacht auf eine Timeout-Situation nahe.
Da die andern beiden Anwendungen im selben virtuellen Netzwerk (die Statusanzeige des Loadbalancers und der PMA Datenbankzugang) diese Verzögerung nicht aufwiesen, wurde die Konfiguration des django Frameworks geändert:
  - Der DHCP-IP-Adressraum des Netzwerks wurde auf 172.42.0.0/24 begrenzt, 
  - der gesamte Adressraum umfasst weiterhin großzügige 172.42.0.0/16. 
  - Die Adresse 172.42.42.42 wurde fest dem DB-Server zugeordnet und 
  - diese IP-Adresse fest in die Konfiguration eingetragen.  

Das ist nicht schön, aber damit sind die Timeouts / Verzögerungen bislang in Lasttests nicht mehr aufgetreten

## 1.5.3 - 1.5.5 Fixes in der Anzeige vorhandener Rechte in den Rollen
- Duch zusätzliche Zeichen und Unterschiede in upper-/lower-case-Darstellungen wurden manche vergebenen Rechte als nicht vergeben angezeigt. Das ist nun in der Online-Anzeige und dem Excel-Export korrigiert.
## 1.4.7 – 1.5.2 Einige Erweiterungen und Gruppierungsmöglichkeiten
### Erweiterung der Konzepte um VAIT-Kapitel
- TF
- RACF-Auflösung
- Db2-Auflösung
- Windows Laufwerke ACL Auflösung  
Hierfür ist auch die Unterscheidung zwischen Konzept (kurz) und Konzept (episch) für die Online-Anzeige und der Hinweis auf die extremen Laufzeiten der PDF-Generierung (Hunderte Seiten) entstanden.

### Es gibt jetzt eine Zusammenfassung über Teams
-	Beispiel Team „IT Krankenversicherung“
-	Achtung: Es wird nur die Liste der darin enthaltenen Teams eingetragen im neuen Feld „Team-Liste“. 
Die Namen der User ergeben sich dann aus der Menge der darin beschriebenen einzelnen Teams.

### Es gibt nun auch sogenannte „freie Teams“
- Hintergrund ist die Modellierung des Konzepts für Axel Panten:
  - Er hat mit sich drei MA konzeptionell vollständig sich selbst zugeordnet
  - Und er hat 7 Als, bei denen er nur die Rechte sehen will, die auf seiner Ebene relevant sind.  
Alle Als haben dann selbst wieder jeweils ein eigenes Berechtigungskonzept, in denen ihre Berechtigungen insgesamt detailliert sind
- Dazu gibt es in tbl_Orga nun das Attribut „Freies Team“.
In dem wird für jeden User festgelegt, ob die Rechte komplett angezeigt werden sollen oder nur spezielle Rechte.
Alle weiteren AFen, die der User hat, werden in einer synthetischen, automatisch erzeugten Rolle „Weitere <Abteilungkürzel>“ zusammengefasst im Konzept angezeigt.
## 1.3.2 Finde ungenutzte Arbeitsplatzfunktionen in den Rollen
- Durch Umbenennungen, Aufräumaktivitäten etc. werden vereinzelte AFen nicht mehr 
in den Rollen benötigt, in die sie hineinmodelliert wurden.
Die neue Funktionalität - erreichbar über den Rollennamen "'+" in der Rollensuche - 
findet genau solche Arbeitsplatzfunktionen und zeigt sie an.  
Über die mitgegebenen Links gelangt man direkt in die Admin-Sicht zur Änderung der Rolle.
![grafik](https://user-images.githubusercontent.com/6292952/69246755-98d9a380-0ba9-11ea-99ab-acb5365856a5.png)

## 1.2.0 Ergänzung um das Handbuch
- Das Handbuch kann nun direkt über den Hilfe-Link in der Oberfläche aufgerufen werden.
Es handelt sich dabei um den Links auf den geschützten SharePoint-Raum der Kernanwendungen.

## 1.1.2 Wichtige Aktualisierungen für VAIT-Compliance 
- In dieser Verison werden zusätzliche Dinge angezeigt bzw. im Konzept-PDF ergänzt:
  - die höchste Kritikalität der TF in jeder AF
  - Die Liste der genutzten AFen mit ihren TFen
  - Die Liste der RACF-TF-Inhalte
  - Die Liste der Db2-TF-Inhalte
  - Vorbereitet ist die Anzeige der Windows-Laufwerk-ACLs

- Da die Informationen ausgesprochen umfangreich sind,
werden in der Online-Anzeige standardmäßig nur die AFen mit ihren TFen zusätzlich angezeigt.
Es gibt jedoch eine erweiterte Ansicht, in der alle Felder gezeigt werden.  
Im PDF werden immer alle zur Verfügung stehenden Daten aufgeführt 
(mehrere Hundert Sieten für einfache Konzept-Kombinationen).

Da diese Änderung etliche Datenbankveränderungen nach sich gezogen hat
(gleichzeitig wurden etlich alten Indizes bereinigt und einige Tabellen umbenannt oder gelöscht),
handelt es sich hierbei um meinen Breaking Change.

## 0.6.11 AF-Beschreibung and HK_TF_in_AF ergänzt, VIP, Zufallsgenerator entfernt
- Die Elemente AF_Beschreibung und die Höchste Kritikalität aller TF in der AF
sind in die Immplem,entierung, Oberfläche und den Export aus dem Suchpanel
eingeflossen.
- Bei der Gelegenheit wurden die Felder VIP und Zufallsganerator entfernt,
weil sie in der Modellierung unter IIQ keine Rolle mehr spielen
(es wurden separate AFen angelegt, keine Spezifikation allgemeiner AFen mehr).
- In diesem Commit wurde darüber hinaus die UserID in den Export des Suchergebnisses
aufgenommen (Issue #183)
## 0.6.9 Anpassungen Länge des Namensfelds und diverse Verbesserungen
- Die Länge des DB-Felds "Name" beim Import wurde auf 100 Zeichen Vorname und 100 Zeichen Nachname gesetzt.
Da im Normmalfall nur der zusammengesetzte Name betrachtet wird, bei dem Vor- und Nachname durch ", " getrennt sind, wurde die Gesamtlänge auf 203 Zeichen gesetzt.
Das ist eins mehr, als eigentlich benötigt wird.
- Die Fehlermeldungen der Datenbankabfragen über Stored Procs waren bei Schritt 1 überhaupt nicht sichtbar, bei den anderen Schritten waren sie nicht besonders aussagekräftig.
Das wurde entsprechend angepasst.
- Das fehlende Löschen der temporären Tabelle uids beim Import wurde ergänzt. Der Fehler war nur zu erkennen, wenn nacheinander mehrere Imports innerhalb derselben Session durchgeführt wurden, hat also keinen Einfluss auf die bisherige Funktionalität gehabt
## 0.6.8 Diverse Verbesserungen
- Neue Stored Procedure für das Thema Direct Connects
- Neue Funktion: "Neue AF/GF" ergänzt die entsprechende Tabelle um neue geffundene Einträge.
Das gilt nun auch für Werte der Organisationen außerhalb AI-BA.
- Umstellung der Code-Basis von Tab auf Space
- Reduzierung des Django-Modells um ungenutzte Indizes
- Optimierung von Suchpattern in Strings (bspw. 'AI-BA' statt %AI-BA%
## 0.6.2 Repariert die Matrix
Erkennbar sind 
- die Blätter-Buttons für die gekürzte Liste der User
- die Team-Spalte in der Matrix; 

![grafik](https://user-images.githubusercontent.com/6292952/62837600-95ad4e00-bc71-11e9-8b00-76b23124681d.png)

Hier in der Übersicht wurde sie schon vorher angezeigt, 
nun wird sie aber auch ins die Excels exportiert:

![grafik](https://user-images.githubusercontent.com/6292952/62837646-ede45000-bc71-11e9-9bfc-1819ad1d56f3.png)

Auch gut erkennbar sind hier 
- die Umstellung auf das TSV-Format 
- und die Voreinstellung für UTF-8

### Ergebnisexport in der "Suche"-Ansicht
![grafik](https://user-images.githubusercontent.com/6292952/62837705-d3f73d00-bc72-11e9-88d5-d9845bbf2586.png)

Am extrem breiten horizontalen Scrollbalken kann die Menge an Spalten erahnt werden. 

### Doku
Weiterhin wurden die [Tabellenübersicht](https://raw.githubusercontent.com/frickler24/RechteDB/master/documentation/RechteDB_Modell_20190811.png) im Dokumentationsverzeichnis aktualisiert
und eine [Tabellenbeschreibung](https://github.com/frickler24/RechteDB/blob/master/documentation/RechteDB_Modell_details_20190811.pdf) generiert. Ob letzteres was nutzt, weiß ich noch nicht.

## Vorgängerversionen
Hier ist der [Link auf die Vorgängerversionen](https://github.com/frickler24/RechteDB/wiki/%C3%84ltere-Versionshinweise)