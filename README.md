# Getting Started

## Clonar repositorio
```
git clone https://github.com/javiesp/django-pokedex-data.git
```

## Inicializar proyecto con Docker

Para iniciarlizar el proyecto con docker ejecuta:

```cmd
docker compose build
docker compose up
```

Ejecutar pytest

```cmd
docker compose run web pytest
```

Constuir y ejecutar 
```
docker compose up --build 
```
---
## Inicializar proyecto para desarrollo

Activar tu terminar de python Python 3.13.7

```cmd
pip install -r requirements
```

### Migraciones

Ejecutar comandos

```
python manage.py makemigrations
```
y
```
python manage.py migrate
```
Luego para ejecutar el servidor local:

```cmd
python manage.py runserver 
```