# Generated by Django 3.0.4 on 2020-03-21 19:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_de_tipo_de_item', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipodeitem',
            name='prefijo',
            field=models.CharField(default='pre', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='atributonumerico',
            name='max_decimales',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0, 'La máxima cantidad de digitos decimales debe ser un numero mayor o igual a 0'), django.core.validators.MaxValueValidator(20, 'El máximo numero de digitos decimales permitidos es 20')]),
        ),
        migrations.AlterField(
            model_name='atributonumerico',
            name='max_digitos',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0, 'La máxima cantidad de digitos debe ser un numero mayor o igual a 0'), django.core.validators.MaxValueValidator(20, 'El máximo numero de digitos permitidos es 20')]),
        ),
    ]