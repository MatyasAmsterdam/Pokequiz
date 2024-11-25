import os
import requests
import urllib.parse
import math
import random
import csv

from flask import redirect, render_template, request, session
from functools import wraps

pokemon_dict = {}
with open('resources/pokemon_properties.csv', mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader):
        pokemon_dict[idx] = {
            'number': int(row['number']),
            'name': row['name'],
            'type1': row['type1'],
            'type2': row['type2'],
            'region': row['region'],
            'stage': int(row['stage'])
        }


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_question(guessed_list, types = False, region = False, stage = False):
    index = random.randint(0, 1024)
    type2 = False
    
    # Ignore Pokémon that have already been geussed
    while index in guessed_list:
        index = random.randint(0, 1024)

    pokemon = pokemon_dict[index]
    question = "Enter a "
    
    if stage:
        question += f"stage {pokemon['stage']} "
    
    if types:
        question += f"{pokemon['type1']}"

        if pokemon['type2']:
            type2 = True
            question += f"/{pokemon['type2']}"
            
        question += " type "
    
    question += "Pokémon "

    if region:
        if pokemon['region'] == 'Unknown':
            question += f"of unknown origins, region-wise"
        else:
            question += f"from the {pokemon['region']} region"
            
    compatible_pokemon = get_compatible_pokemon(pokemon, guessed_list, types, type2, region, stage)
    
    return question, compatible_pokemon


def get_compatible_pokemon(properties, guessed_list = [], types = False, type2 = False, region = False, stage = False):
    compatible_pokemon = []
    for pokemon in pokemon_dict.values():

        # Progress check
        if pokemon['number'] + 1 in guessed_list:
            continue
        
        # Stage check
        if stage and pokemon['stage'] != properties['stage']:
            continue
            
        # Type checks
        if types and not type2:
            if pokemon['type1'] != properties['type1']:
                if pokemon['type2'] != properties['type1']:
                    continue
        if types and type2:
            if pokemon['type1'] != properties['type1']:
                if pokemon['type1'] != properties['type2']:
                    continue
            if pokemon['type2'] != properties['type2']:
                if pokemon['type2'] != properties['type1']:
                    continue   

         # Region check
        if region and pokemon['region'] != properties['region']:
            continue

        compatible_pokemon.append(pokemon['number'])
    
    return compatible_pokemon


def calculate_points(x):
    base_reward = 200
    scaling_factor = 50
    
    reward = base_reward + (scaling_factor // x) * scaling_factor
    
    if reward > 2000:
        return 2000    
    return round(reward / 50) * 50
