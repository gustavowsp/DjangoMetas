QUERY_FUNCIONARIOS = """SELECT 
	DISTINCT
    NOME,
	CPF,
    CODIGO_ML
	
FROM
	dw.dbo.v_ml_funcionario
where CPF IN
("""

INSERT_META = """
INSERT INTO
        HOMOLOGACAO.DBO.ML_14072023_TESTE_METADEFLATOES(
		COMP, 
		CENTRO_CUSTO,
		COD_CRED,
		NOM_CREDOR,
		COD_FUNC,
		NOME_OPERADOR,
		CPF,
		MATRICULA,
		FALTAS_QTDE,
		ADVERTENCIAS_QTDE,
		RECLAMAÇÕES_QTDE,
		MONITORIA_NOTA,
		SUSPENSAO_QTDE, 
		QUEM_VALIDOU,
		DATA_VALIDAÇÃO,
        QUEM_IMPORTOU,
		DATA_IMPORT
		)
VALUES

"""


CODIGO_FUNCIONARIO = """
/*Selecionando informações dos funcionários -- BRADESCO*/


SELECT 
	   TOP (4000) 
	   [COD_FUNC]
      ,[CPFCGC_PES]
  FROM 
	  [CobReports_Tambore].[dbo].[FUNCIONARIOS]
  WHERE 
	  ATIVO != 'NÃO' 
	 AND ATIVO = 'SIM'
  /*Selecionando informações dos funcionários -- BRADESCO*/

  UNION ALL

  /*Selecionando informações dos funcionários -- ITAU*/
  SELECT TOP (1000) 
	   [COD_FUNC]
      ,[CPFCGC_PES]
  FROM [CobReports_Itau].[dbo].[FUNCIONARIOS]
  WHERE ATIVO != 'NÃO' AND ATIVO = 'SIM'
 /*Selecionando informações dos funcionários -- ITAU*/

  UNION ALL
  /*Selecionando informações dos funcionários -- DIVERSOS*/
  SELECT TOP (1000) 
        [COD_FUNC]
      ,[CPFCGC_PES]
  FROM [CobReports_Diversos].[dbo].[FUNCIONARIOS]
  WHERE ATIVO != 'NÃO' AND ATIVO = 'SIM'

"""