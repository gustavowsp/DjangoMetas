# Generated by Django 4.2.1 on 2023-07-18 18:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secao_ajuda', '0009_artigo_data_publicacao_alter_artigo_primeira_imagem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artigo',
            name='em_destaque',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='artigo',
            name='data_publicacao',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 18, 18, 29, 22, 274668, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='ArtigosEmDestaque',
        ),
    ]
