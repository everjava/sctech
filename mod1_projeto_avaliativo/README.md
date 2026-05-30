# Pipeline de Sanitização de Dados - Olist

## Descrição do Projeto

Este projeto foi desenvolvido para solucionar um problema real da equipe de Engenharia de Dados da Olist, onde inconsistências nos dados estavam travando relatórios automatizados. O script implementa um pipeline completo de sanitização de dados utilizando apenas bibliotecas nativas do Python (`csv`, `re`, `datetime`), demonstrando domínio de programação estruturada sem depender de bibliotecas como Pandas. As bibliotecas auxiliares (`logging`, `traceback`) foram utilizadas para log.

### Problemas Identificados e Soluções:

1. **Dados Ausentes em Produtos**: Valores nulos na categoria do produto são preenchidos com "sem categoria". Para dimensões físicas (peso, altura, etc.), utilizamos a **média da coluna** como preenchimento - escolha técnica justificada pela preservação da distribuição estatística e manutenção da amostra completa.

2. **Padronização de Strings**: Aplicação de `.lower()`, `.strip()` e Expressões Regulares para remover caracteres especiais, garantindo consistência nas categorias.

3. **Validação de Regra de Negócio**: Verificação da hipótese de que pedidos com data de entrega vazia são obrigatoriamente cancelados, confirmando a lógica de negócio da Olist.

4. **Formatação Temporal**: Conversão de datas do formato ISO para o padrão brasileiro (DD/MM/AAAA).

## Guia de Execução

### Pré-requisitos

- Python 3.6 ou superior instalado
- Arquivos CSV nos diretórios:
  - `sample_data/olist_products_dataset.csv`
  - `sample_data/olist_orders_dataset.csv`

### Passo a Passo

1. **Clone ou baixe o repositório** contendo o arquivo `main.py`

2. **Certifique-se de que os arquivos CSV estão diretório sample_data** no raiz do script

3. **Execute o script**:
   ```bash
   python main.py



# Reflexão    

A qualidade dos dados é fundamental para o sucesso de qualquer modelo de Machine Learning.Dados inconsistentes ou valores extremos mal tratados podem fazer o modelo decorar padrões equivocados em vez de aprender relacionamentos verdadeiros. Por exemplo, se mantivermos categorias de produtos com caracteres especiais inconsistentes (ex: "Eletrônicos", "eletrônicos!", "ELETRÔNICOS"), o modelo pode criar features separadas para cada variação, levando ao overfitting e baixa generalização. 

Descartar registros com valores nulos (como fizemos com a média em vez de exclusão) pode introduzir viés. Se removermos produtos sem dimensões físicas, mas esses produtos são justamente os mais vendidos, o modelo aprenderá um padrão distorcido da realidade. A abordagem de preenchimento pela média, embora simplificada, preserva a representatividade da amostra. Dados temporais mal formatados podem fazer o modelo perder relações causais importantes.

Em resumo, um pipeline robusto de sanitização não apenas corrige problemas imediatos, mas constrói uma base sólida que permite modelos de IA aprenderem padrões verdadeiros do negócio, reduzindo overfitting e minimizando vieses prejudiciais às decisões automatizadas.