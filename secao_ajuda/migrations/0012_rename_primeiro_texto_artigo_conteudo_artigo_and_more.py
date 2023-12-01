# Generated by Django 4.2.1 on 2023-09-01 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('secao_ajuda', '0011_alter_artigo_data_publicacao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='artigo',
            old_name='primeiro_texto',
            new_name='conteudo_artigo',
        ),
        migrations.RemoveField(
            model_name='artigo',
            name='em_destaque',
        ),
        migrations.RemoveField(
            model_name='artigo',
            name='primeira_imagem',
        ),
        migrations.RemoveField(
            model_name='artigo',
            name='segunda_imagem',
        ),
        migrations.RemoveField(
            model_name='artigo',
            name='segundo_texto',
        ),
    ]
