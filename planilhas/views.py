from django.shortcuts import render,redirect
from django.contrib import messages
import planilhas.viewsfunc.view_incremento as incremento_functions
import openpyxl
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, 'planilhas/index.html')

def incremento(request):

    if request.method == 'POST':

        carteira = request.POST.get('carteira')
        
        # C000
        try:
            meta_op = request.FILES['meta_mae']
            incremento_meta = request.FILES['meta_filha']
            # Pegamos as duas planilhas
        except:
            messages.add_message(
                request,
                messages.WARNING, 
                "Ops! Você se esqueceu de enviar uma das planilhas"
                )
            return render(request, 'planilhas/metas.html')
            # O usuário não enviou as planilhas e recuperamos algo que não existe, ocasionando em um erro.
        
        # Verificamos que as planilhas de metas foram enviadas.


        # C001
        metas_erradas, planilhas_or_template,  = incremento_functions.informacoes_corretas(
            request,
            carteira=carteira,
            meta_op=meta_op,
            incremento_meta=incremento_meta,
            meta='incremento'
        )
        # Verificamos se as planilhas estão corretas e se a carteira existe.
        incremento_meta = openpyxl.load_workbook(incremento_meta)


        # R000
        if metas_erradas:
            return render(
                metas_erradas, # Existe um requeste nesta variável.
                planilhas_or_template
            )
        # As metas estavam erradas então vamos retornar um erro



        # C002
        # Pegando a sheet de dentro da tupla, que foi retornada na função anteior.
        incremento_sheet_dados = planilhas_or_template[0]
        metaop_sheet_dados = planilhas_or_template[1]
    
        # Pegando os valores das planilhas.
        dados_incremento = incremento_functions.recuperar_informacoes_unicas(incremento_sheet_dados,9)
        dados_operadores = incremento_functions.recuperar_informacoes_unicas(metaop_sheet_dados,20)


        # C003
        # Verificando se há linhas excedentes na planilha
        existem_linhas_excedentes = incremento_functions.existem_linhas_excedentes(incremento_sheet_dados)
        if existem_linhas_excedentes:
            messages.add_message(request,messages.ERROR, 'Em sua planilha há linhas que possuem células vazias, preenchas!')
            return render(request,'planilhas/metas.html')



        # C004
        # Comparando os valores de cada coluna chave com a planilha de metas operadores
        metas_erradas = incremento_functions.comparacao_dados(request,dados_incremento,dados_operadores)
        if metas_erradas:
            request = metas_erradas[0]
            template = metas_erradas[1]
            return render(request,template)

        # Verificando se o nome está correto
        nome_carteira_errado = incremento_functions.validando_nome_carteira(request,carteira,dados_incremento)
        if nome_carteira_errado:
            return render(request, 'planilhas/metas.html')
        
        # Alterando o nome_cred na planilha para o nome padrão
        total_linhas_pagina = incremento_functions.contar_linhas(incremento_sheet_dados)
        incremento_sheet_dados = incremento_meta['Dados']        
        incremento_functions.padronizando_nome_cartira(incremento_sheet_dados,carteira,total_linhas_pagina)
        
        # Pegando os novos valores, já que alterei acima.
        dados_incremento = incremento_functions.recuperar_informacoes_unicas(incremento_sheet_dados,9)


        # C005 -- Formatando células com valores diferentes de int
        row = (
            dados_incremento['META_1'],
            dados_incremento['META_2'],
            dados_incremento['META_3'],
            dados_incremento['META_4'],
            dados_incremento['META_5'],
            )   
        # Há células com outro valor a não ser int?
        if incremento_functions.existe_valores_incorretos(row):
            
            # Formatando as células incorretas
            incremento_functions.format_number(incremento_sheet_dados) 
            # TODO: Retornar planilha formatada para o usuário
            name = incremento_functions.gerador_nome()
            path = 'media/planilha-'
            incremento_meta.save(f'{path}{name}.xlsx')

            context = {
                'planilha_incorreta_url' : f'{path}{name}.xlsx'
            }

            messages.add_message(
                request,
                messages.ERROR,
                'Alguns dados contidos na planilhas, não são do tipo correto')
            return render(
                request, 
                'planilhas/metas.html',
                context
            ) 


        carteiras_da_meta = dados_incremento['CARTEIRA']
        competencia_da_meta = dados_incremento['COMP']
       
        puxando_meta_ativa = incremento_functions.criando_query_meta_ativa(
            carteiras_da_meta,
            competencia_da_meta,
            incremento_functions.BUSCANDO_METAS_ATIVAS)

        itens = incremento_functions.execute_consulta(puxando_meta_ativa)
        query_falhou = itens[2]

        if query_falhou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            meta_existente = itens[0].fetchall()
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql

        # Alterar meta antiga para inativa
        if meta_existente:
            alterando_meta_ativa = incremento_functions.criando_query_meta_ativa(
                carteiras_da_meta,
                competencia_da_meta,
                incremento_functions.ALTERANDO_META_ATIVA
                )
            itens = incremento_functions.execute_consulta(alterando_meta_ativa)
            
            importacao_nao_funcionou = itens[2] 
            if importacao_nao_funcionou:
                incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
                messages.add_message(
                    request,messages.
                    ERROR,
                    "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos alterar meta antiga no banco de dados"
                    )
                return render(request, 'planilhas/metas.html')
            else:
                itens[1].commit() # Confirmando as alterações    
                incremento_functions.desativando(itens[0],itens[1]) # Desativando 



        # C006 - Importando a meta -- Como ativa
        data_planilha_incremento = incremento_functions.get_data_meta_com_duplicatas(incremento_sheet_dados,9)# Pegando os valores da planilha
        consulta = incremento_functions.criando_valors_para_insert(data_planilha_incremento)# Criando a consulta -- Parte dos VALUES
        consulta_final = (incremento_functions.INSERT_INCREMENTO_META + consulta)# Juntando a consulta de VALUES com insert -- COMANDO INTO
        itens = incremento_functions.execute_consulta(consulta_final)# Importando para o banco de dados
        
        importacao_nao_funcionou = itens[2] 
        if importacao_nao_funcionou:
            incremento_functions.desativando(itens[0],itens[1]) # Desativando a conexão sql
            messages.add_message(
                request,messages.
                ERROR,
                "Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados"
                )
            return render(request, 'planilhas/metas.html')
        else:
            itens[1].commit() # Confirmando as alterações    
            incremento_functions.desativando(itens[0],itens[1]) # Desativando


        
        # Deu tudo certo e estamos importando
        messages.add_message(request,messages.SUCCESS, "Importada com sucesso!")
        return render(request, 'planilhas/metas.html')

    return render(request, 'planilhas/metas.html')

def valor(request):
    messages.add_message(request,messages.INFO,"Estamos desenvolvendo esta página ainda... ")
    return redirect('planilhas:HomePage') 

def deflator(request):

    return render(request, 'planilhas/metas.html')
        

def meta_operador(request):
    return render('request','')