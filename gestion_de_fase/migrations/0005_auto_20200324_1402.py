# Generated by Django 3.0.4 on 2020-03-24 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_de_fase', '0004_auto_20200322_2221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fase',
            old_name='faseCerrada',
            new_name='fase_cerrada',
        ),
        migrations.RenameField(
            model_name='fase',
            old_name='puedeCerrarse',
            new_name='puede_cerrarse',
        ),
    ]
