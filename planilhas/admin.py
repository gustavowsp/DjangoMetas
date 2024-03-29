from django.contrib import admin
from . models import Carteira, PasswordDataBase

# Register your models here.

@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    list_display = ['nome_carteira','cod_cred']
    list_display_links = ['cod_cred']
    search_fields = ['nome_carteira','cod_cred']

@admin.register(PasswordDataBase)
class PasswordDataBaseAdmin(admin.ModelAdmin):
     ...