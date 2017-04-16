from datetime import datetime


class DatabaseManager:

    def __init__(self, cursor):
        self.cursor = cursor

    def __create_audit_group(self):
        query = 'INSERT INTO AuditGroup(date) VALUES(%s);'
        data = (datetime.now().date(),)
        self.cursor.execute(query, data)
        return self.cursor.lastrowid

    def store_audit_registers(self, audit_list):
        id_group = self.__create_audit_group()
        for audit in audit_list:
            query = ('INSERT INTO Audit(idAuditGroup, webPage, registersNumber, errors, status)'
                     'VALUES(%s, %s, %s, %s, %s);')
            data = (id_group, audit.web_page, audit.registers_number, audit.errors, audit.status)
            self.cursor.execute(query, data)

    def store_or_update_abilities_registers(self, abilities_list):
        for ability in abilities_list:
            query = 'CALL createOrUpdateAbility(%s, %s, %s, %s)'
            data = (ability.id, ability.name, ability.description, ability.gen)
            self.cursor.execute(query, data)

    def store_or_update_egg_groups_registers(self, egg_groups_list):
        for egg_group in egg_groups_list:
            query = 'CALL createOrUpdateEggGroup(%s, %s)'
            data = (egg_group.name, egg_group.description)
            self.cursor.execute(query, data)

    def store_or_update_pokemon_registers(self, pokemon_list):
        for pokemon in pokemon_list:
            query = 'CALL createOrUpdatePokemonRegister(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            data = (pokemon.pokedex_number, pokemon.name, pokemon.japanese_name, pokemon.species, pokemon.image_path,
                    pokemon.gender_ratio, pokemon.catch_rate, pokemon.hatch_time, pokemon.height, pokemon.weight,
                    pokemon.base_happiness, pokemon.leveling_rate)
            self.cursor.execute(query, data)
            self.__update_tables_connections(pokemon)

    def __update_tables_connections(self, pokemon):
        self.__update_types_connections(pokemon.pokedex_number, pokemon.type)
        self.__update_abilities_connections(pokemon.pokedex_number, pokemon.abilities)
        self.__update_egg_groups_connections(pokemon.pokedex_number, pokemon.egg_groups)

    def __update_types_connections(self, pokedex_number, types):
        query = 'DELETE FROM PokemonTypes WHERE pokemonPokedexNumber = %s'
        data = (pokedex_number,)
        self.cursor.execute(query, data)
        for type in types:
            query = 'CALL insertPokemonType(%s, %s)'
            data = (pokedex_number, type)
            self.cursor.execute(query, data)

    def __update_abilities_connections(self, pokedex_number, abilities):
        query = 'DELETE FROM PokemonAbilities WHERE pokemonPokedexNumber = %s'
        data = (pokedex_number,)
        self.cursor.execute(query, data)
        for ability in abilities:
            query = 'CALL insertPokemonAbility(%s, %s)'
            data = (pokedex_number, ability)
            self.cursor.execute(query, data)

    def __update_egg_groups_connections(self, pokedex_number, egg_groups):
        query = 'DELETE FROM PokemonEggGroups WHERE pokemonPokedexNumber = %s'
        data = (pokedex_number,)
        self.cursor.execute(query, data)
        for egg_group in egg_groups:
            query = 'CALL insertPokemonEggGroup(%s, %s)'
            data = (pokedex_number, egg_group)
            self.cursor.execute(query, data)
