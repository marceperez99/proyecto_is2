from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Proyecto, Participante, Comite


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'gerente')


class EditarProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion')


class NuevoParticipanteForm(forms.ModelForm):

    def __init__(self, *args, proyecto=None, **kwargs):

        super(NuevoParticipanteForm, self).__init__(*args, **kwargs)
        usuarios = []
        if proyecto is not None:
            # Se obtienen todos los ids de usuarios que no estan entro del proyecto
            for user in User.objects.all():
                if not proyecto.participante_set.all().filter(usuario=user).exists():
                    usuarios.append(user.id)
                if proyecto.participante_set.all().filter(usuario=user, rol__isnull=True) \
                        .exclude(id=proyecto.gerente.id).exists():
                    if user not in usuarios:
                        usuarios.append(user.id)
            self.fields['usuario'].queryset = User.objects.all().filter(pk__in=usuarios)

    class Meta:
        model = Participante
        fields = ['usuario', 'rol']


class SeleccionarPermisosForm(forms.Form):

    def __init__(self, usuario, proyecto, rol, *args, **kwargs):
        super(SeleccionarPermisosForm, self).__init__(*args, **kwargs)
        for fase in proyecto.get_fases():
            self.fields[f'f_{fase.id}'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                choices=[(pp.codename, pp.name) for pp in rol.get_pp_por_fase()],
                label=f'Fase {fase.nombre}'
            )
        self.usuario = usuario
        self.permisos_de_proyecto = list(rol.get_pp_por_proyecto())
        self.rol = rol


class SeleccionarMiembrosDelComiteForm(forms.ModelForm):
    miembros = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Comite
        fields = ['miembros']

    def __init__(self, proyecto, *args, **kwargs):
        super(SeleccionarMiembrosDelComiteForm, self).__init__(*args, **kwargs)
        self.fields['miembros'].queryset = proyecto.participante_set.all()
