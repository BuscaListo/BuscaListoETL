from os import path
from typing import Any
from webscraping.models_enum import ConfigDaka
from webscraping.extractors.base_extractor import BaseExtractor


class DakaExtractor(BaseExtractor):
    """Extractor para la API de Daka"""
    
    def __init__(self):
        super().__init__(ConfigDaka.BASE_URL.value)
    
    def get_extractor_name(self) -> str:
        return "Daka"
    
    def extract_data(self) -> list[dict[str, Any]]:
        """Extrae datos de productos de Daka"""
        try:

            output_data = []

            for product_name in ConfigDaka.PRODUCTS_NAME.value:

                # Ejemplo de extracción - ajustar según API real
                response = self._make_request(
                    endpoint=path.join(product_name, '0', ConfigDaka.COUNT_PRODUCTS.value),
                )
                data = response.json()
                
                # Procesar y normalizar datos según necesidades
                processed_data = self._process_data(data)
                output_data.extend(processed_data)

            return output_data
            
        except Exception as e:
            print(f"Error extrayendo datos de {self.get_extractor_name()}: {e}")
            return []
    
    def _process_data(self, raw_data: dict) -> list[dict[str, Any]]:
        """Procesa y normaliza los datos extraídos"""

        all_products = raw_data.get('valor', [])
        if not all_products:
            return []

        for index, product in enumerate(all_products):
            all_products[index]['image'] = self._get_product_image(
                image_base_url=ConfigDaka.IMAGE_BASE_URL.value, image_id=product['sap']
            )

        return all_products
    
    def _get_product_image(self, image_base_url: str, image_id: str) -> None:
        """Obtener la imagen del producto"""
        return path.join(image_base_url, image_id + '.webp')


if __name__ == '__main__':
    extractor = DakaExtractor()
    data = extractor.extract_data()
    print(f"Extraídos {len(data)} registros de {extractor.get_extractor_name()}")