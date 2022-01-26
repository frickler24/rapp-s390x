from django.test import TestCase

from ..view_Matrix import string_aus_liste

class test_string_aus_liste(TestCase):
    def test_string_aus_leerer_liste(self):
        self.erg = string_aus_liste(())
        self.assertEqual(self.erg, '')

    def test_string_aus_kurzer_liste(self):
        self.erg = string_aus_liste(("a", "b"))
        self.assertEqual(self.erg, 'a, b')

    def test_string_aus_langer_liste(self):
        self.erg = string_aus_liste(("abc",
                                     "def",
                                     "das hier wird ein längerer String mit Komma, lala",
                                     " "))
        self.assertEqual(self.erg, 'abc, def, das hier wird ein längerer String mit Komma, lala,  ')

