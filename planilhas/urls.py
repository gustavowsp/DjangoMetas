from django.urls import path
from . import views

app_name = 'planilhas'

urlpatterns = [
    path('',views.index, 
        name='HomePage'),
    
    path('layouts/',views.layouts, 
        name='Layouts'),

    path('deflatores/', views.deflator, 
        name='MetaDeflator'),

    path('incremento/', views.incremento, 
        name='MetaIncremento'),

    path('valormeta/', views.valor, 
        name='MetaValor'),

    path('meta-operadores/',views.meta_operador,
         name='MetaOperadores'),
]