class Pokemon:

    def __init__(self, name, japanese_name, species, pokedex_number, image_path, type, abilities, gender_ratio,
                 catch_rate, egg_groups, hatch_time, height, weight, base_happiness, leveling_rate):
        self.name = name
        self.japanese_name = japanese_name
        self.species = species
        self.pokedex_number = pokedex_number
        self.image_path = image_path
        self.type = type
        self.abilities = abilities
        self.gender_ratio = gender_ratio
        self.catch_rate = catch_rate
        self.egg_groups = egg_groups
        self.hatch_time = hatch_time
        self.height = height
        self.weight = weight
        self.base_happiness = base_happiness
        self.leveling_rate = leveling_rate
