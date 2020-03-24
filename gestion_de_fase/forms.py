from django import forms
from gestion_de_fase.models import Fase
from django.contrib.auth.models import User


class NuevaFaseForm(forms.ModelForm):

    class Meta:
        model = Fase
        fields = ['nombre',]