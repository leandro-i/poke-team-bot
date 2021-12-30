from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests
from html2image import Html2Image
from matplotlib.colors import is_color_like
import sqlite3
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))
BOT_TOKEN = os.environ['BOT_TOKEN']

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def create_user_db(user_id, username, full_name):
    if not username:
        username = 'NULL'
    if not full_name:
        full_name = 'NULL'
        
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO poketeam (user_id, username, full_name) values (?, ?, ?);', (user_id, username, full_name))
            conn.commit()
        except:
            pass

def update_columns(user_id, nickname=False, team=False, color=False, image=False):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        if nickname:
            try:
                cursor.execute('UPDATE poketeam SET nickname = ? WHERE user_id = ?;', (nickname, user_id))
            except:
                pass
        if team:
            try:
                cursor.execute('UPDATE poketeam SET team = ? WHERE user_id = ?;', (team, user_id))
            except:
                pass
        if color:
            try:
                cursor.execute('UPDATE poketeam SET color = ? WHERE user_id = ?;', (color, user_id))
            except:
                pass
        if image:
            try:
                cursor.execute('UPDATE poketeam SET image = ? WHERE user_id = ?;', (image, user_id))
            except:
                pass
        conn.commit()
        
def get_value(user_id, nickname=False, team=False, color=False):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        if nickname:
            try:
                cursor.execute('SELECT nickname FROM poketeam WHERE user_id = ?;', (user_id,))
                value = cursor.fetchone()[0]
                return value
            except:
                pass
        if team:
            try:
                cursor.execute('SELECT team FROM poketeam WHERE user_id = ?;', (user_id,))
                value = cursor.fetchone()[0]
                return value
            except:
                pass
        if color:
            try:
                cursor.execute('SELECT color FROM poketeam WHERE user_id = ?;', (user_id,))
                value = cursor.fetchone()[0]
                return value
            except:
                pass

def generate_path():
    try:
        path_list = os.listdir('./img/')
    except FileNotFoundError:
        os.mkdir('./img/')
    img_list = []
    num_list = []
    
    for file in path_list:
        if 'poketeam' in file and file.endswith('.png'):
            img_list.append(file)
            num = int(''.join(filter(lambda x: x.isdigit(), file)))
            num_list.append(num)
            
    if not img_list:
        return ('./img/', 'poketeam_1.png')
    elif len(img_list) > 10:
        os.remove(f'./img/poketeam_{min(num_list)}.png')
    
    return ('./img/', f'poketeam_{max(num_list)+1}.png')


# Comandos

def start(update, context):
    user_id = update.effective_chat.id
    username = getattr(update.message.from_user, 'username', '')
    full_name = getattr(update.message.from_user, 'full_name', '')
    
    create_user_db(user_id, username, full_name)
    
    context.bot.send_message(
        chat_id=user_id,
        text="""
        Este bot genera una imagen de tu equipo Pokémon.  \n
        Comandos:  \n
        - */name* <user-name>: Definir nombre de usuario para la imagen.  \n
        - */add* <pokemon-name>: Agregar Pokémon al equipo. `/add pikachu` `/add bulbasaur charmander squirtle`  \n
        - */delete* <pokemon-name>: Quitar Pokémon del equipo. `/delete pikachu`  \n
        - */color* <color-code>: Definir color de fondo para la imagen. `/color blue` `/color #FF5733`  \n
        - */create*: Generar imagen.
        """,
        parse_mode='markdown'
    )
    
start_handler = CommandHandler('start', start)


def warning(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Utilice el comando /add para agregar Pokémon a su equipo. El máximo es 6.\n/delete para quitar Pokémon de su equipo.\n/name para agregarle tu nombre a la imagen'
    )
    
warning_handler = MessageHandler(Filters.text & (~Filters.command), warning)


def name(update, context):
    user_id = update.effective_chat.id
    nickname = ' '.join(context.args)[:21]
    
    update_columns(user_id=user_id, nickname=nickname)
    
    context.bot.send_message(
        chat_id=user_id,
        text=f'Se ha cargado tu nombre: {nickname}'
    )
    
name_handler = CommandHandler('name', name)


def set_color(update, context):
    user_id = update.effective_chat.id
    color = ' '.join(context.args)
    
    update_columns(user_id=user_id, color=color)
    
    if is_color_like(color):
        update_columns(user_id=user_id, color=color)
        text = f'Se ha cargado el color: {color}'
    else:
        text = f'El color "{color}" es inválido'
        
    context.bot.send_message(
        chat_id=user_id,
        text=text
    )
        
color_handler = CommandHandler('color', set_color)


def add(update, context):
    user_id = update.effective_chat.id
    new_pokemon = context.args
    team = get_value(user_id, team=True)
    
    if team:
        team_list = team.split()
    else:
        team_list = []
    
    for p in new_pokemon:
        if len(team_list) > 5:
            context.bot.send_message(
                chat_id=user_id,
                text='El máximo es de 6 Pokémon.'
            )
            break
        
        if p.endswith('*'):
            shiny = True
            p = p.replace('*', '')
        else:
            shiny = False
        
        r = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p}')
        p = r.json()['name'].capitalize()
        if r.status_code == 200:
            if shiny == False:
                team_list.append(p)
            else:
                team_list.append(p + '*')
                
        else:
            context.bot.send_message(
                chat_id=user_id,
                text=f'{p.capitalize()} no es un Pokémon válido.'
            )
    
    update_columns(user_id, team=' '.join(team_list))
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Tu equipo hasta ahora es: {", ".join(team_list)}'
    )
add_handler = CommandHandler('add', add)


def delete(update, context):
    user_id = update.effective_chat.id
    del_pokemon = ' '.join(context.args)
    team = get_value(user_id, team=True)
    
    if team:
        team_list = team.split()
    else:
        team_list = []
    
    if del_pokemon in team_list:
        team_list.remove(del_pokemon)
        update_columns(user_id, team=team_list)
    else:
        context.bot.send_message(
            chat_id=user_id,
            text=f'{del_pokemon.capitalize()} no se encuentra en tu equipo.'
        )
delete_handler = CommandHandler('delete', delete)


def reset_team(update, context):
    user_id = update.effective_chat.id
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE poketeam SET team = NULL WHERE user_id = ?;', (user_id,))
            conn.commit()
            context.bot.send_message(
                chat_id=user_id,
                text='Se ha reseteado tu equipo Pokémon.'
            )
        except:
            pass
reset_handler = CommandHandler('reset', reset_team)


def create(update, context):
    user_id = update.effective_chat.id    
    str_cards = ''
    nickname = get_value(user_id, nickname=True)
    team = get_value(user_id, team=True)
    color = get_value(user_id, color=True)
    
    if team:
        team_list = team.split()
    else:
        context.bot.send_message(
            chat_id=user_id,
            text='No has elegido tu equipo.'
        )
        return
    
    if team_list:
        for p in team_list:
            if p.endswith('*'):
                shiny = True
                p = p.replace('*', '')
            else:
                shiny = False
            
            r = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p.lower()}')
            pokemon = r.json()
            type_1 = pokemon['types'][0]['type']['name']
            
            if len(pokemon['types']) == 1:
                div_types = f'<div class="type {type_1}"><span>{type_1}</span></div>'
            else:
                type_2 = pokemon['types'][1]['type']['name']
                div_types = f'<div class="type {type_1}">{type_1}</div><div class="type {type_2}">{type_2}</div>'
                
            str_cards += f"""
            <div class="pokemon-card {type_1}">
                <h3 class="name {'big' if len(pokemon['name']) > 9 else ''}">{pokemon['name']}</h3>
                <img src="{pokemon['sprites']['front_default'] if shiny == False else pokemon['sprites']['front_shiny']}">
                <div class="cont">
                    <div class="typebar">
                        {div_types}
                    </div>
                </div>
            </div>
            """
        html = f"""
            <div class="card" {'style="background-color:'+color+'"' if color else ''}>
                <h2 class="user name">{nickname if nickname else ''}</h2>
                <div class="pokemon-cont">
                    {str_cards}
                </div>
            </div>
        """
        css = """@import url(https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap);@import url(https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;600&display=swap);*{margin:0;padding:0;box-sizing:border-box;font-family:'Roboto Mono',monospace}body{max-width:500px;max-height:500px;background-color:transparent}.card{position:relative;background-color:#c52525;display:flex;flex-direction:column;justify-content:space-around;align-items:center;width:500px;height:500px;outline:1px solid #000;border:3px solid #fff;overflow:hidden}.card::before{content:'';position:absolute;top:0;right:0;left:0;bottom:0;background:linear-gradient(180deg,rgba(0,0,0,0) 5px,rgba(255,255,255,.2) 5px,rgba(255,255,255,.2) 10px,rgba(0,0,0,0) 10px,rgba(0,0,0,0) 16px,rgba(255,255,255,.2) 16px,rgba(255,255,255,.2) 22px,rgba(0,0,0,0) 22px,rgba(0,0,0,0) 29px,rgba(255,255,255,.2) 29px,rgba(255,255,255,.2) 36px,rgba(0,0,0,0) 36px,rgba(0,0,0,0) 44px,rgba(255,255,255,.2) 44px,rgba(255,255,255,.2) 55px,rgba(0,0,0,0) 55px,rgba(0,0,0,0) 67px,rgba(255,255,255,.2) 67px,rgba(255,255,255,.2) 79px,rgba(0,0,0,0) 79px,rgba(0,0,0,0) 92px,rgba(255,255,255,.2) 92px,rgba(255,255,255,.2) 106px,rgba(0,0,0,0) 106px,rgba(0,0,0,0) 121px,rgba(255,255,255,.2) 121px,rgba(255,255,255,.2) 136px,rgba(0,0,0,0) 136px,rgba(0,0,0,0) 152px,rgba(255,255,255,.2) 152px,rgba(255,255,255,.2) 169px,rgba(0,0,0,0) 169px,rgba(0,0,0,0) 188px,rgba(255,255,255,.2) 188px,rgba(255,255,255,.2) 210px,rgba(0,0,0,0) 210px,rgba(0,0,0,0) 232px,rgba(255,255,255,.2) 232px,rgba(255,255,255,.2) 258px,rgba(0,0,0,0) 258px,rgba(0,0,0,0) 282px,rgba(255,255,255,.2) 282px,rgba(255,255,255,.1) 310px,rgba(0,0,0,0) 310px,rgba(0,0,0,0) 340px,rgba(255,255,255,.1) 340px,rgba(255,255,255,.1) 380px,rgba(0,0,0,0) 380px,rgba(0,0,0,0) 420px,rgba(255,255,255,.1) 420px,rgba(0,0,0,0) 100%,rgba(0,0,0,0) 100%)}.pokemon-cont{width:90%;height:100%;display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap}.pokemon-card{position:relative;z-index:999;display:flex;align-items:center;flex-direction:column;width:120px;height:180px;border:2px solid #fff;outline:1px solid #000;box-shadow:1px 1px 5px 0 #000;border-radius:10px;overflow:hidden}.pokemon-card::before{content:'';z-index:9999;position:absolute;top:0;right:0;left:0;bottom:0;background:linear-gradient(180deg,rgba(255,255,255,.2) 0,rgba(0,0,0,0) 20%)}.pokemon-card::after{content:'';z-index:9999;position:absolute;top:0;right:0;left:0;bottom:0;background:linear-gradient(0deg,rgba(0,0,0,.3) 0,rgba(255,255,255,0) 10%)}.name{color:#fff;width:100%;font-weight:400;text-shadow:-1px 0 #000,0 1px #000,1px 0 #000,0 -1px #000;margin:5px 0;text-align:center;font-size:20px;text-transform:capitalize}.big{font-size:18px}.user{position:relative;display:flex;justify-content:center;align-items:center;height:60px;margin:0;font-size:25px;text-shadow:-2px 0 #000,0 2px #000,2px 0 #000,0 -2px #000;border-bottom:3px solid #fff;box-shadow:0 2px 0 0 #000}img{border-radius:50%;background-image:url(https://i.ibb.co/7KqFXvV/pokeballbw2.png);background-size:contain;background-repeat:no-repeat;width:96px;height:96px}.cont{display:flex;width:100%;height:100%;align-items:center;justify-content:center}.typebar{display:flex;justify-content:center;align-items:center;margin:10px 0;width:110px;height:20px;border-radius:10px;overflow:hidden;outline:1px solid #000;border:1px solid #fff;position:relative}.typebar::after{content:'';position:absolute;z-index:999;top:0;right:0;left:0;bottom:0;background:linear-gradient(0deg,rgba(0,0,0,.1) 50%,rgba(0,0,0,0) 50%)}.type{display:flex;justify-content:center;align-items:center;width:100%;height:100%;font-size:11px;color:#fff;text-transform:uppercase;text-shadow:-1px 0 #000,0 1px #000,1px 0 #000,0 -1px #000}.type span{z-index:9999}.normal{background-color:#b6b6b6}.fighting{background-color:#f86825}.flying{background-color:#4c64cc}.poison{background-color:#7d18b8}.ground{background-color:#83461e}.rock{background-color:#493426}.bug{background-color:#b5c718}.ghost{background-color:#452e61}.steel{background-color:#758da1}.fire{background-color:#f0361d}.water{background-color:#419fec}.grass{background-color:#5aac42}.electric{background-color:#ffd000}.psychic{background-color:#ce4796}.ice{background-color:#a0c2dd}.dragon{background-color:#12728a}.dark{background-color:#2b2b2b}.fairy{background-color:#ff9bfc}"""
        img_path = generate_path()
        
        hti = Html2Image(output_path=img_path[0])
        hti.screenshot(html_str=html, css_str=css, size=(500, 500), save_as=img_path[1])
        
        context.bot.send_photo(
            chat_id=user_id,
            photo=open(''.join(img_path), 'rb')
        )
        update_columns(user_id, image=True)
        
create_handler = CommandHandler('create', create)

    

if __name__ == '__main__':
    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(warning_handler)
    dispatcher.add_handler(name_handler)
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(delete_handler)
    dispatcher.add_handler(reset_handler)
    dispatcher.add_handler(create_handler)
    dispatcher.add_handler(color_handler)
    
    updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                            url_path=BOT_TOKEN,
                            webhook_url='https://poke-team-bot.herokuapp.com/' + BOT_TOKEN)
    # updater.bot.setWebhook('https://poke-team-bot.herokuapp.com/' + BOT_TOKEN)
    updater.idle()