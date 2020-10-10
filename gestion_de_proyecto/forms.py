from django import forms
from usuario.models import Usuario
from .models import Proyecto, Participante, Comite


class ProyectoForm(forms.ModelForm):
    """
    Form que permite la creacion de un nuevo proyecto.
    Es necesario espesificar el gerente del proyecto.

    Campos:
        -nombre: str, nombre del proyecto
        -descripcion: str, descripcion del proyecto
        -gerente: User, usuario que se le asignar el rol de gerente del proyecto
    """

    descripcion = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))

    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'gerente')

    def __init__(self, *args, **kwargs):
        """
        Constructor de la clase ProyectoForm.
        Para el posible gerente, el usuario seleciona entre los usuarios logeados un gerente
        """
        super(ProyectoForm, self).__init__(*args, **kwargs)
        self.fields['gerente'].empty_label = 'Seleccionar Gerente'
        self.fields['gerente'].queryset = Usuario.objects.filter(groups__isnull=False)


class EditarProyectoForm(forms.ModelForm):
    """
    Form que permite editar un proyecto.

    Campos:
        -nombre: str, nombre del proyecto
        -descripcion: str, descripcion del proyecto
    """
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion')


class NuevoParticipanteForm(forms.ModelForm):
    """
    Formulario utilizado para Asignar un nuevo Participante un Proyecto.
    El formulario solicita la selección de un Usuario activo del Sistema que no esté aún dentro
    del Proyecto.

    Clase Padre:
        forms.ModelForm.
    """
    def __init__(self, *args, proyecto=None, **kwargs):
        """
        Constructor del Formulario.

        Este filtra, en el campo de usuario, solo los usuarios que aun no estan en el proyecto y están
        activos dentro del Sistema.

        Argumentos:
            proyecto:Proyecto, proyecto al cual se agregará el participante
        """
        super(NuevoParticipanteForm, self).__init__(*args, **kwargs)
        usuarios = []
        if proyecto is not None:
            # Se obtienen todos los ids de usuarios que no estan entro del proyecto
            for user in Usuario.objects.filter(groups__isnull=False):
                if not proyecto.participante_set.all().filter(usuario=user).exists():
                    usuarios.append(user.id)

                if proyecto.participante_set.all().filter(usuario=user, rol__isnull=True) \
                        .exclude(usuario=proyecto.gerente).exists():
                    if user not in usuarios:
                        usuarios.append(user.id)
            self.fields['usuario'].queryset = Usuario.objects.all().filter(pk__in=usuarios)
            self.fields['usuario'].empty_label = 'Seleccionar un usuario'
            self.fields['rol'].empty_label = 'Seleccionar un rol'

    class Meta:
        model = Participante
        fields = ['usuario', 'rol']


class SeleccionarPermisosForm(forms.Form):
    """
    Formulario utilizado para seleccionar los permisos de proyecto que se asignarán a un usuario por cada
    fase del Proyecto.

    El formulario solicita al usuario seleccionar, por cada fase, los permisos que se darán al nuevo participante.

    Clase Padre:
        forms.Form
    """
    def __init__(self, usuario, proyecto, rol, *args, **kwargs):
        """
        Constructor del formulario.

        Se agrega, por cada fase, un campo de selección multiple con los permisos de proyecto a seleccionar
        para asignarlos al usuario.

        Argumentos:
            usuario: User, nuevo participante del Proyecto.\n
            proyecto: Proyecto, proyecto al cual se agregará al usuario.\n
            rol: RolDeProyecto, rol el cual se asignará al nuevo Participante.\n
        """
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
    #

    class Meta:
        model = Comite
        fields = ['miembros']

    def __init__(self, proyecto, *args, **kwargs):
        super(SeleccionarMiembrosDelComiteForm, self).__init__(*args, **kwargs)
        self.fields['miembros'].queryset = proyecto.participante_set.all()
        self.fields['miembros'].widget = forms.CheckboxSelectMultiple()

    def clean_miembros(self):
        miembros = self.cleaned_data["miembros"]
        if miembros.count() % 2 == 0 or miembros.count() < 3:
            raise forms.ValidationError("El número de miembros del comite debe ser mayor a 3 e impar.")
        return miembros