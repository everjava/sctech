import csv
import re
from datetime import datetime
import logging
import traceback


class OlistPipeline:
    logging.basicConfig(
        level=logging.ERROR,
        format='Erro no arquivo: %(filename)s na linha: %(lineno)d | Mensagem: %(message)s'
    )

    def __init__(self):
        self.SEM_CATEGORIA = 'sem categoria'
        self.CLEAN_PATTERN = re.compile(r"[^\w\s]", re.UNICODE)
        self.products: list = []
        self.orders: list = []
        # Dicionário de estatísticas usado no relatório final (Tarefa 5)
        self._stats: dict = {
            "total_produtos_lidos": 0,
            "total_pedidos_lidos": 0,
            "categorias_preenchidas": 0,
            "dimensoes_corrigidas": 0,
            "datas_entrega_nulas": 0,
            "cancelados_sem_entrega": 0,
            "nao_cancelados_sem_entrega": 0,
            "nao_cancelados_unavailable": 0,
            "datas_aprovacao_convertidas": 0,
            "datas_aprovacao_nulas": 0,
            "nao_cancelados_sem_entrega_created": 0,
            "nao_cancelados_sem_entrega_delivered": 0,
        }

    def read_csv(self, path: str) -> list:
      """
        Lê um arquivo CSV e retorna uma lista de dicionários.

        Parâmetros:
            caminho_arquivo (str): Caminho relativo ou absoluto do arquivo CSV.
 
        Retorno:
            list[dict]: Lista de registros; cada registro é um dicionário.
        """
      try:
          result = []
          with open(path, mode='r', encoding='utf-8') as arquivo:
              leitor_csv = csv.DictReader(arquivo)
              return list(leitor_csv)
      except FileNotFoundError:
          logging.error(f"Erro: O arquivo '{path}' não foi encontrado.")
      except Exception as e:
          logging.error(f"Ocorreu um erro ao ler o arquivo: {e}")
          traceback.print_exc()

    def clean_product_category_name(self, name: str) -> str:
      """
        Padroniza o nome de uma categoria de produto (Tarefa 2).
 
        Passos aplicados em ordem:
          1. .strip()  → remove espaços em branco nas extremidades
          2. .lower()  → converte para letras minúsculas
          3. re.sub()  → remove caracteres que NÃO sejam letras (a-z),
                         dígitos (0-9), espaço ou hífen
        Parâmetros:
            nome (str): Nome da categoria bruto.
 
        Retorno:
            str: Nome sanitizado.
      """
      try:
        name = name.strip().lower()
        return self.CLEAN_PATTERN.sub('', name)
      except Exception as e:
        logging.error(f"Ocorreu um erro ao sanitizar category name: {e}")
        traceback.print_exc()
        return None

    def convert_data_br(self, data: str) -> str:
      """
        Converte uma string de data/hora ISO para o formato brasileiro (Tarefa 4).
 
        O módulo `datetime` é usado para fazer o parse da string original
        (ex: "2017-05-16 15:05:35") e depois formatar no padrão DD/MM/AAAA.
 
        Parâmetros:
            data_str (str): Data no formato "YYYY-MM-DD HH:MM:SS".
 
        Retorno:
            str: Data no formato "DD/MM/YYYY" 
      """
      try:
        data_str = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        return data_str.strftime("%d/%m/%Y")
      except Exception as e:
        logging.error(f"Ocorreu um erro ao converter a data para padrão BR: {e}")
        traceback.print_exc()
        return None

    def calculate_products_average(self, linha):
      """
           Retorna a média acumulada para cada dimensão física.

           Caso nenhum valor tenha sido lido ainda (divisão por zero), retorna 0.0
           como valor neutro de fallback.

           Parâmetros:
               coluna (str): Nome da coluna.

           Retorno:
               float: Média atual, ou 0.0 se não houver dados.
      """
      try:
        total_weight = 0.0
        total_length = 0.0
        total_height = 0.0
        total_width = 0.0

        # Contadores individuais para médias precisas (caso falte algum dado no CSV)
        count_w = count_l = count_h = count_wd = 0

        # for linha in leitor_csv:
        # 1. Processa Peso
        if linha.get('product_weight_g'):
            try:
                total_weight += float(linha['product_weight_g'])
                count_w += 1
            except ValueError:
                pass  # Ignora se não for um número válido

            # 2. Processa Comprimento
            if linha.get('product_length_cm'):
                try:
                    total_length += float(linha['product_length_cm'])
                    count_l += 1
                except ValueError:
                    pass
            # 3. Processa Altura
            if linha.get('product_height_cm'):
                try:
                    total_height += float(linha['product_height_cm'])
                    count_h += 1
                except ValueError:
                    pass
            # 4. Processa Largura
            if linha.get('product_width_cm'):
                try:
                    total_width += float(linha['product_width_cm'])
                    count_wd += 1
                except ValueError:
                    pass

        # Calcula as médias (usa ternário para evitar ZeroDivisionError se o CSV estiver vazio)
        media_weight = total_weight / count_w if count_w > 0 else 0
        media_length = total_length / count_l if count_l > 0 else 0
        media_height = total_height / count_h if count_h > 0 else 0
        media_width = total_width / count_wd if count_wd > 0 else 0

        return media_weight, media_length, media_height, media_width
      except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")
        traceback.print_exc()
        return None, None, None, None

    def determine_category_name(self, produto):
        """
          Preenchimento de categoria nula com "sem categoria" (Tarefa 1)
          Limpeza/padronização de categoria via clean_product_category_name() (Tarefa 2)

          Parâmetros:
              produto da lista de produtos.
          """
        if not produto['product_category_name']:
            # TAREFA 1-A: Tratamento categoria ausente
            produto['product_category_name'] = self.SEM_CATEGORIA
            self._stats["categorias_preenchidas"] += 1
        else:
            # TAREFA 2: Padronização de Strings e Regex
            produto['product_category_name'] = self.clean_product_category_name(produto['product_category_name'])


    # TAREFA 1-B: Avaliar dimensões físicas
    def determine_dimensions(self, produto):
      """
          Preenchimento das dimenções vazias com a media

          Parâmetros:
              produto da lista de produtos.
          """
      avg_weight_g, avg_length_cm, avg_height_cm, avg_width_cm = self.calculate_products_average(produto)
      strategies = {
        'product_weight_g': avg_weight_g,
        'product_length_cm': avg_length_cm,
        'product_height_cm': avg_height_cm,
        'product_width_cm': avg_width_cm
      }
      for field_dimension, avg_dimension in strategies.items():
        if not produto.get(field_dimension):
          produto[field_dimension] = avg_dimension
          self._stats["dimensoes_corrigidas"] += 1


    def read_products(self, caminho_csv: str) -> list:
      """
        Lê, sanitiza e armazena os registros do dataset de produtos.

        Parâmetros:
            caminho_csv (str): Caminho para olist_products_dataset.csv.

        Retorno:
            list[dict]: Lista de produtos sanitizados (exclui descartados).
      """


      try:
        self.products = self.read_csv(caminho_csv)
        self._stats["total_produtos_lidos"] = len(self.products)
        for produto in self.products:
          self.determine_category_name(produto)
          self.determine_dimensions(produto)
        return self.products
      except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")
        traceback.print_exc()
        return None


    def format_order_approved_at(self, order):
      """
        Verifica se a data existe e aplica convert_data_br() para formatar a data no padrao BR

        Parâmetros:
            order(pedido) da lista de orders(pedidos)
      """
      order_approved_at = order.get("order_approved_at").strip()
      if not order["order_approved_at"]:
        order["order_approved_at"] = "N/A"
        self._stats["datas_aprovacao_nulas"] += 1
      else:
        order["order_approved_at"] = self.convert_data_br(order_approved_at)
        self._stats["datas_aprovacao_convertidas"] += 1

    # TAREFA 3: Hipótese — datas de entrega nulas / pedidos cancelados?
    def determine_delivery_hypothesis(self, order):
      """
        Determina se a hipótese é valida e faz contagem

        Parâmetros:
            order(pedido) da lista de orders(pedidos)
      """


      order_delivered_customer_date = order.get("order_delivered_customer_date", "").strip()
      status = order.get("order_status", "").strip().lower()
      if not order_delivered_customer_date:
        order["order_delivered_customer_date"] = "N/A"
        self._stats["datas_entrega_nulas"] += 1
        if status == "canceled":
          # Hipótese CONFIRMADA para este registro, sem data de entrega porque o pedido foi cancelado
          self._stats["cancelados_sem_entrega"] += 1
          order["delivery_hypothesis"] = "confirmed"
        elif status in ("shipped", "processing", "invoiced", "approved"):
          # Pedido ainda em andamento — entrega futura esperada
          order["delivery_hypothesis"] = "in_transit"
          self._stats["nao_cancelados_sem_entrega"] += 1
        elif status == "unavailable":
          # Pedido indisponível — entrega incerta
          order["delivery_hypothesis"] = "unavailable"
          self._stats["nao_cancelados_unavailable"] += 1
        elif status == "delivered":
          order["delivery_hypothesis"] = "delivered"
          self._stats["nao_cancelados_sem_entrega_delivered"] += 1
        else:
          order["delivery_hypothesis"] = "created"
          self._stats["nao_cancelados_sem_entrega_created"] += 1
      else:
        order["delivery_hypothesis"] = "delivered"
        order["order_delivered_customer_date"] = self.convert_data_br(order_delivered_customer_date)


    def read_orders(self, caminho_csv: str) -> list:
      """
        Lê os registros do dataset de pedidos e aplica as hipóteses e formatação da
        data de aprovação

        Parâmetros:
            caminho_csv (str): Caminho para olist_products_dataset.csv.

        Retorno:
            list[dict]: Lista de pedidos com data e hipotese atualizados
      """
      try:
        self.orders = self.read_csv(caminho_csv)
        self._stats["total_pedidos_lidos"] = len(self.orders)
        for order in self.orders:
          self.determine_delivery_hypothesis(order)
          self.format_order_approved_at(order)
        return self.orders
      except Exception as e:
        logging.error(f"Ocorreu um erro ao processar leitura do arquivo orders: {e}")
        traceback.print_exc()
        return None


    # =======================================================================
    # TAREFA 5: RELATÓRIO DE STATUS
    # =======================================================================
    def report(self) -> None:
      """
        Exibe na tela um sumário estatístico do processamento (Tarefa 5).
          Todas as métricas são calculadas a partir do dicionário _stats,
        preenchido incrementalmente durante o processamento dos datasets.
      """
      # Cálculos derivados para o relatório
      total_produtos_validos = len(self.products)
      total_nulos_corrigidos = (
        self._stats["categorias_preenchidas"]
        + self._stats["dimensoes_corrigidas"]
      )
      # Verifica se a hipótese de negócio foi totalmente confirmada
      nao_cancelados_sem_entrega_total = (
        self._stats['nao_cancelados_sem_entrega']
        + self._stats['nao_cancelados_unavailable']
        + self._stats['nao_cancelados_sem_entrega_delivered']
        + self._stats['nao_cancelados_sem_entrega_created'])

      hipotese_status = (
        "CONFIRMADA"
        if self._stats["nao_cancelados_sem_entrega"] == 0
        else f" PARCIAL — {nao_cancelados_sem_entrega_total} registro(s) "
                 f"sem entrega NÃO são cancelados e {self._stats['cancelados_sem_entrega']} são cancelados"
        )

      separador = "=" * 60
      print(separador)
      print("       RELATÓRIO DE SANITIZAÇÃO — OLIST PIPELINE")
      print(separador)
      print("\n PRODUTOS")
      print(f"  Total de produtos lidos                             : {self._stats['total_produtos_lidos']}")
      # print(f"  Registros descartados                               : {self._stats['registros_descartados']}")
      print(f"  Registros válidos                                   : {total_produtos_validos}")
      print(f"  Categorias preenchidas                              : {self._stats['categorias_preenchidas']}")
      print(f"  Dimensões corrigidas (média)                        : {self._stats['dimensoes_corrigidas']}")
 
      print("\n PEDIDOS")
      print(f"  Total de pedidos lidos                              : {self._stats['total_pedidos_lidos']}")
      print(f"  Datas de entrega ausentes                           : {self._stats['datas_entrega_nulas']}")
      print(f"  Pedidos cancelados s/ data entrega                  : {self._stats['cancelados_sem_entrega']}")
      print(f"  Pedidos não cancelados s/ data entrega (shipped, processing, invoiced, approved) : {self._stats['nao_cancelados_sem_entrega']}")
      print(f"  Pedidos não cancelados s/ data entrega (delivered)  : {self._stats['nao_cancelados_sem_entrega_delivered']}")
      print(f"  Pedidos não cancelados s/ data entrega (created)    : {self._stats['nao_cancelados_sem_entrega_created']}")
      print(f"  Pedidos não cancelados s/ data entrega (unavailable): {self._stats['nao_cancelados_unavailable']}")
       
      print(f"  Datas aprovação convertidas                         : {self._stats['datas_aprovacao_convertidas']}")
      print(f"  Datas aprovação nulas                               : {self._stats['datas_aprovacao_nulas']}")
      
      print("\n HIPÓTESE DE NEGÓCIO")
      print(f"  Datas de entrega nulas = cancelados?' -> {hipotese_status}")
 
      print("\n RESUMO GERAL")
      print(f"  Total de linhas processadas : {self._stats['total_produtos_lidos'] + self._stats['total_pedidos_lidos']}") 
      print(f"  Total de nulos corrigidos   : {total_nulos_corrigidos}")
      print(f"  Total de cancelados         : {self._stats['cancelados_sem_entrega']}")
      # print(f"  Base sanitizada?            : {'SIM' if self._stats['registros_descartados'] == 0 else '  Registros descartados presentes'}")
 
      print(separador)
