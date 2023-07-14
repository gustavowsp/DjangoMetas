# Generated by Django 4.2.1 on 2023-07-14 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artigo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo_artigo', models.CharField(max_length=255, verbose_name='Titulo do artigo')),
                ('capa_artigo', models.ImageField(upload_to='secao_ajuda/static/capas_artigo/%Y/%m/%d/<django.db.models.fields.CharField>', verbose_name='Capa do artigo')),
                ('primeiro_texto', models.TextField()),
                ('primeira_imagem', models.ImageField(upload_to='secao_ajuda/static/imagem_artigo/%Y/%m/%d/<django.db.models.fields.CharField>_imagemUM', verbose_name='Capa do artigo')),
                ('segundo_texto', models.TextField()),
                ('segunda_imagem', models.ImageField(upload_to='secao_ajuda/static/imagem_artigo/%Y/%m/%d/<django.db.models.fields.CharField>_imagemDOIS', verbose_name='Capa do artigo')),
            ],
        ),
    ]