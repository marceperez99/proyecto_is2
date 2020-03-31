# Generated by Django 3.0.4 on 2020-03-31 00:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_de_tipo_de_item', '0005_merge_20200330_2309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipodeitem',
            options={'permissions': [('pp_f_crear_tipo_de_item', 'Crear tipo de ítem'), ('pp_f_eliminar_tipo_de_item', 'Eliminar tipo de ítem'), ('pp_f_editar_tipo_de_item', 'Editar tipo de ítem'), ('pp_f_importar_tipo_de_item', 'Importar tipo de ítem')]},
        ),
        migrations.AlterField(
            model_name='atributobinario',
            name='max_tamaño',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'El tamaño maximo para el archivo debe ser mayor o igual a 1MB')], verbose_name='Tamaño Máximo (MB)'),
        ),
        migrations.AlterField(
            model_name='tipodeitem',
            name='descripcion',
            field=models.CharField(max_length=401),
        ),
        migrations.AlterField(
            model_name='tipodeitem',
            name='nombre',
            field=models.CharField(max_length=101),
        ),
    ]