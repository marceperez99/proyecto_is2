# Generated by Django 3.0.4 on 2020-03-19 23:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles_de_proyecto', '0004_auto_20200317_1255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roldeproyecto',
            options={'permissions': [('ps_crear_rp', 'Crear Rol de Proyecto'), ('ps_editar_rp', 'Editar Rol de Proyecto'), ('ps_eliminar_rp', 'Eliminar Rol de Proyecto'), ('ps_ver_rp', 'Visualizar Rol de Proyecto')]},
        ),
    ]