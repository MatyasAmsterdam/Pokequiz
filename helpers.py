import os
import requests
import urllib.parse
import math
import random

from flask import redirect, render_template, request, session
from functools import wraps

pokemon_dict = {}


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
            
    compatible_pokemon = get_compatible_pokemon(pokemon, types, type2, region, stage)
    
    return question, compatible_pokemon


def get_compatible_pokemon(properties, types = False, type2 = False, region = False, stage = False):
    compatible_pokemon = []
    for pokemon in pokemon_dict.values():
        
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

        compatible_pokemon.append(pokemon['name'])
    
    return compatible_pokemon
