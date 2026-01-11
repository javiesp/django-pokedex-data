from django.test import TestCase
import requests_mock
from .services import PokeService, PokemonDTO

class PokemonMantenibilidadTest(TestCase):
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.service = PokeService()
        # Simular interce DTO
        self.mock_list = [
            PokemonDTO(1, "bulbasaur", ["grass"], 7, 69, "ruasablub"),
            PokemonDTO(6, "charizard", ["fire", "flying"], 17, 905, "drazirahc"),
            PokemonDTO(18, "pidgeot", ["normal", "flying"], 15, 395, "toegdip"),
        ]

    def test_transformacion_nombre_invertido(self):
        nombre = "pikachu"
        dto = PokemonDTO(id=25, name=nombre, types=[], height=4, weight=60, name_reversed=nombre[::-1])
        self.assertEqual(dto.name_reversed, "uhcakip")

    def test_filtro_peso(self):
        resultado = self.service.filter_by_weight(self.mock_list)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].name, "bulbasaur")

    def test_filtro_tipo_grass(self):
        resultado = self.service.filter_by_type(self.mock_list, "grass")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].name, "bulbasaur")

    def test_filtro_combinado(self):
        resultado = self.service.filter_combined(self.mock_list)
        self.assertEqual(len(resultado), 2)  # Charizard y Pidgeot cumplen
        for p in resultado:
            self.assertIn("flying", p.types)
            self.assertGreater(p.height, 10)

    def test_consumo_api_con_mock(self):
        """Asegura que el servicio maneja bien la estructura de la PokeAPI."""
        with requests_mock.Mocker() as m:
            m.get(f"{self.service.BASE_URL}?limit=50", json={
                "results": [{"name": "test-poke", "url": "https://pokeapi.co/api/v2/pokemon/99/"}]
            })
            m.get("https://pokeapi.co/api/v2/pokemon/99/", json={
                "id": 99, "name": "test-poke", "types": [{"type": {"name": "water"}}], 
                "height": 10, "weight": 100
            })
            
            pokes = self.service.get_top_50_pokemon()
            self.assertEqual(len(pokes), 1)
            self.assertEqual(pokes[0].name, "test-poke")