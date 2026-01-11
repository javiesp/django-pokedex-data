import os
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from django.core.cache import cache
from .dto.PokemonDTO import PokemonDTO
from .models import Pokemon  # <--- Importamos el modelo

logger = logging.getLogger('pokedex')

class PokeService:
    BASE_URL = os.getenv("POKEAPI_URL") or "https://pokeapi.co/api/v2/pokemon"

    def __init__(self):
        self.session = requests.Session()

    def _fetch_single_pokemon(self, url: str) -> Optional[PokemonDTO]:
        """Auxiliar para hilos."""
        try:
            response = self.session.get(url, timeout=3)
            if response.status_code == 200:
                return PokemonDTO.from_api(response.json())
        except Exception as e:
            logger.error(f"Error descargando {url}: {e}")
        return None

    def get_top_50_pokemon(self) -> List[PokemonDTO]:
        """Obtiene pokemon con persistencia en DB y caché de memoria."""
        cache_key = 'pokedex_top_50_v2'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # 1. Intentar obtener de la Base de Datos (Persistencia Real)
        db_pokemons = Pokemon.objects.all().order_by('id')[:50]
        
        if db_pokemons.count() >= 50:
            logger.info("📦 Sirviendo desde la Base de Datos")
            pokemon_list = [
                PokemonDTO(p.id, p.name, p.types, p.height, p.weight, p.name_reversed, p.image_url)
                for p in db_pokemons
            ]
            cache.set(cache_key, pokemon_list, 3600)
            return pokemon_list

        # 2. Si no están en DB, descargar de la API en paralelo
        try:
            response = self.session.get(f"{self.BASE_URL}?limit=50", timeout=5)
            response.raise_for_status()
            results = response.json().get('results', [])

            with ThreadPoolExecutor(max_workers=10) as executor:
                urls = [item['url'] for item in results]
                pokemon_results = list(executor.map(self._fetch_single_pokemon, urls))

            final_list = [p for p in pokemon_results if p is not None]

            # 3. Guardar en la Base de Datos para persistencia futura
            for p in final_list:
                Pokemon.objects.update_or_create(
                    id=p.id,
                    defaults={
                        'name': p.name,
                        'types': p.types,
                        'height': p.height,
                        'weight': p.weight,
                        'image_url': p.image_url,
                        'name_reversed': p.name_reversed
                    }
                )

            cache.set(cache_key, final_list, 3600)
            return final_list
        except Exception as e:
            logger.error(f"Error en get_top_50: {e}")
            return []

    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[PokemonDTO]:
        """Busca en DB primero, si no existe, descarga de API."""
        try:
            p = Pokemon.objects.get(id=pokemon_id)
            return PokemonDTO(p.id, p.name, p.types, p.height, p.weight, p.name_reversed, p.image_url)
        except Pokemon.DoesNotExist:
            # Lógica de respaldo API si no está en DB
            url = f"{self.BASE_URL}/{pokemon_id}/"
            return self._fetch_single_pokemon(url)

    @staticmethod
    def filter_by_weight(pokemon_list: List[PokemonDTO]) -> List[PokemonDTO]:
        return [p for p in pokemon_list if 30 < p.weight < 80]

    @staticmethod
    def filter_by_type(pokemon_list: List[PokemonDTO], target_type: str = "grass") -> List[PokemonDTO]:
        return [p for p in pokemon_list if target_type in p.types]

    @staticmethod
    def filter_combined(pokemon_list: List[PokemonDTO]) -> List[PokemonDTO]:
        return [p for p in pokemon_list if "flying" in p.types and p.height > 10]