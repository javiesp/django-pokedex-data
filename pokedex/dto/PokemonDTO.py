from dataclasses import dataclass

@dataclass
class PokemonDTO:
    id: int
    name: str
    types: list[str]
    height: int
    weight: int
    name_reversed: str
    image_url: str

    @classmethod
    def from_api(cls, data: dict):
        name = data.get('name', '')
        sprites = data.get('sprites', {})
        image_url = sprites.get('other', {}).get('official-artwork', {}).get('front_default') or \
                    sprites.get('front_default', '')

        return cls(
            id=data.get('id'),
            name=name,
            types=[t['type']['name'] for t in data.get('types', [])],
            height=data.get('height', 0),
            weight=data.get('weight', 0),
            name_reversed=name[::-1],
            image_url=image_url
        )