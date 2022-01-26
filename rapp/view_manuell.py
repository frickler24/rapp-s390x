# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.urls import reverse_lazy

from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from .models import Manuelle_Berechtigung


class ManuelleBerechtigungCreate(CreateView):
    """Neue manuell behandelte Berechtigung erstellen"""
    model = Manuelle_Berechtigung
    fields = '__all__'
    initial = {'letzte_aenderung': timezone.now(), }
    success_url = reverse_lazy('manuell_liste')


class Manuelle_BerechtigungUpdate(UpdateView):
    """Manuell behandelte Berechtigung ändern"""
    model = Manuelle_Berechtigung
    fields = '__all__'
    initial = {'letzte_aenderung': timezone.now(), }
    success_url = reverse_lazy('manuell_liste')


class Manuelle_BerechtigungDelete(DeleteView):
    """Manuell behandelte Berechtigung löschen"""
    model = Manuelle_Berechtigung
    fields = '__all__'
    initial = {'letzte_aenderung': timezone.now(), }
    success_url = reverse_lazy('manuell_liste')


class Manuelle_BerechtigungListe(ListView):
    """Manuell behandelte Berechtigung löschen"""
    model = Manuelle_Berechtigung
    fields = '__all__'
