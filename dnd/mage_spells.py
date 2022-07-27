import os
import random
import re
from pathlib import Path
from dnd_globals import dnd_dir


# todo
# it's correct to put all the spells together into one folder, and have "what class gets this, as what level of spell" as metadata PER SPELL
# rather than dividing the spells up into "mage" "cleric" etc folders as I used to do
# otherwise i have to duplicate spells between folders and that's BAD; that's letting a file system detail complicate my data representation

# THEREFORE, with all spells in one folder, i'll need to be able to read the metadata from those spell files and PLUCK OUT the mage ones
# but god knows i dont want to be doing any more yaml parsing bullshit, or markdown text nonsense ... yet that's my only current way to do "metadata" in a text file
# again, the problem rears its head, of having a "text" file instead of a code (actually, DATA) file
# which is hwy I need a language where those two are the same

# todo SOLUTION is to write, not markdown files, but python files, for each spell - containing their text description AND other metadata...


# todo
# randomization in this file should be seeded from variable so easier to write unit tests
# probably sufficien to pass a seed value to get_pickable_spells with default value = random.randint()


def camel_case_to_spaced(name):
    x = re.sub(r"(.)([A-Z][a-z]+)", r"\1 \2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", x)


# switch to spell directory
first_level_spell_directory = dnd_dir / Path(
    "dnd/rules/todo/spells/MageSpellDescriptions/Level1/"
)

# retrieve and format spell names
first_level_spells = [
    f for f in os.listdir(first_level_spell_directory) if ".txt" in f and "un~" not in f
]
first_level_spells = [camel_case_to_spaced(s[:-4]) for s in first_level_spells]

minimum_first_level_spells = 6

# todo refactor the repetition
# move while len(pickable_spells) ...
def get_pickable_spells(intelligence):
    pickable_spells = []
    # todo bias: goes thru spells in wahtever order they are put into first_level_spells var
    # all else being equal, spells near end of that order less likely to get chosen
    # to fix: for s in randomize(first_level_spells):
    for s in first_level_spells:
        # an Intelligence check
        x = random.randint(1, 20)
        if x <= intelligence:
            pickable_spells.append(s)
            first_level_spells.remove(s)
        else:
            pass
    # keep going if there's too few:
    while len(pickable_spells) < minimum_first_level_spells:
        s = random.choice(first_level_spells)
        x = random.randint(1, 20)
        if x <= intelligence:
            pickable_spells.append(s)
            first_level_spells.remove(s)
    return pickable_spells
