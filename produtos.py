import oracledb  # Importa o módulo para interagir com o banco de dados Oracle
import conexao  # Importa o módulo com informações de conexão ao banco de dados
from colorama import Fore, Style  # Importa módulos para estilização de texto colorido no terminal
import numpy as np  # Importa o módulo numpy para lidar com operações de matriz
from sympy import Matrix  # Importa o módulo sympy para lidar com matrizes

# Função para converter uma string em uma lista de valores numéricos
def string_para_numeros(texto, comprimento_chave):
    # Converter cada caractere em um número (exemplo: 'A' a 'Z' -> 0 a 25)
    texto = texto.upper().replace(" ", "")
    numeros = [ord(char) - ord('A') for char in texto]
    # Completar com zeros se o comprimento não for múltiplo do tamanho da chave
    while len(numeros) % comprimento_chave != 0:
        numeros.append(0)
    return numeros

# Função para converter uma lista de valores numéricos em uma string
def numeros_para_string(numeros):
    # Converte uma lista de números em uma string, adicionando 'A' ao número para obter um caractere
    texto = ''.join(chr(num + ord('A')) for num in numeros)
    return texto

# Função para criptografar a descrição utilizando a cifra de Hill
def criptografar_hill(texto, matriz_chave):
    # Obtém o comprimento da chave (número de linhas ou colunas da matriz)
    comprimento_chave = matriz_chave.shape[0]
    # Converte a string em uma lista de números
    numeros = string_para_numeros(texto, comprimento_chave)
    # Lista para armazenar números criptografados
    numeros_criptografados = []
    
    # Criptografa cada bloco de tamanho comprimento_chave da lista de números
    for i in range(0, len(numeros), comprimento_chave):
        # Seleciona um bloco de números com tamanho comprimento_chave
        bloco = np.array(numeros[i:i + comprimento_chave])
        # Multiplica a matriz de chave pelo bloco para criptografar
        bloco_criptografado = np.dot(matriz_chave, bloco) % 26
        # Adiciona o bloco criptografado à lista de números criptografados
        numeros_criptografados.extend(bloco_criptografado)
    
    # Converte a lista de números criptografados de volta para uma string
    texto_criptografado = numeros_para_string(numeros_criptografados)
    return texto_criptografado

# Função para descriptografar a descrição utilizando a cifra de Hill
def descriptografar_hill(texto_criptografado, matriz_chave):
    # Obtém o comprimento da chave (número de linhas ou colunas da matriz)
    comprimento_chave = matriz_chave.shape[0]
    # Converte a string criptografada em uma lista de números
    numeros = string_para_numeros(texto_criptografado, comprimento_chave)
    
    # Calcula a inversa da matriz de chave com módulo 26
    matriz_chave_inv = Matrix(matriz_chave).inv_mod(26)
    
    # Lista para armazenar números descriptografados
    numeros_descriptografados = []
    
    # Descriptografa cada bloco de tamanho comprimento_chave da lista de números
    for i in range(0, len(numeros), comprimento_chave):
        # Seleciona um bloco de números com tamanho comprimento_chave
        bloco = np.array(numeros[i:i + comprimento_chave])
        # Multiplica a inversa da matriz de chave pelo bloco para descriptografar
        bloco_descriptografado = np.dot(matriz_chave_inv, bloco) % 26
        # Adiciona o bloco descriptografado à lista de números descriptografados
        numeros_descriptografados.extend(bloco_descriptografado)
    
    # Converte a lista de números descriptografados de volta para uma string
    texto_descriptografado = numeros_para_string(numeros_descriptografados)
    return texto_descriptografado


# Função para cadastrar os custos no banco de dados
def cadastrar_custo(connection, id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para atualizar os custos na tabela preco
    sql = "INSERT INTO preco (ID_PROD, CUSTO_PROD, CUSTO_ADM, COMISSAO_VENDA, IMPOSTO, LUCRO) VALUES (:1, :2, :3, :4, :5, :6)"
    
    try:
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Custos cadastrados com sucesso. \n")  # Exibir mensagem de sucesso
    except oracledb.Error as e:
        print("Erro ao cadastrar custos: \n", e)  # Em caso de erro, exibir mensagem de erro
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()  # Fechar o cursor

# Função para cadastrar um produto no banco de dados com a descrição criptografada
def cadastrar_produto(connection, id_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_prod, key_matrix):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para inserir um novo produto
    sql = "INSERT INTO produtos (ID_PROD, NOME_PROD, PRECO_PROD, CATEGORIA_PROD, QNT_PROD, DESC_PROD) VALUES (:1, :2, :3, :4, :5, :6)"
    
    try:
        # Criptografar a descrição do produto antes de inseri-la no banco de dados
        desc_criptografada = criptografar_hill(desc_prod, key_matrix)
        
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (id_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_criptografada))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Produto cadastrado com sucesso.")  # Exibir mensagem de sucesso

        # Exibir informações do produto cadastrado
        print("ID: ", id_prod)
        print("Nome: ", nome_prod)
        print("Preço: ", preco_prod)
        print("Categoria: ", categoria_prod)
        print("Quantidade: ", quantidade_prod)
        print("Descrição: \n", desc_prod)
        
    except oracledb.Error as e:
        print("Erro ao cadastrar produto: \n", e)  # Em caso de erro, exibir mensagem de erro
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
            print("Não foi possível obter os dados para o cálculo do preço de venda.\n")
            return None
    except oracledb.Error as e:
        print("Erro ao obter dados para o cálculo do preço de venda: \n", e)
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
def buscar_produto(connection, nome_produto, key_matrix):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para buscar um produto pelo nome
    sql = "SELECT ID_PROD, NOME_PROD, PRECO_PROD, CATEGORIA_PROD, QNT_PROD, DESC_PROD FROM produtos WHERE UPPER(NOME_PROD) LIKE UPPER(:1)"

    try:
        # Executar a consulta
        cursor.execute(sql, (f'%{nome_produto}%',))

        # Recuperar os resultados da consulta
        rows = cursor.fetchall()
        
        if rows:
            print("Resultados da busca:")
            for row in rows:
                # Descriptografar a descrição do produto
                desc_descriptografada = descriptografar_hill(row[5], key_matrix)

                # Exibir informações do produto encontrado
                print("ID: ", row[0])
                print("Nome: ", row[1])
                print("Preço: ", row[2])
                print("Categoria: ", row[3])
                print("Quantidade: ", row[4])
                print("Descrição: \n", desc_descriptografada)  # Exibir descrição descriptografada
                print()  # Adicionar uma linha em branco entre os produtos encontrados
            return True  # Indicar que o produto foi encontrado
        else:
            print("Nenhum produto encontrado com esse nome.\n")
            return False  # Indicar que o produto não foi encontrado

    except oracledb.Error as e:
        print("Erro ao buscar produto pelo nome:\n", e)
        return False  # Indicar que houve um erro na busca
    finally:
        cursor.close()  # Fechar o cursor

# Função para excluir um produto pelo ID
def excluir_produto(connection, id_prod):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados.          

    # Consulta SQL para excluir um produto pelo ID
    sql = "DELETE FROM PRODUTOS WHERE ID_PROD = :1"

    try:
        # Executar a consulta
        cursor.execute(sql, (id_prod,))
        # Confirmar a transação no banco de dados
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Produto com ID {id_prod} foi excluído com sucesso.\n")  # Exibir mensagem de sucesso
        else:
            print(f"Produto com ID {id_prod} não foi encontrado.\n")  # Exibir mensagem se o produto não for encontrado
    except oracledb.Error as e: 
        print("Erro ao excluir produto:\n", e)  # Exibir mensagem de erro
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()  # Fechar o cursor

# Função para alterar as informações de um produto
def alterar_produto(connection, id_prod):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Verificar se o ID do produto existe na tabela produtos
    if verificar_existencia_id(connection, id_prod):
        print(f"Alterando informações do produto com ID {id_prod}.\n")

        # Solicitar as novas informações ao usuário
        novo_nome = input("Inserir novo nome do produto (deixe em branco para manter o atual): ")
        novo_preco = input("Inserir novo preço do produto (deixe em branco para manter o atual): ")
        nova_categoria = input("Inserir nova categoria do produto (deixe em branco para manter a atual): ")
        nova_quantidade = input("Inserir nova quantidade em estoque (deixe em branco para manter a atual): ")
        nova_descricao = input("Inserir nova descrição do produto (deixe em branco para manter a atual): \n")

        # Consulta SQL para atualizar as informações do produto
        sql = "UPDATE produtos SET "

        # Lista para armazenar os campos e valores a serem atualizados
        updates = []
        # Adicionar atualizações de cada campo fornecido pelo usuário
        if novo_nome:
            updates.append(f"NOME_PROD = :nome")
        if novo_preco:
            updates.append(f"PRECO_PROD = :preco")
        if nova_categoria:
            updates.append(f"CATEGORIA_PROD = :categoria")
        if nova_quantidade:
            updates.append(f"QNT_PROD = :quantidade")
        if nova_descricao:
            # Criptografar a nova descrição se fornecida
            nova_descricao_criptografada = criptografar_hill(nova_descricao, key_matrix)
            updates.append(f"DESC_PROD = :descricao")

        # Verificar se houve atualizações
        if updates:
            # Juntar as atualizações em uma string para a consulta
            sql += ", ".join(updates)
            # Completar a consulta com a cláusula WHERE para identificar o produto
            sql += " WHERE ID_PROD = :id"

            # Dicionário de parâmetros para a consulta
            params = {"id": id_prod}
            if novo_nome:
                params["nome"] = novo_nome
            if novo_preco:
                params["preco"] = float(novo_preco)
            if nova_categoria:
                params["categoria"] = nova_categoria
            if nova_quantidade:
                params["quantidade"] = int(nova_quantidade)
            if nova_descricao:
                params["descricao"] = nova_descricao_criptografada

            try:
                # Executar a consulta de atualização
                cursor.execute(sql, params)
                connection.commit()  # Confirmar a transação no banco de dados
                print(f"Produto com ID {id_prod} atualizado com sucesso.\n")
            except oracledb.Error as e:
                print(f"Erro ao alterar o produto com ID {id_prod}: {e}\n")
                connection.rollback()  # Reverter a transação em caso de erro
        else:
            print("Nenhuma atualização fornecida para o produto.\n")
    else:
        print(f"Produto com ID {id_prod} não encontrado na tabela produtos.\n")

    cursor.close()  # Fechar o cursor


#Função adicionar produto na sacola
def adicionar_no_carrinho(connection, id_carrinho, id_prod, nome_prod, preco_prod, qnt_compra):
    cursor = connection.cursor()  # Cria um cursor para executar comandos no banco de dados

    # Consulta SQL para inserir um novo produto
    sql = "INSERT INTO produtos (ID_CARRINHO, ID_PROD, NOME_PROD, PRECO_PROD, QNT_COMPRA) VALUES (:1, :2, :3, :4, :5)"

    try:  
        # Executar a consulta SQL com os parâmetros fornecidos
        cursor.execute(sql, (id_carrinho, id_prod, nome_prod, preco_prod, qnt_compra))
        connection.commit()  # Confirmar a transação no banco de dados
        print("Produto cadastrado com sucesso.")  # Exibir mensagem de sucesso  

    except oracledb.Error as e:
        print("Erro ao cadastrar produto: \n", e)  # Em caso de erro, exibir mensagem de erro
        connection.rollback()  # Reverter a transação em caso de erro
    finally:
        cursor.close()  # Fechar o cursor

# Informações de conexão ao banco de dados
username = conexao.username  # Nome de usuário para conexão
password = conexao.password  # Senha para conexão
connect_string = conexao.connect_string  # String de conexão ao banco de dados

try:
    connection = oracledb.connect(user=username, password=password, dsn=connect_string)  # Conectar ao banco de dados

    # Mensagem de boas-vindas do sistema
    print("Sistema Papelaria\n")

    # Exemplo de matriz de chave para a cifra de Hill (2x2)
    key_matrix = np.array([[3, 3], [2, 5]])

    # Loop principal do programa
    while True:
        # Menu principal
        print("Selecione uma opção:")
        print("1. Custos")
        print("2. Produtos")
        print("3. Vendas")
        print("4. Sair\n")

        # Ler a escolha do usuário
        escolha_principal = int(input("Opção: "))

        if escolha_principal == 1:
            # Menu de custos
            while True:
                print("\nSistema Papelaria: Custos\n")
                print("1. Cadastrar custo")
                print("2. Calcular preço de venda")
                print("3. Voltar ao Menu Principal\n")

                # Ler a escolha do usuário
                escolha_custos = int(input("Opção: "))

                if escolha_custos == 1:
                    # Cadastrar custo
                    print("\nCadastrar custo")
                    id_prod = int(input("Insira o ID do produto: "))
                    custo_prod = float(input("Insira o custo do produto: "))
                    custo_adm = float(input("Insira o custo administrativo: "))
                    comissao_venda = float(input("Insira a comissão de venda: "))
                    imposto = float(input("Insira o imposto: "))
                    lucro = float(input("Insira o lucro: \n"))

                    # Chama a função para cadastrar custo
                    cadastrar_custo(connection, id_prod, custo_prod, custo_adm, comissao_venda, imposto, lucro)

                elif escolha_custos == 2:
                    # Calcular preço de venda
                    print("\nCalcular preço de venda")
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
                                tipo_lucro = "Lucro alto\n"

                            # Imprimir os resultados
                            print("Descrição                             Valor                      %")
                            print(f"A. Preço de Venda                     {preco_venda:.2f}        100%")
                            print(f"B. Custo de Aquisição (Fornecedor)    {custo_prod:.2f}         {B:.2f}%")
                            print(f"C. Receita Bruta (A-B)                {C:.2f}                  {CC:.2f}%")
                            print(f"D. Custo Fixo/Administrativo          {D:.2f}                  {custo_adm:.2f}%")
                            print(f"E. Comissão de Vendas                 {E:.2f}                  {comissao_venda:.2f}%")
                            print(f"F. Imposto                            {F:.2f}                   {imposto:.2f}%")
                            print(f"G. Outros custos (D+E+F)              {G:.2f}                  {GG:.2f}%")
                            print(f"H. Rentabilidade (C-G)                {H:.2f}                  {r:.2f}% - {tipo_lucro}\n")

                            # Imprimir tabela de lucro com formatação colorida
                            imprimir_tabela_lucro(tipo_lucro)
                    else:
                        print("O ID do produto não está registrado.\n")

                elif escolha_custos == 3:
                    # Voltar ao menu principal
                    break
                else:
                    print("Opção inválida. Por favor, escolha uma das opções disponíveis.\n")

        elif escolha_principal == 2:
            # Menu de produtos
            while True:
                print("\nSistema Papelaria: Produtos\n")
                print("1. Cadastrar produto")
                print("2. Consultar produto")
                print("3. Excluir produto")
                print("4. Alterar produto")
                print("5. Voltar ao Menu Principal\n")

                # Ler a escolha do usuário
                escolha_produtos = int(input("Opção: "))

                if escolha_produtos == 1:
                    # Cadastrar produto
                    print("\nCadastrar produto")
                    id_prod = int(input("Insira o ID do produto: "))
                    nome_prod = input("Insira o nome do produto: ")
                    preco_prod = float(input("Insira o preço do produto: "))
                    categoria_prod = input("Insira a categoria do produto: ")
                    quantidade_prod = int(input("Insira a quantidade em estoque: "))
                    desc_prod = input("Insira a descrição do produto: \n")

                    # Chama a função para cadastrar o produto
                    cadastrar_produto(connection, id_prod, nome_prod, preco_prod, categoria_prod, quantidade_prod, desc_prod, key_matrix)

                elif escolha_produtos == 2:
                    # Consultar produto
                    print("\nConsultar produto")
                    nome_produto = input("Digite o nome do produto: \n")

                    # Verificar se o produto existe no banco de dados
                    if buscar_produto(connection, nome_produto, key_matrix):
                        pass
                    else:
                        print("Nenhum produto encontrado com esse nome.\n")

                elif escolha_produtos == 3:
                    # Excluir produto
                    print("\nExcluir produto")
                    id_prod = int(input("Insira o ID do produto que deseja excluir: \n"))

                    # Chama a função para excluir o produto com ID específico
                    excluir_produto(connection, id_prod)

                elif escolha_produtos == 4:
                    # Alterar produto
                    print("\nAlterar produto")
                    id_prod = int(input("Insira o ID do produto que deseja alterar: \n"))
                    alterar_produto(connection, id_prod)

                elif escolha_produtos == 5:
                    # Voltar ao menu principal
                    break
                else:
                    print("Opção inválida. Por favor, escolha uma das opções disponíveis.\n")

        elif escolha_principal == 3:
            # Vendas
            # Consultar produto
            escolha_vendas = 0
            while(escolha_vendas != 3):
                print("\nConsultar produto para adicionar ao carrinho")
                nome_produto = input("Digite o nome do produto: \n")

                # Verificar se o produto existe no banco de dados
                if buscar_produto(connection, nome_produto, key_matrix):
                    pass
                else:
                    print("Nenhum produto encontrado com esse nome.\n")
                
                
                print("1. Adicionar produto ao carrinho")
                print("2. Buscar outro produto")
                print("3. Sair")
                
                escolha_vendas = int(input("Opção: "))
                if escolha_vendas == 1:
                    # Adicionar produto no carrinho
                    #por aqui as coisas pra adicionar
                    id_prod = int(input("Digite o id do produto encontrado: "))
                    qnt_compra = int(input("Quanto desse produto deseja adicionar ao carrinho: "))
                    adicionar_no_carrinho(id_prod, qnt_compra)

                    print("1. Fazer nova busca")
                    print("2. Finalizar venda")
                    escolha_add = int(input("Opção: "))
                    if escolha_add == 1:
                        # Sair para retornar ao while de busca
                        continue
                    elif escolha_add == 2:
                        # Finalizar venda
                        break
                    break
                elif escolha_vendas == 2:
                    # Escolher outro produto
                    continue
                elif escolha_vendas == 3:
                    # Voltar ao menu principal
                    break

        elif escolha_principal == 4:
            # Encerrar o programa
            break
        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.\n")

except oracledb.Error as e:
    print("Erro ao conectar ao banco de dados Oracle: \n", e)

finally:
    if 'connection' in locals():
        connection.close()

print("\nPrograma encerrado.")  # Exibir mensagem de encerramento do programa

