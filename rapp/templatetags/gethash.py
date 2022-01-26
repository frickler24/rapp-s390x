from django import template
from urllib.parse import quote, unquote

register = template.Library()

#
@register.filter
def hash(h, key):
	"""
	Liefert einen Wert des unveränderten Keys eines Hashes.
	Falls der Key nicht existiert, wird der Hash zurückgeliefert (das erzeugt mehr Ausgaben als None zurückzuliefern)

	:param h: Der Hash
	:param key: Der gesuchte Key
	:return: hash[key] or hash
	"""
	if key in h:
		return h[key]
	return h

@register.filter
def strhash(h, key):
	"""
	Liefert einen Wert des normierten Keys eines Hashes.
	Normierung ist: Umwandeln in lower-case-String mit anschließendem Stipping
	Falls der Key nicht existiert, wird "ungenutzt" zurückgeliefert.
	:param h: Der Hash
	:param key: Der gesuchte Key
	:return: hash[str(key).lower().strip()] or "ungenutzt"
	"""
	key = str(key).lower().strip()
	if key in h:
		return h[key]
	return 'Ungenutzt'

# Liefert einen Wert eines 2-teiligen Hashes für die Templates
@register.filter
def hash2(_1, _2):
	return _1, _2

@register.filter
def hash3(_1_2, _3):
	_1, _2 = _1_2
	key = '!'.join((_2, _3))
	return hash(_1, key)

@register.filter
def part1(_1, delim='!'):
	"""
	Liefere den ersten Teil gestrippt eines durch ! getrennten Strings

	:param delim:
	:param _1: Ein Sting, bestehend aus <s1> ?! ?<s2>  bspw. "XV12345 ! FoobarUser"
	:return: <s1>
	"""
	s = _1.split(delim)
	if len(s) > 1:
		return s[0].strip()
	else:
		return s

@register.filter
def part1a(_1):
	"""
	Liefere vom ersten Teil eines durch ! getrennten Strings das erste Zeichen als String, sonst ""

	:param _1: Ein Sting, bestehend aus <s1> ?! ?<s2>  bspw. "XV12345 ! FoobarUser"
	:return: <s1>[0] or ""
	"""
	s = part1(_1)
	if len(s) > 0:
		return quote(part1(_1)[0], safe='')
	else:
		return ""

@register.filter
def part2(_1):
	"""
	Liefere den zweiten Teil eines durch ! getrennten Strings

	:param _1: Ein Sting, bestehend aus <s1> ?! ?<s2>   bspw. "XV12345 ! FoobarUser"
	:return: <s2>
	"""
	s = _1.split("!")
	if len(s) > 1:
		return s[1]
	else:
		return "Kein zweites Element gefunden"

@register.filter
def part2a(_1):
	"""
	Liefere den zweiten Teil eines durch " | " getrennten Elements, das zunächst in einen Strings gewandelt wird

	:param _1: Ein Objekt, bestehend aus <s1> ?! ?<s2>   bspw. "XV12345 ! FoobarUser"
	:return: <s2>
	"""
	s = str(_1).split(" | ")
	if len(s) > 1:
		return s[1]
	else:
		return "Kein zweites Element gefunden"

@register.filter
def finde(inputset, search):
	"""
	Liefert den Zweck einer Rolle (ist der zweite Teil des Tupels)

	:param inputset:
	:param search:
	:return:
	"""
	for s in inputset:
		(name, zweck) = s
		if name == search:
			return zweck
	return ('')

@register.filter
def sort(menge):
	liste = list(menge)
	liste.sort()
	return liste

@register.filter
def vergleich(einzel, menge):
	einzel = einzel.strip()
	for element in menge:
		if element.lower() == einzel:
			return True
	return False