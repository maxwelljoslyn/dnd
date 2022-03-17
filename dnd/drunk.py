from decimal import Decimal, getcontext
from characters import races, mod_to_text
from math import floor
import click


getcontext().prec = 4

# todo once economic recipes are  more structured data, import beer/ale/rum/etc ABV figures for use here
beverages = {
    "beer": {
        "abv": Decimal(4.07),
        "drinks per pint": 1,
    },
    "ale": {
        "abv": Decimal(10.6),
        "drinks per pint": 1,
    },
    "rum": {
        "abv": Decimal(29.6),
        "drinks per pint": 8,  # 2 oz. shots
    },
    "wine": {
        "abv": Decimal(13.2),
        "drinks per pint": 2,  # 4 oz. pours
    },
}

intoxication_thresholds = {
    "sober": 0,
    "tipsy": 2,
    "drunk": 4,
    "smashed": 6,
}

intoxication_effects = {
    # each level incorporates the modifiers from the previous one - do NOT add them together cumulatively!
    "sober": None,
    "tipsy": {
        "intelligence": -1,
        "dexterity": -1,
        "wisdom": -1,
        "charisma": -1,
        "HP": "+1/Hit Die",
        "morale": 1,
    },
    "drunk": {
        "intelligence": -2,
        "dexterity": -2,
        "wisdom": -3,
        "charisma": -1,
        "HP": "+2/Hit Die",
        "morale": 2,
    },
    "smashed": {
        "intelligence": -4,
        "dexterity": -4,
        "wisdom": -5,
        "charisma": -2,
        "HP": "+3/Hit Die",
        "morale": 3,
    },
}


def equivalent_drinks(kind, pints):
    """Given `pints` pints of `kind` drink, how many drink-equivalents is that for purpose of drunkenness?
    >>> equivalent_drinks('beer', 1) => 1
    >>> equivalent_drinks('rum', 1) => 8
    """
    return Decimal(pints) / beverages[kind]["drink per pint"]


# todo all these positional arguments perhaps ought to be keyword arguments
def intoxication_ratio(race, sex, weight, con):
    # since average CON is 10, the 0.1 factors it out
    # higher weight and higher CON = can drink more
    # the division COULD use human weight as the denominator, such that smaller races get blasted even more easily ... but no, b/c then small races can take little or no advantage of alcohol to heal
    # on the other hand,  for current calculation, all that matters is character weight relative to his race/sex's average ... no differentation *between* races
    return Decimal(weight) / races[race]["base weight"][sex] * con * Decimal(0.1)


# drink_taken = namedtuple(kind, pints, hours_ago)


def personal_intoxication_thresholds(race, sex, weight, con):
    # todo don't forget that drinking can harm CON, but the base CON and not the drunk-adjusted CON should be used for these thresholds and for intoxication_ratio
    ratio = intoxication_ratio(race, sex, weight, con)
    # todo I used floor() to round out these numbers, but in a drinking contest... that fraction would matter! perhaps a CON check can be used instead...
    return {k: floor(v * ratio) for k, v in intoxication_thresholds.items()}


def calculate_intoxication(race, sex, weight, con, drinks_in_body):
    thresholds = personal_intoxication_thresholds(race, sex, weight, con)
    if drinks_in_body < thresholds["tipsy"]:
        return "sober", intoxication_effects["sober"]

    elif drinks_in_body < thresholds["drunk"]:
        return "tipsy", intoxication_effects["tipsy"]

    elif drinks_in_body < thresholds["smashed"]:
        return "drunk", intoxication_effects["drunk"]

    else:
        return "smashed", intoxication_effects["smashed"]


# @action
# def take_drink(race, weight, sex, con, beverage, pints, drinks_in_body):
#    # dib is just an int -- equivalent drinks calculated before adding to it, and you just subtract 1 every hour
#    # at call site of take_drink, update the drinks_in_body of the character
#    drinks_in_body += equivalent_drinks(beverage, pints)
#    return (
#        calculate_intoxication(race, weight, sex, con, drinks_in_body),
#        drinks_in_body,
#    )


def intoxication_to_text(level, effects):
    def textify(effect):
        if isinstance(effect, int):
            return mod_to_text(effect)
        else:
            return effect

    drunk_injury_size = {"tipsy": 1, "drunk": 2, "smashed": 3}

    effects = "\n".join([f"{k}: {textify(v)}" for k, v in effects.items()])
    result = [
        f"Intoxication level: {level}.",
        "Effects (not cumulative with earlier effects):",
        f"{effects}",
    ]
    if level != "sober":
        result.append(
            f"After losing the above HP, Dex check or sustain {drunk_injury_size[level]}-point injury."
        )
    return "\n".join(result)


@click.command()
@click.option("--con", type=int, help="CON score of character", prompt=True)
@click.option(
    "-s",
    "--sex",
    type=click.Choice(["m", "male", "f", "female"], case_sensitive=False),
    help="Sex of character",
    prompt=True,
)
@click.option(
    "-r",
    "--race",
    type=click.Choice(list(races.keys()), case_sensitive=False),
    help="Race of character",
    prompt=True,
)
@click.option(
    "-w",
    "--weight",
    type=float,
    help="Weight of character",
    prompt=True,
)
@click.option(
    "-d",
    "--drinks",
    type=int,
    help="Drinks currently in character's body",
    prompt=True,
)
def main(race, sex, weight, con, drinks):
    if not race:
        print("Randomizing race")
        race = "dwarf"

    if not sex:
        print("Randomizing sex")
        sex = "male"
    if sex == "m":
        sex = "male"
    if sex == "f":
        sex = "female"

    if not con:
        print("Randomizing con")
        con = 10

    if not weight:
        print("Randomizing weight")
        weight = 125.0
    weight = Decimal(weight)

    if not drinks:
        print("Randomizing drinks")
        drinks = 0

    # print(
    #    f"A {sex} {race} with {con} Con @ {weight} lbs has thresholds:\n"
    #    + str(
    #        {
    #            k: f"{v} drinks"
    #            for k, v in personal_intoxication_thresholds(
    #                race, sex, weight, con
    #            ).items()
    #        }
    #    )
    # )
    level, effects = calculate_intoxication(race, sex, weight, con, drinks)
    print(intoxication_to_text(level, effects))


if __name__ == "__main__":
    main()
