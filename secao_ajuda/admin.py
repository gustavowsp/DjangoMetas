from django.contrib import admin
from secao_ajuda import models
# Register your models here.


@admin.register(models.Artigo)
class ArtigoAdmin(admin.ModelAdmin):
    list_display = ['id','titulo_artigo']
    list_display_links = ['id']
    search_fields = ['descricao_artigo','titulo_artigo']

# # @admin.register(models.ArtigosEmDestaque)
# # class ArtigosEmDestaqueAdmin(admin.ModelAdmin):
#     list_display = ['id','artigo','em_destaque']
#     list_display_links = ['id','artigo']