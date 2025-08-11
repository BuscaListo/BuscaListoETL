import urllib3
import requests
from os import path
from abc import ABC, abstractmethod
from typing import Any


# Suprimir warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseExtractor(ABC):
    """Clase base abstracta para todos los extractores de APIs"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    @abstractmethod
    def extract_data(self) -> list[dict[str, Any]]:
        """Método abstracto para extraer datos de la API"""
        pass
    
    @abstractmethod
    def get_extractor_name(self) -> str:
        """Retorna el nombre del extractor"""
        pass
    
    def _make_request(
            self, 
            endpoint: str, 
            params: dict = None, 
            headers: dict = None
        ) -> requests.Response:

        """Método helper para hacer peticiones HTTP"""
        url = path.join(self.base_url, endpoint)
        response = self.session.get(
            url, 
            params=params,
             headers=headers, 
             verify=False
        )
        response.raise_for_status()
        return response