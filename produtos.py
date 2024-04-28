import oracledb  # Importa o módulo para interagir com o banco de dados Oracle
import conexao  # Importa o módulo com informações de conexão ao banco de dados
from colorama import Fore, Style  # Importa módulos para estilização de texto colorido no terminal

# Função para cadastrar os custos no banco de dados
def cadastrar_custo(connection, id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para atualizar os custos na tabela preco
    sql = "INSERT INTO preco (ID_PROD, CUSTO_PROD, CUSTO_ADM, COMISSAO_VENDA, IMPOSTO, LUCRO) VALUES (:1, :2, :3, :4, :5, :6)"
    
    try:
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Custos cadastrados com sucesso.")  # Exibir mensagem de sucesso
    except oracledb.Error as e:
        print("Erro ao cadastrar custos:", e)  # Em caso de erro, exibir mensagem de erro
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()  # Fechar o cursor

# Função para cadastrar um produto no banco de dados
def cadastrar_produto(connection, id_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_prod):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para inserir um novo produto
    sql = "INSERT INTO produtos (ID_PROD, NOME_PROD, PRECO_PROD, CATEGORIA_PROD, QNT_PROD, DESC_PROD) VALUES (:1, :2, :3, :4, :5, :6)"
    
    try:
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (id_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_prod))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Produto cadastrado com sucesso.")  # Exibir mensagem de sucesso

        # Exibir informações do produto cadastrado
        print("ID: ", id_prod)
        print("Nome: ", nome_prod)
        print("Preço: ", preco_prod)
        print("Categoria: ", categoria_prod)
        print("Quantidade: ", quantidade_prod)
        print("Descrição: ", desc_prod)
        
    except oracledb.Error as e:
        print("Erro ao cadastrar produto:", e)  # Em caso de erro, exibir mensagem de erro
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()  # Fechar o cursor

# Função para obter os dados necessários para o cálculo do preço de venda
def obter_dados_para_calculo_preco_venda(connection, id_prod):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para obter os dados necessários para o cálculo do preço de venda
    sql = "SELECT CUSTO_PROD, CUSTO_ADM, COMISSAO_VENDA, IMPOSTO, LUCRO FROM PRECO WHERE ID_PROD = :1"

    try:
        # Executar a consulta
        cursor.execute(sql, (id_prod,))

        # Recuperar os resultados da consulta
        row = cursor.fetchone()
        if row:
            # Se o lucro for zero, classificar como "Prejuízo"
            if row[4] == 0:
                return row[:4] + (-1,)  # Definir o lucro como -1 (indicando prejuízo)
            else:
                return row
        else:
            print("Não foi possível obter os dados para o cálculo do preço de venda.")
            return None
    except oracledb.Error as e:
        print("Erro ao obter dados para o cálculo do preço de venda:", e)
        return None
    finally:
        cursor.close()  # Fechar o cursor

# Função para verificar se o ID do produto existe na tabela PRECO
def verificar_existencia_id(connection, id_prod):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para verificar a existência do ID do produto na tabela PRECO
    sql = "SELECT 1 FROM PRECO WHERE ID_PROD = :1"

    try:
        # Executar a consulta
        cursor.execute(sql, (id_prod,))

        # Verificar se há alguma linha retornada pela consulta
        if cursor.fetchone():
            return True  # ID do produto existe na tabela PRECO
        else:
            return False  # ID do produto não existe na tabela PRECO
    except oracledb.Error as e:
        print("Erro ao verificar existência do ID do produto:", e)
        return False
    finally:
        cursor.close()  # Fechar o cursor

# Função para imprimir a tabela de lucro com formatação colorida
def imprimir_tabela_lucro(tipo_lucro):
    # Primeira linha da tabela
    print("TABELA DE LUCRO")

    # Segunda linha (cabeçalho)
    print("CLASSIFICAÇÃO", "|", "LUCRO")

    # Dicionário de cores para cada tipo de lucro
    cores = {
        "Lucro alto": Fore.BLUE,
        "Lucro médio": Fore.GREEN,
        "Lucro baixo": Fore.YELLOW,
        "Prejuízo": Fore.RED,
    }

    # Dicionário de classificações e lucros
    tabela = {
        "Lucro alto": "> 20%",
        "Lucro médio": ">10 - 20%",
        "Lucro baixo": ">0 - 10%",
        "Prejuízo": "<= 0%",
    }

    for classificacao, lucro in tabela.items():
        # Verificar se é o tipo de lucro atual e aplicar a cor correspondente
        if classificacao == tipo_lucro:
            print(cores[classificacao] + classificacao, "|", lucro)
        else:
            print(Style.RESET_ALL + classificacao, "|", lucro)

    # Resetar a cor para o texto normal após imprimir a tabela
    print(Style.RESET_ALL)

# Função para buscar um produto pelo nome e verificar se existe
def buscar_produto(connection, nome_produto):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para buscar um produto pelo nome
    # Consulta SQL para buscar um produto pelo nome (case-insensitive)
    sql = "SELECT ID_PROD, NOME_PROD, PRECO_PROD, CATEGORIA_PROD, QNT_PROD, DESC_PROD FROM produtos WHERE UPPER(NOME_PROD) LIKE UPPER(:1)"


    try:
        # Executar a consulta
        cursor.execute(sql, (f'%{nome_produto}%',))

        # Recuperar os resultados da consulta
        rows = cursor.fetchall()
        
        if rows:
            print("Resultados da busca:")
            for row in rows:
                # Exibir informações do produto encontrado
                print("ID: ", row[0])
                print("Nome: ", row[1])
                print("Preço: ", row[2])
                print("Categoria: ", row[3])
                print("Quantidade: ", row[4])
                print("Descrição: ", row[5])
                print()  # Adicionar uma linha em branco entre os produtos encontrados
            return True  # Indicar que o produto foi encontrado
        else:
            print("Nenhum produto encontrado com esse nome.")
            return False  # Indicar que o produto não foi encontrado

    except oracledb.Error as e:
        print("Erro ao buscar produto pelo nome:", e)
        return False  # Indicar que houve um erro na busca
    finally:
        cursor.close()  # Fechar o cursor
    
def excluir_produto (connection, id_prod): # funçao para excluir produto 
    cursor = connection.cursor()  # cria um cursor para executar comandos no banco de dados.          

    # consulta sql para deletar um produto pelo id.
    sql = "DELETE FROM PRODUTOS WHERE ID_PROD = : 1"

    try:
        # executa a consulta.
        cursor.execute (sql,(id_prod,))
        # confirmar a transaçao do banco de dados.
        connection.commit ()
        if cursor.rowcount >0:
            print(f"produto com id {id_prod} foi excluido com sucesso.") # exibir mensagem de sucesso.
        else:
            print(f"produto com id {id_prod} nao foi encontrado.") # exibir mensagem se o produto nao for encontrado.
    except oracledb.Error as e: 
        print("Erro ao excluir produto:", e) # exibir mensagem de erro.
        connection.rollback () # reverter a transaçao em caso de erro.
    finally:
        cursor.close()  # Fechar o cursor

# Informações de conexão ao banco de dados
username = conexao.username  # Nome de usuário para conexão
password = conexao.password  # Senha para conexão
connect_string = conexao.connect_string  # String de conexão ao banco de dados

try:
    connection = oracledb.connect(user=username, password=password, dsn=connect_string)  # Conectar ao banco de dados
    
    print("Sistema Papelaria\n")  # Exibir mensagem de boas-vindas

    while True:  # Loop principal do programa
        print("Selecione uma opção:")  # Exibir opções para o usuário
        print("1. Calcular preço de venda")
        print("2. Cadastrar produto")
        print("3. Cadastrar custo")
        print("4. Consultar produto")
        print("5. Excluir produto")
        print("6. Sair")

        esc = int(input("Opção: "))  # Ler a opção escolhida pelo usuário

        if esc == 1:  # Se a opção escolhida for calcular preço de venda
            # Obter o ID do produto do usuário
            id_produto = int(input("Insira o ID do produto: "))

            # Verificar a existência do ID do produto na tabela PRECO
            if verificar_existencia_id(connection, id_produto):
                # Obter os dados necessários para o cálculo do preço de venda
                dados_calculo = obter_dados_para_calculo_preco_venda(connection, id_produto)
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

                    # Imprimir tabela de lucro com formatação colorida
                    imprimir_tabela_lucro(tipo_lucro)
            else:
                print("O ID do produto não está registrado.")  # Exibir mensagem se o ID do produto não estiver registrado

        elif esc == 2:  # Se a opção escolhida for cadastrar produto
            print("Cadastrar produto.\n")  # Exibir mensagem para o usuário
            # Solicitar informações do produto ao usuário
            cod_prod = int(input("Inserir o código do produto: \n"))
            nome_prod = input("Inserir nome do produto: \n")
            preco_prod = float(input("Inserir o preço de venda do produto: \n"))
            categoria_prod = input("Inserir a categoria do produto: \n")
            quantidade_prod = int(input("Inserir quantidade do produto em estoque: \n"))
            desc_prod = input(("Inserir a descrição do produto: \n"))

            # Chamar a função para cadastrar o produto no banco de dados
            cadastrar_produto(connection, cod_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_prod)

        elif esc == 3:  # Se a opção escolhida for cadastrar custo
            print("Cadastrar custo.\n")  # Exibir mensagem para o usuário
            # Solicitar informações do custo ao usuário
            id_prod = int(input("Inserir o código do produto: \n"))
            custo_prod = float(input("Custo do produto: "))
            custo_adm = float(input("Custo administrativo: "))
            comissao_venda = float(input("Comissão de venda: "))
            imposto = float(input("Imposto: "))
            lucro = float(input("Lucro: "))

            # Chamar a função para cadastrar o custo no banco de dados
            cadastrar_custo(connection, id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro)
        elif esc == 4:  # Se a opção escolhida for buscar produto por nome
            print("Buscar produto por nome.\n")  # Exibir mensagem para o usuário
            # Solicitar nome do produto ao usuário
            nome_produto = input("Digite o nome do produto: ")
            # Verificar se o produto existe no banco de dados antes de exibir suas informações
            if buscar_produto(connection, nome_produto):
                # Se o produto existir, as informações já foram exibidas dentro da função buscar_produto_por_nome
               pass
            else:
               print("O produto não está registrado no banco de dados.")

        elif esc == 5:
            # solicitar id do produto ao usuario.
            id_prod = int(input("Digite o id do produto que deseja excluir: "))

            # chamar a funçao para excluir produto com id especifico.
            excluir_produto(connection,id_prod)


        elif esc == 6:  # Se a opção escolhida for sair
            break  # Encerrar o loop
        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")  # Exibir mensagem de opção inválida

except oracledb.Error as e:
    print("Erro ao conectar ao banco de dados Oracle:", e)  # Exibir mensagem de erro em caso de falha na conexão

finally:
    if 'connection' in locals():
        connection.close()  # Fechar a conexão com o banco de dados

print("\nPrograma encerrado.")  # Exibir mensagem de encerramento do programa




