"""
Baue eine TSV-Datei zusammen,
die zumindest in open Office und LIbre offeice direkt importiert werden kann.
"""
import csv

from django.http import HttpResponse


class Excel():
    """
    Baue eine TSV-Datei zusammen, die zumindest in open Office und Libre office
    direkt importiert werden kann.
    """

    def __init__(self, name: str, ftyp: str = "text/csv") -> None:
        """
        Erzeuge den Header der TSV-Datei mit den einzelnen Spaltennamen
        :param name: Name der Datei
        :param ftyp: Typ ist offiziell csv, aber getrennt wird aktuell mit \t
        """
        self.response = HttpResponse(content_type=ftyp)
        self.response['Content-Disposition'] = 'attachment; filename="' + name + '"'

        # BOM (optional...Excel needs it to open UTF-8 file properly)
        self.response.write(u'\ufeff'.encode('utf8'))
        self.writer = csv.writer(self.response, csv.excel, delimiter='\t', quotechar='"')

    def writerow(self, content: object) -> None:
        """
        Schreibe genua eine Datenzeile
        :param content: Der Inhalt
        :return:
        """
        self.writer.writerow(content)

    def close(self) -> None:
        """
        Schließe die TSV-Datei
        :return:
        """
        self.writer = None
