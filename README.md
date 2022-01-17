# Poke-Team-Bot
Bot de Telegram deployado en Heroku para generar una imagen de un equipo Pokémon.

## Bot en Telegram
[https://t.me/poke_team_bot](https://t.me/poke_team_bot)

## Imagen de muestra
![Imagen de muestra](https://i.ibb.co/vZbY2Nv/photo1642461200.jpg)

## Comandos
- */name* <user-name>: Definir nombre de usuario para la imagen.  
- */add* <pokemon-name>: Agregar Pokémon al equipo. El máximo es de 6. `/add pikachu` `/add bulbasaur charmander squirtle`  
- */delete* <pokemon-name>: Quitar Pokémon del equipo. `/delete pikachu`  
- */reset*: Borrar equipo.  
- */color* <color-code>: Definir color de fondo para la imagen. `/color blue` `/color #FF5733`  
- */create*: Generar imagen.

Para elegir un Pokémon shiny, agregar un \* al final del nombre. `/add mew*`

## Clonar
`git clone https://github.com/leandro-i/poke-team-bot`

## Packages requeridos
- python-telegram-bot
- requests
- html2image
- psycopg2
- matplotlib

## Buildpacks de Heroku
- [heroku/python](https://github.com/heroku/heroku-buildpack-python)
- [heroku-community/apt](https://github.com/heroku/heroku-buildpack-apt)
- [heroku/google-chrome](https://github.com/aurelmegn/heroku-buildpack-google-chrome)

## Recursos
[PokéAPI](https://pokeapi.co/)