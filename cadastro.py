import oracledb
import conexao

# Função para cadastrar os custos no banco de dados
def cadastrar_custo(connection, custo_prod, custo_adm, comissao_venda, imposto, lucro):
    cursor = connection.cursor()

    # Consulta SQL para atualizar os custos na tabela preco
    sql = "INSERT INTO preco (CUSTO_PROD, CUSTO_ADM, COMISSAO_VENDA, IMPOSTO, LUCRO) VALUES (:1, :2, :3, :4, :5)"
    
    try:
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (custo_prod, custo_adm, comissao_venda, imposto, lucro))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Custos cadastrados com sucesso.")
    except oracledb.Error as e:
        print("Erro ao cadastrar custos:", e)
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()

# Função para cadastrar um produto no banco de dados
def cadastrar_produto(connection, cod_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod):
    cursor = connection.cursor()

    # Consulta SQL para inserir um novo produto
    sql = "INSERT INTO produtos (ID_PROD, NOME_PROD, PRECO_PROD, CATEGORIA_PROD, QNT_PROD) VALUES (:1, :2, :3, :4, :5)"
    
    try:
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (cod_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Produto cadastrado com sucesso.")
    except oracledb.Error as e:
        print("Erro ao cadastrar produto:", e)
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()

# Função para obter os dados necessários para o cálculo do preço de venda
def obter_dados_para_calculo_preco_venda(connection):
    cursor = connection.cursor()

    # Consulta SQL para obter os dados necessários para o cálculo do preço de venda
    sql = "SELECT CUSTO_PROD, CUSTO_ADM, COMISSAO_VENDA, IMPOSTO, LUCRO FROM PRECO"

    try:
        # Executar a consulta
        cursor.execute(sql)

        # Recuperar os resultados da consulta
        row = cursor.fetchone()
        if row:
            return row
        else:
            print("Não foi possível obter os dados para o cálculo do preço de venda.")
            return None
    except oracledb.Error as e:
        print("Erro ao obter dados para o cálculo do preço de venda:", e)
        return None
    finally:
        cursor.close()

# Informações de conexão ao banco de dados
username = conexao.username
password = conexao.password
connect_string = conexao.connect_string

try:
    connection = oracledb.connect(user=username, password=password, dsn=connect_string)
    
    print("Sistema Papelaria\n")

    while True:
        print("Selecione uma opção:")
        print("1. Calcular preço de venda")
        print("2. Cadastrar produto")
        print("3. Cadastrar custo")
        print("4. Sair")

        esc = int(input("Opção: "))

        if esc == 1:
            # Obter os dados necessários para o cálculo do preço de venda
            dados_calculo = obter_dados_para_calculo_preco_venda(connection)
            if dados_calculo:
                custo_prod, custo_adm, comissao_venda, imposto, lucro = dados_calculo
                
                # Calcular o preço de venda
                preco_venda = custo_prod / (1 - ((custo_adm + comissao_venda + imposto + lucro) / 100))

                # Calcular valores adicionais 
                B = custo_prod * 100 / preco_venda 
                C = preco_venda - custo_prod
                CC = C * 100 / preco_venda
                D = custo_adm / 100 * preco_venda
                E = comissao_venda / 100 * preco_venda
                F = imposto / 100 * preco_venda
                G = D + E + F
                GG = G * 100 / preco_venda
                H = C - G
                
                # Determinar o tipo de lucro
                r = (H / preco_venda) * 100
                if r <= 0:
                    tipo_lucro = "Prejuízo"
                elif 0 < r <= 10:
                    tipo_lucro = "Lucro baixo"
                elif 10 < r <= 20:
                    tipo_lucro = "Lucro médio"
                else:
                    tipo_lucro = "Lucro alto"
                
                # Imprimir os resultados 
                print("Descrição                             Valor                      %")
                print(f"A. Preço de Venda                     {preco_venda:.2f}        100%")
                print(f"B. Custo de Aquisição (Fornecedor)    {custo_prod:.2f}         {B:.2f}%")
                print(f"C. Receita Bruta (A-B)                {C:.2f}                  {CC:.2f}%")
                print(f"D. Custo Fixo/Administrativo          {D:.2f}                  {custo_adm:.2f}%")
                print(f"E. Comissão de Vendas                 {E:.2f}                  {comissao_venda:.2f}%")
                print(f"F. Imposto                           {F:.2f}                   {imposto:.2f}%")
                print(f"G. Outros custos (D+E+F)              {G:.2f}                  {GG:.2f}%")
                print(f"H. Rentabilidade (C-G)                {H:.2f}                  {r:.2f}% - {tipo_lucro}")
            else:
                print("Não foi possível calcular o preço de venda.")

        elif esc == 2:
            print("Cadastrar produto.\n")
            cod_prod = int(input("Inserir o código do produto: \n"))
            nome_prod = input("Inserir nome do produto: \n")
            preco_prod = float(input("Inserir o preço de venda do produto: \n"))
            categoria_prod = input("Inserir a categoria do produto: \n")
            quantidade_prod = int(input("Inserir quantidade do produto em estoque: \n"))

            cadastrar_produto(connection, cod_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod)

        elif esc == 3:
            print("Cadastrar custo.\n")
            custo_prod = float(input("Custo do produto: "))
            custo_adm = float(input("Custo administrativo: "))
            comissao_venda = float(input("Comissão de venda: "))
            imposto = float(input("Imposto: "))
            lucro = float(input("Lucro: "))

            cadastrar_custo(connection, custo_prod, custo_adm, comissao_venda, imposto, lucro)
        elif esc == 4:
            break

        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")

except oracledb.Error as e:
    print("Erro ao conectar ao banco de dados Oracle:", e)

finally:
    if 'connection' in locals():
        connection.close()

print("\nPrograma encerrado.")
