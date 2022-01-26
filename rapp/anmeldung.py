from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class Anmeldung():
    """
    Die Hilfsklasse zum Login: User John Doe einrichten und anmelden.
    Falls der User bereits existiert, einfach nur anmelden.
    Diese Klasse wird ausschließlich von den Testscripten verwendet
    """
    def login(self, loginfunc):
        user = authenticate(username='john', password='123')
        if user is None:
            user = User.objects.create_user(username='john', email='john@doe.com', password='123')

        loginfunc(username=user, password='123')

    def __init__(self, loginfunc):
        self.login(loginfunc)
