# Generated by Django 4.2.1 on 2023-07-06 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planilhas', '0008_alter_carteira_cod_cred'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carteira',
            name='cod_cred',
            field=models.CharField(max_length=2),
        ),
    ]
