# Generated by Django 3.0.4 on 2020-03-17 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roles_de_proyecto', '0003_auto_20200316_2343'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='roldeproyecto',
            options={},
        ),
        migrations.AlterField(
            model_name='roldeproyecto',
            name='nombre',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
