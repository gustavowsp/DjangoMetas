QUERY_FUNCIONARIOS = """\
SELECT 
	NOME,
	CPF,
	DT_NASC
FROM
	dw.dbo.v_ml_funcionario
WHERE 
	SIT_EMPRE != 'DEMITIDO' AND
	CPF  NOT IN 
"""
QUERY_FUNCIONARIOS_SEM_CPF =  """\
SELECT 
	NOME,
	CPF,
	DT_NASC
FROM
	dw.dbo.v_ml_funcionario
WHERE 
	SIT_EMPRE != 'DEMITIDO'
"""