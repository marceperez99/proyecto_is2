from django import forms

from gestion_de_solicitud.models import Voto


class GenerarReporteForm(forms.Form):
    fecha_inicial = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}))
    fecha_final = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}))
    solicitudesAprobadas = forms.BooleanField(required=False, initial=False, label='Aprobadas')
    solicitudesPendientes = forms.BooleanField(required=False, initial=False, label='Pendientes')
    solicitudesRechazadas = forms.BooleanField(required=False, initial=False, label='Rechazadas')
    pass