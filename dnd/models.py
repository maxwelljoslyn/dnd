town_model = {
    "towns": {
        "name": "TEXT UNIQUE NOT NULL",
        "population": "REAL NOT NULL",
    },
    "town_references": {
        "town": "INTEGER NOT NULL",  # references towns.rowid
        "name": "TEXT NOT NULL",
        "amount": "TEXT NOT NULL",  # a stringified pint unit
    },
    "travel_times": {
        "source": "INTEGER NOT NULL",  # references towns.rowid
        "destination": "INTEGER NOT NULL",  # references towns.rowid
        "distance": "REAL",  # i want it possible to insert a town with no connections yet specified
    },
    "material_costs": {
        "town": "INTEGER",  # references towns.rowid
        "name": "TEXT NOT NULL",
        # TODO randomize material costs based on in-game year and week
        # "year": "INTEGER NOT NULL",
        # "week": "INTEGER NOT NULL", # TODO limit range 1-52
        "price": "TEXT NOT NULL",
    },
}

tradegood_model = {
    "tradegoods": {
        "name": "TEXT UNIQUE NOT NULL",
        "recipe": "JSON NOT NULL",
    },
    "prices": {
        "name": "TEXT NOT NULL",  # references tradegoods.name
        "town": "INTEGER NOT NULL",  # references towns.rowid
        "price": "TEXT NOT NULL",  # a stringified pint unit
        # TODO randomize trade good availability, based on good's final price for a given year and week
        # "year": "INTEGER NOT NULL",
        # "week": "INTEGER NOT NULL",  # TODO limit range 1-52
        # "base_number_available": "INTEGER NOT NULL", # range 0 to N ... also, oh god this is updatable STATE!!!!! unless I call this BASE availability, track transactions somewhere else, another table, and compare total transactions for X against this number without updating in place
    },
}

global_model = {
    "date": {"date": "TEXT NOT NULL"},
}


# TODO instead of purchases table, a table of actions/events, with "purchase" as just one of many, many types
# "purchases": {
#    # DO NOT put this table in tradegood_model: that stores current tradegood prices, which will be change during gameplay. these purchase records must not be touched when that happens
#    "date": "TEXT NOT NULL",
#    "character": "INTEGER NOT NULL",  # references characters.rowid
#    "town": "INTEGER NOT NULL",  # references towns.rowid
#    "tradegood_name": "TEXT NOT NULL",  # references tradegoods.name; if I want to give an item not yet programmed, it won't show up in this table
#    "quantity": "INTEGER NOT NULL",
#    "unit_price": "REAL NOT NULL",
# },
