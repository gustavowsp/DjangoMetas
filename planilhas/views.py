from django.shortcuts import render,redirect
from django.contrib import messages
import openpyxl
import pyodbc
from openpyxl.styles import PatternFill, Font
import random


# Create your views here.
def index(request):
    return render(request, 'planilhas/index.html')

def incremento(request):


    INSERT_INCREMENTO_META = """INSERT INTO HOMOLOGACAO.DBO.ML_12062023_TESTE_METAINCREMENTO 
VALUES """

    def desativando(cursor,cn):
        cursor.close()
        cn.close()

    def verify_carteira(carteira):
        """
        True: Existe
        False: Não Existe

        Essa função verifica se a carteira 
        que foi enviada existe"""

        #TODO: Seria interresante puxar as carteiras existentes, de cada meta, de um banco de dados
        # Assim, sempre que uma nova carteira surgir, é so adicionar no banco de dados e ela passará a passar na nossa validação
        # Por enquanto se uma nova carteira surge, temos que mudar no hardcode

        # True - Existe   |   False - Não existe
        carteira_existe = False

        carteiras_existentes = (
            'alto_ticket',
            'comercial_imobiliario',
            'veiculos_amg',
            'veiculos_lp',
            'consorcio_imo_jur',
            'comercial_juri',
            'credito_imobiliario_juamg',
            'veiculos_juri',
        )

        if carteira in carteiras_existentes:
            carteira_existe = True

        return carteira_existe

    def is_excel(plan):
        """
        True: é uma planilha excel
        False: Não é uma planilha excel
        """
        
        try: # Só abre se for excel, caso não vai dar erro
            openpyxl.load_workbook(plan)
            is_excel = True
        except:
            is_excel =  False

        return is_excel

    def sheet_exists(plan):
        """
        A página de dados existe?
        Sim : True
        Não : False

        Essa função verifica se a aba de dados existe, para que possamos ter acesso aos dados.
        """

        if 'Dados' not in plan.sheetnames:
            exist = False
        else:
            exist = True

        return exist

    def headers_is_corretct(plan,tipo):
        """
        True: Está correto
        False: Está incorreto

        Essa função verifica se os cabeçalhos da meta existem, caso não existam, possívelmente estamos abrindo
        uma planilha errada, que possui uma aba nomeada DADOS.
        """

        header_plan = []

        if tipo == 'incremento':
            header_default = [
                'COMP',
                'CARTEIRA',
                'FRENTE', 
                'TIPO_META', 
                'META_1', 
                'META_2', 
                'META_3', 
                'META_4',
                'META_5'
            ]            
            max_col = 9
        elif tipo == 'operadores':        
            header_default = [
                'COMPETENCIA',
                'DATA_IMPORT',	
                'QUEM_IMPORTOU',	
                'COD_CRED',	
                'NOME_CREDOR',	
                'COD_FUNC',
                'NOME_FUNCIONARIO',
                'SUPERVISOR'	,
                'FRENTE'	,
                'META_QTDE'	 ,
                'META_HONORARIOS', 	 
                'META_REPASSE' 	 ,
                'META_VALOR' 	 ,
                'META_ATIVA' 	,
                'TURNO'   	,
                'ATUAÇÃO'	,
                'ESTAGIO'	,
                'DATA_INI'	,
                'DATA_FIN'	,
                'TIPO_MEDICAO',

            ]
            max_col = 20


        #TODO: Criar um sistema que muda o local de busca de valores, já que em metas operadores está em um local e incremento meta em outro
        for row in plan.iter_rows(min_row=3, max_row=3, max_col=max_col ):
            for cell in row:
                header_plan.append(cell.value)

        
        return header_plan == header_default

    def get_data_meta_com_duplicatas(plan,max_col):
        """
        Retorna um dicionário com nomes das colunas em forma de key, e os dados na forma de valores da key.
        """

        dados = []

        # Passa por cada coluna
        for row in plan.iter_rows(min_row=4, max_col=max_col):

            # Criando uma key com o nome da coluna COMP, ela recebe o valor lista, para que possamos adicionar valores
            dados.append([])

            # Adicionando valores na key atual
            for cell in row:
            

                dados[-1].append(cell.value)  

        return dados

    def get_data_meta_sem_duplicatas(plan,max_col):
        """
        Retorna um dicionário com nomes das colunas em forma de key, e os dados na forma de valores da key.
        """

        dados = {

        }

        # Passa por cada coluna
        for row in plan.iter_cols(min_row=3, max_col=max_col):

            # Criando uma key com o nome da coluna COMP, ela recebe o valor lista, para que possamos adicionar valores
            dados[row[0].value] = set()

            # Adicionando valores na key atual
            for cell in row:
                
                # Se o valor da célula for o nome da coluna, pule o looping
                if cell.value == row[0].value:
                    continue

                dados[row[0].value].add(cell.value)  

        return dados

    def format_number(plan):

        fundo_vermelho = PatternFill("solid", fgColor="EB607F")
        font_bold = Font(bold=True)

        for coluna in plan.iter_cols(min_col=5 ,min_row=4, max_col=9):
            for cell in coluna:
                if type(cell.value) != int:
                    cell.fill = fundo_vermelho
                    cell.font = font_bold
        return plan

    def pegue_um_numero_aleatorio():
        numro_um = random.randint(0,999)
        numro_dois = random.randint(1,9)
        numro_tres = random.randint(9,99)

        return f'{numro_um}{numro_dois}{numro_tres}'

    def execute_consulta(consulta):
     
        def conectando():

            
            
            cn = pyodbc.connect(f'DRIVER={"SQL Server"};SERVER=10.10.5.31;DATABASE=METAS;UID=planejamento;PWD=pl@n1234')
            
            cursor = cn.cursor()
            return (cursor,cn)
                    

        cursor,cn = conectando()
        # Executando uma consulta
        try:
            cursor.execute(consulta)
        except:
            return cursor.fetchone, cursor,cn, True    
                
        # Pegando o resultado da consulta
        return cursor.fetchone, cursor,cn, False
    

    if request.method == 'POST':
        """RECUPERAÇÃO DE INFORMAÇÕES
        
        Nesta etapa vamos recuperar e verificar se foi enviado
        as informações necessárioas para o funcionamento da view."""


        # Pegando informações, nome carteira e planilhas
        #--------------------------------------------------
        carteira = request.POST.get('carteira')
        
        # Recuperando planilhas
        try:
            meta_op = request.FILES['meta_mae']
            incremento_meta = request.FILES['meta_filha']
        except:
            messages.add_message(
                request,
                messages.WARNING, 
                "Ops! Você se esqueceu de enviar uma das planilhas"
                )
            return render(request, 'planilhas/metas.html')
        
        # Verificando se carteira existe
        if not verify_carteira(carteira): 
            messages.add_message(request ,messages.ERROR, "Essa carteira não existe...")
            return render(request, 'planilhas/metas.html')
        


        # Os arquivos enviados, são realmentes planilhas excel?
        if not is_excel(meta_op): 
            messages.add_message(request,messages.ERROR, "Ops! O que foi enviado no campo meta operadores, não era uma planilha ")
            return render(request, 'planilhas/metas.html')
        else:
            meta_op = openpyxl.load_workbook(meta_op) # Abrindo a planilha
        
        if not is_excel(incremento_meta):
            messages.add_message(request,messages.ERROR, "Ops! O que foi enviado no campo incremento meta, não era uma planilha ")
            return render(request, 'planilhas/metas.html')
        else:
            incremento_meta = openpyxl.load_workbook(incremento_meta)



        # Verificando se a página de dados existe
        if not sheet_exists(meta_op):
            messages.add_message(
                request,
                messages.ERROR, 
                "Ops! a página 'dados' na planilha meta operadores, não pode ser encontrada. Baixe nosso layout de metas e insira os dados!")
            return render(request, 'planilhas/metas.html')
        else:
            meta_op_dados = meta_op['Dados']
        
        if not sheet_exists(incremento_meta):
            messages.add_message(
                request,
                messages.ERROR, 
                "Ops! a página 'dados' na planilha incremento meta, não pode ser encontrada. Baixe nosso layout de metas e insira os dados!")
            return render(request, 'planilhas/metas.html')
        else:
            incremento_meta_dados = incremento_meta['Dados']



        # Verificando se os cabecalhos são os esperados
        if not headers_is_corretct(incremento_meta_dados,'incremento'):
            messages.add_message(
                request,
                messages.WARNING,
                "Não foi possível encontrar o cabeçalho de informações, na aba de dados, na planilha incremento meta. Você está enviando a meta correta? Verifique!"
            )
            return render(request, 'planilhas/metas.html')

        if not headers_is_corretct(meta_op_dados,'operadores'):
            messages.add_message(
                request,
                messages.WARNING,
                "Não foi possível encontrar o cabeçalho de informações, na aba de dados, na planilha meta operadores. Você está enviando a meta correta? Verifique!"
            )
            return render(request, 'planilhas/metas.html')

 

        # VALIDANDO AS INFORMAÇÕES EXISTENTES NA PLANILHA ENVIADA
        #----------------------------------------------------------------
        dados_incremento = get_data_meta_sem_duplicatas(incremento_meta_dados,9)
        dados_operadores = get_data_meta_sem_duplicatas(meta_op_dados,20)

        # Formatando o campo TIPO MEDICAO da meta de operadors, para poder comparar com a outra planilha
        def formatando_tipo_medicao(valores):

            new_values = set()
            for valor in valores:
                new_values.add(valor.replace('_',' - '))
            
            return new_values
        
        validador_um = dados_incremento['COMP'] == dados_operadores['COMPETENCIA'] and dados_incremento['FRENTE'] == dados_operadores['FRENTE']
        validador_dois = dados_incremento['CARTEIRA'] == dados_operadores['NOME_CREDOR'] and dados_incremento['TIPO_META'] == formatando_tipo_medicao(dados_operadores['TIPO_MEDICAO'])

        if not validador_um and not validador_dois:
            messages.add_message(request,messages.ERROR,'Os dados das planilhas estão incorretos.')
            return render(request, 'planilhas/metas.html')

        #TODO: Criar sistema que preenche o nome da carteira com o cod cred na planilha.



        # Formatando o campo METAS, da planilha de incremento
        # Verificando se são números, não há espaços em brancos

        row = {
            'META_1' : {
                'coluna_dados' : dados_incremento['META_1'],
                'coluna_local' : 5
                },

            'META_2' : {
                'coluna_dados' : dados_incremento['META_2'],
                'coluna_local' : 6
                },

            'META_3' : {
                'coluna_dados' : dados_incremento['META_3'],
                'coluna_local' : 7
                },

            'META_4' : {
                'coluna_dados' : dados_incremento['META_4'],
                'coluna_local' : 8
                },

            'META_5' : {
                'coluna_dados' : dados_incremento['META_5'],
                'coluna_local' : 9
                },
        }     
        
        exists_str = bool()

        # Passando em cada letra, de cada meta e verificando se há letras ou espaços
        for conjunto_dados in row.values():
    
            for meta in conjunto_dados['coluna_dados']:
               if type(meta) != int:
                   exists_str = True
                   break
            
        if exists_str:
            format_number(incremento_meta_dados) # Formatando campos incorretos da página.
            messages.add_message(request,messages.ERROR,'Alguns dados contidos na planilhas, não são do tipo correto')

            while True:
                try:
                    numero_aleatorio = pegue_um_numero_aleatorio()
                    incremento_meta.save(
                        f'templates/global/planilhas/planilha_com_erro{numero_aleatorio}.xlsx'
                        )
                    nome_planilha_incorreta = f'planilha_com_erro{numero_aleatorio}.xlsx'
                    break
                except:
                    ...


            contexto = {
                'url' : f'/media/{nome_planilha_incorreta}'
            }

            #TODO: Enviar planilha devolta para o usuário.
            return render(
                request, 
                'planilhas/metas.html',
                contexto
                ) 


        # Importando a meta
        data_planilha_incremento = get_data_meta_com_duplicatas(incremento_meta_dados,9)
        
        def criando_valors_para_insert(valores):
            
            consulta = str()


            linhas_existentes_planilha =len(valores)
            linha_atual = 0

            for row in valores:
                consulta += ' ( '

                celula_atual = 0
                for cell in row:

                    # Adicionando o valor na consulta
                    if type(cell) == str:
                        consulta += "'"
                        consulta += cell
                        consulta += "'"
                    else:
                        consulta += str(cell)
                    
                    celula_atual += 1
                    if celula_atual < 9:
                        consulta += ', '
                
                linha_atual += 1
                if linha_atual < linhas_existentes_planilha:
                    consulta += ' ), '
                else:
                    consulta += ') '
            return consulta
       
        consulta = criando_valors_para_insert(data_planilha_incremento)
        consulta_final = (INSERT_INCREMENTO_META + consulta)

        itens = execute_consulta(consulta_final)

        if itens[3]:
            desativando(itens[1],itens[2])
            messages.add_message(request,messages.ERROR,"Ops, algo deu errado. Contate o desenvolvedor, não conseguimos importar sua planilha para o banco de dados")
            return render(request, 'planilhas/metas.html')
        
        else:
            itens[2].commit()        
            desativando(itens[1],itens[2])

        # Deu tudo certo e estamos importando
        messages.add_message(request,messages.SUCCESS, "Importada com sucesso!")
        return render(request, 'planilhas/metas.html')


    return render(request, 'planilhas/metas.html')

def valor(request):
    messages.add_message(request,messages.INFO,"Estamos desenvolvendo esta página ainda... ")
    return redirect('planilhas:HomePage') 

def deflator(request):
    messages.add_message(request,messages.INFO,"Estamos desenvolvendo esta página ainda... ")
    return redirect('planilhas:HomePage') 

