# README - Sistema de Gerenciamento de Papelaria

## Descrição
Este é um sistema de gerenciamento de papelaria desenvolvido em Python, que permite calcular o preço de venda de produtos com base nos custos associados, cadastrar novos produtos, cadastrar custos adicionais, consultar produtos pelo nome e excluir produtos do banco de dados Oracle.

## Funcionalidades:

### 1. Calcular Preço de Venda
Esta função permite calcular o preço de venda de um produto com base nos custos de aquisição, custos administrativos, comissão de venda, impostos e lucro desejado.

### 2. Cadastrar Produto
Permite adicionar novos produtos ao banco de dados. Solicita informações como código do produto, nome, preço de venda, categoria, quantidade em estoque e descrição.

### 3. Cadastrar Custo
Possibilita registrar custos adicionais associados a um produto específico, como custo de aquisição, custos administrativos, comissão de venda, impostos e lucro.

### 4. Consultar Produto
Permite buscar produtos pelo nome e exibir suas informações, como código, nome, preço, categoria, quantidade em estoque e descrição.

### 5. Excluir Produto
Permite remover um produto do banco de dados com base no seu ID.

### 6. Sair
Encerra a execução do programa.

## Requisitos
- Python 3.4.1
- Biblioteca `oracledb` para interagir com o banco de dados Oracle
- Arquivo `conexao.py` contendo informações de conexão ao banco de dados

## Uso
1. Execute o programa Python `gerenciamento_papelaria.py`.
2. Escolha uma das opções do menu para acessar as funcionalidades disponíveis.
3. Siga as instruções na tela para realizar as operações desejadas.

## Autores
Ana Julia Matozo Rodrigues
Hugo Daniel Bosada Rodrigues
Letícia Lima da Silva
Murilo Euphrasio Brito