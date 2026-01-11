from django.shortcuts import render
from .services import PokeService

def index(request):
    service = PokeService()
    pokemon_data = service.get_top_50_pokemon()
    
    action = request.GET.get('action')
    if action == 'weight_filter':
        pokemon_data = service.filter_by_weight(pokemon_data)
    elif action == 'type_grass':
        pokemon_data = service.filter_by_type(pokemon_data, "grass")
    elif action == 'combined':
        pokemon_data = service.filter_combined(pokemon_data)

    context = {
        'pokemons': pokemon_data,
        'current_filter': action or 'Todos'
    }
    return render(request, 'pokedex/index.html', context)

def details(request, pokemon_id):
    service = PokeService()
    pokemon = service.get_pokemon_by_id(pokemon_id)
    
    if not pokemon:
        from django.http import Http404
        raise Http404("Pokémon no encontrado")

    return render(request, 'pokedex/details.html', {'pokemon': pokemon})