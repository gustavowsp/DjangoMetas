from django.contrib import admin
from pageuser.models import AcoesRealizadas,Atividade

# Register your models here.
@admin.register(AcoesRealizadas)
class AcoesRealizadasAdmin(admin.ModelAdmin):   
    
    list_display = ('id','acao','data_realizacao','usuario')
    search_fields = ('nome_acao',)
    list_filter = ('data_realizacao',)
    list_per_page = 25
    list_max_show_all = 100

    
@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('id','nome_atividade')