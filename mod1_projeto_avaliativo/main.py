import sys
sys.stdout.reconfigure(encoding='utf-8')

from pipeline import OlistPipeline

class MainPipeline:

  def exibir_amostra_produtos(self, produtos: list, n: int = 5) -> None:
      """

      """
      print("\n───── AMOSTRA: PRODUTOS SANITIZADOS ─────")
      print(f"{'#':<4} {'ID (8 chars)':<12} {'Categoria':<35} {'Peso(g)':<10} {'Comp(cm)':<10}")
      print("-" * 75)

      for i, prod in enumerate(produtos[:n]):
          # Exibe só os 8 primeiros caracteres do ID para não truncar a tabela
          id_curto = prod.get("product_id", "")[:8]
          categoria = prod.get("product_category_name", "")
          peso = prod.get("product_weight_g", "—")
          comprimento = prod.get("product_length_cm", "—")
          print(f"{i+1:<4} {id_curto:<12} {categoria:<35} {str(peso):<10} {str(comprimento):<10}")


  def exibir_amostra_pedidos(self, pedidos: list, n: int = 8) -> None:
      """

      """
      print("\n───── AMOSTRA: PEDIDOS SANITIZADOS ─────")
      print(f"{'#':<4} {'ID (8)':<10} {'Status':<12} {'Aprovação BR':<14} {'Entrega':<25} {'Hipótese':<18}")
      print("-" * 90)

      for i, ped in enumerate(pedidos[:n]):
          id_curto = ped.get("order_id", "")[:8]
          status = ped.get("order_status", "")
          aprov_br = ped.get("order_approved_at", "—")
          entrega = ped.get("order_delivered_customer_date", "—") or "—"
          hipotese = ped.get("delivery_hypothesis", "—")
          print(
              f"{i+1:<4} {id_curto:<10} {status:<12} {aprov_br:<14} {entrega:<25} {hipotese:<18}"
          )

def main():
  """
      Função principal — instancia o pipeline e orquestra toda a execução.

      Fluxo:
        1. Cria uma instância de OlistPipeline
        2. Processa produtos, pedidos e gera relatório
        3. Exibe amostras para validação visual
      """
  olist_pipeline = OlistPipeline()
  main_pipeline = MainPipeline()

  produtos_sanitizados = olist_pipeline.read_products(
    "sample_data/olist_products_dataset.csv"
  )

  pedidos_sanitizados = olist_pipeline.read_orders(
    "sample_data/olist_orders_dataset.csv"
  )

  olist_pipeline.report()

  if produtos_sanitizados:
      main_pipeline.exibir_amostra_produtos(produtos_sanitizados, n=5)
  if pedidos_sanitizados:
      main_pipeline.exibir_amostra_pedidos(pedidos_sanitizados, n=8)

  print(f"\n{chr(10148)} Pipeline finalizado com sucesso.\n")



 
if __name__ == "__main__":
  main()
 