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
		--SUSPENSAO_QTDE, Criar coluna na planilha primeiro
		QUEM_VALIDOU,
		DATA_VALIDAÇÃO,
        QUEM_IMPORTOU,
		DATA_IMPORT
		)
VALUES

"""