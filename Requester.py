from urllib.request import Request, urlopen
from urllib import error

from bs4 import BeautifulSoup
import mysql.connector as connector
from mysql.connector import errorcode

import Constants
from DatabaseManager import DatabaseManager
from classes.Pokemon import Pokemon
from classes.Ability import Ability
from classes.EggGroup import EggGroup
from classes.Audit import Audit


# The pokémon's japanese name is in the 8th position of a th list. So, in some cases there's no japanese name yet (Gen
# VII pokémon) and is set to be 'None'.
def __get_japanese_name(tr_list):
    return tr_list[-1].td.text if len(tr_list) > 7 else 'None'


# Each pokémon can have 1 or 2 types, so it's necessary to validate it.
def __get_pokemon_types(a_list):
    types = []
    for a in a_list:
        types.append(a.text)
    return types


# Each pokémon can have 1 or 2 abilities and 0 or 1 hidden abilities.
def __get_pokemon_abilities(a_list):
    abilities = []
    for a in a_list:
        abilities.append(a.text)
    return abilities


# Each pokémon can have gender or not.
def __get_pokemon_gender_ratio(span_list):
    gender = 'Genderless'
    if len(span_list) == 2:
        gender = span_list[0].text + ', ' + span_list[1].text
    return gender


# Each pokémon can have 1 or 2 egg groups, but I don't know why in some cases they don't have any.
def __get_pokemon_egg_groups(a_list):
    egg_groups = []
    for a in a_list:
        egg_groups.append(a.text)
    return egg_groups if len(egg_groups) > 0 else ['Undiscovered']


# Makes a request to each pokémon url and then parses they information.
def __get_pokemon(pokemon_url):
    request = Request(pokemon_url, headers={'User-Agent': 'Mozilla/52.0'})
    soup_object = BeautifulSoup(urlopen(request).read(), 'html.parser').body.article
    pokemon_info_div = soup_object.contents[11].contents[3].contents[1].contents[1]
    pokedex_data_tr_list = pokemon_info_div.contents[3].contents[3].find_all('tr')
    training_and_breeding_div_list = pokemon_info_div.contents[5].contents[1].find_all('div')
    training_div_tr_list = training_and_breeding_div_list[0].find_all('tr')
    breeding_div_tr_list = training_and_breeding_div_list[1].find_all('tr')

    pokemon_name = soup_object.contents[1].text
    pokemon_japanese_name = __get_japanese_name(pokedex_data_tr_list)
    pokemon_species = pokedex_data_tr_list[2].td.text
    pokemon_pokedex_number = pokedex_data_tr_list[0].strong.text
    pokemon_image_path = pokemon_info_div.contents[1].img['src']
    pokemon_types = __get_pokemon_types(pokedex_data_tr_list[1].td.find_all('a'))
    pokemon_abilities = __get_pokemon_abilities(pokedex_data_tr_list[5].td.find_all('a'))
    pokemon_gender_ratio = __get_pokemon_gender_ratio(breeding_div_tr_list[1].td.find_all('span'))
    pokemon_catch_rate = training_div_tr_list[1].td.text
    pokemon_egg_groups = __get_pokemon_egg_groups(breeding_div_tr_list[0].td.find_all('a'))
    # For some reason this string is accompanied by \t and \n.
    pokemon_hatch_time = breeding_div_tr_list[2].td.text.replace('\t', '').replace('\n', '')
    pokemon_height = pokedex_data_tr_list[3].td.text.replace('\u2032', '.').replace('\u2033', '..')
    pokemon_weight = pokedex_data_tr_list[4].td.text
    pokemon_base_happiness = training_div_tr_list[2].td.text
    pokemon_leveling_rate = training_div_tr_list[4].td.text
    return Pokemon(pokemon_name, pokemon_japanese_name, pokemon_species, pokemon_pokedex_number, pokemon_image_path,
                   pokemon_types, pokemon_abilities, pokemon_gender_ratio, pokemon_catch_rate, pokemon_egg_groups,
                   pokemon_hatch_time, pokemon_height, pokemon_weight, pokemon_base_happiness, pokemon_leveling_rate)


# This is the Web Crawler, it gets the url of each pokémon.
def __get_pokemon_span_list():
    request = Request(Constants.POKEMON_LIST_URL, headers={'User-Agent': 'Mozilla/52.0'})
    soup_object = BeautifulSoup(urlopen(request).read(), 'html.parser').body.article.contents[9]
    span_list = soup_object.find_all('span')
    return span_list


# Return a list with 25 pokemon depending of the page requested.
def get_pokemon_by_page(page):
    last_index = page * Constants.POKEMON_PER_PAGE
    first_index = last_index - 25
    pokemon_list = []

    span_list = __get_pokemon_span_list()
    span_list_length = len(span_list)
    span_list = span_list[first_index:last_index if span_list_length >= last_index else span_list_length]

    for pokemon_span in span_list:
        pokemon_list.append(__get_pokemon(Constants.POKEMON_DB_URL + pokemon_span.a['href']))
    return pokemon_list


def __scrap_pokemon():
    pokemon_list = []
    try:
        span_list = __get_pokemon_span_list()
    except error.HTTPError as err:
        print('Error scraping Pokemon URLs, error code: ', err.code)
        return [], Audit(Constants.POKEMON_DB_URL, 0, 1, 'Failed')
    else:
        cont = 0
        success_cont = 0
        error_cont = 0
        for pokemon_span in span_list:
            cont += 1
            try:
                pokemon_list.append(__get_pokemon(Constants.POKEMON_DB_URL + pokemon_span.a['href']))
            except error.HTTPError as err:
                print('Error scraping a Pokemon, error code: ', err.code)
                error_cont += 1
            else:
                success_cont += 1
                print('Pokemon ', cont)
        return pokemon_list, Audit(Constants.POKEMON_DB_URL, success_cont, error_cont,
                                   'Incomplete' if error_cont > 0 else 'Complete')


def __scrap_abilities():
    abilities_list = []
    try:
        request = Request(Constants.ABILITIES_URL, headers={'User-Agent': 'Mozilla/52.0'})
    except error.HTTPError as err:
        print('Error scraping abilities, error code: ', err.code)
        return [], Audit(Constants.BULBAPEDIA_URL, 0, 1, 'Failed')
    else:
        tr_list = BeautifulSoup(urlopen(request).read(), 'html.parser').find_all('table')[1].find_all('tr')[1:]
        cont = 0
        for tr in tr_list:
            td_list = tr.find_all('td')
            abilities_list.append(Ability(td_list[0].text.replace('\n', ''), td_list[1].text.replace('\n', ''),
                                          td_list[2].text.replace('\n', ''), td_list[3].text.replace('\n', '')))
            cont += 1
            print('Ability ', cont)
        return abilities_list, Audit(Constants.BULBAPEDIA_URL, cont, 0, 'Complete')


def __scrap_egg_groups():
    egg_groups_list = []
    try:
        request = Request(Constants.EGG_GROUPS_URL, headers={'User-Agent': 'Mozilla/52.0'})
    except error.HTTPError as err:
        print('Error scraping egg groups, error code: ', err.code)
        return [], Audit(Constants.BULBAPEDIA_URL, 0, 1, 'Failed')
    else:
        li_list = BeautifulSoup(urlopen(request).read(), 'html.parser').ol.find_all('li')
        cont = 0
        for li in li_list:
            li_split_text = li.text.split(': ')
            egg_groups_list.append(EggGroup(li_split_text[0], li_split_text[1]))
            cont += 1
            print('Egg group ', cont)
        return egg_groups_list, Audit(Constants.BULBAPEDIA_URL, cont, 0, 'Complete')


def __scrap_all():
    pokemon_tuple = __scrap_pokemon()
    abilities_tuple = __scrap_abilities()
    egg_groups_tuple = __scrap_egg_groups()
    return pokemon_tuple, abilities_tuple, egg_groups_tuple


def update_database_registers(username, password):
    tuple_lists = __scrap_all()
    pokemon_tuple = tuple_lists[0]
    abilities_tuple = tuple_lists[1]
    egg_groups_tuple = tuple_lists[2]
    audit_list = [pokemon_tuple[1], abilities_tuple[1], egg_groups_tuple[1]]
    try:
        cnx = connector.connect(user=username, password=password, host='us-cdbr-iron-east-03.cleardb.net',
                                database='heroku_2f9dc8c5082641a')
    except connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return {'Error': 'Something is wrong with your username or password'}, 401
        else:
            return {'Error': 'Something is wrong, please try again later'}, 400
    else:
        cursor = cnx.cursor()
        db_manager = DatabaseManager(cursor)
        db_manager.store_or_update_abilities_registers(abilities_tuple[0])
        db_manager.store_or_update_egg_groups_registers(egg_groups_tuple[0])
        db_manager.store_or_update_pokemon_registers(pokemon_tuple[0])
        db_manager.store_audit_registers(audit_list)

        cnx.commit()
        cursor.close()
        cnx.close()
        return audit_list, 200
