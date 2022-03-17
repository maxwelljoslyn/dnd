# TODO I KNOW THAT, LIKE RACES AND CLASSES, THIS WILL BECOME A DEEPLY NESTED DATA STRUCTURE

# todo should information about each weapon live on the weapon list in data, and be referenced by the recipe system, or vicev? DECISION: canonicalweapon data lives in this list (wherever it ends up); INCLUDING length, which economy system can employ in calculations etc...
# todo incomplete: cestus/brassknuckles? sai, trident? shuriken, chakram, quoit/dart? Torimono sandogu, mancatcher? sword cane?
weapons = {
    "handaxe": {"recipe": True},
    "mace": {"recipe": True},
    "dagger": {"recipe": True},
    "shortsword": {"recipe": True},
    "warhammer": {"recipe": False},
    "goedendag": {"recipe": False},
    "longsword": {"recipe": True},
    "quarterstaff": {"recipe": True},
    "bow": {"recipe": True},
    "longbow": {"recipe": False},
    "bastard sword": {"recipe": False},
    "claymore": {"recipe": True},  # greatsword
    "scimitar": {"recipe": False},
    "spear": {"recipe": True},
    "pike": {"recipe": False},
    "halberd": {"recipe": False},
    "javelin": {"recipe": True},
    "glaive": {"recipe": False},
    "club": {"recipe": True},
    "sling staff": {"recipe": False},
    "sling": {"recipe": True},
    "flail": {"recipe": False},
    "lance": {"recipe": False},
    "battleaxe": {"recipe": False},
    "bolas": {"recipe": False},
    "broadsword": {"recipe": False},
}
# ? separate out hte corseque/ranseur?
# ? greatclub as a lighter, cheaper, weaker, wood-only alternative to the goedendag
# dagger covers the dirk
# mace covers the morning star
# club covers all baton weapons, including the tonfa
# flail covers the ball and chain, meteor hammer, and kusari-gama
# glaive covers all other stabbing, hooking, and forking polearms, including the guisarme, faulchard, voulge, bec de corbin, ranseur, and corseque
# halberd covers all other slashing, smashing, crushing, and chopping polearms, including the  poleaxe, lucerne hammer, guandao/yanyuedao, naginata
# shortsword covers the dueling rapier, smallsword, cutlass, hanger, gladius, arming sword, estoc
# bastard sword is in between short and long; d6+1 dmg
# longsword covers the falchion
# SOMETHING between longsword and claymore -- broadsword. still onehanded but longer, heavier
# claymore covers the greatsword, two-handed sword
# scimitar covers the saber, cutlass, khopesh (sickle sword) , hunting sword
# battleaxe covers the pickaxe (military pick)
