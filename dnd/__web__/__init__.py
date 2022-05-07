import web
from web import tx
import json

import dnd

muh_regex = r"[\w\d'\-, ]+"
ability_regex = "|".join(dnd.characters.abilities.keys())
class_regex = "|".join(dnd.characters.classes.keys())
race_regex = "|".join(dnd.characters.races.keys())
entity_id_regex = r"[\d]+"
player_id_regex = entity_id_regex
integer_regex = r"[\d]+"
coin_regex = r"gp|sp|cp"


app = web.application(
    __name__,
    db=True,
    args={
        "tradegood": muh_regex,
        "town": muh_regex,
        "player": muh_regex,
        "pc": muh_regex,
        "ability": ability_regex,
        "eid": entity_id_regex,
        "pid": player_id_regex,
        "integer": integer_regex,
        "coin": coin_regex,
        "klass": class_regex,
        "race": race_regex,
    },
    model={
        "players": {"name": "TEXT NOT NULL"},
        "characters": {
            "player_id": "INTEGER NOT NULL",
            "name": "TEXT NOT NULL",
        },
        "inventory": {
            "owner_id": "INTEGER",
            "item_id": "INTEGER",
        },
        "items": {
            "name": "TEXT",
        },
        "money": {
            "owner_id": "INTEGER",
            "coin": "TEXT",
            "amount": "INTEGER",
            # PRIMARY KEY (OWNER_ID, COIN)
        },
        "creation": {
            "player_id": "INTEGER UNIQUE NOT NULL",
            "step": "INTEGER",
            "state": "JSON",
        },
    },
)

all_characters = {
    "Fritz": {
        "player": "Angelo",
        "class": "fighter",
        "abilities": {
            "strength": 16,
            "dexterity": 12,
            "constitution": 15,
            "intelligence": 11,
            "wisdom": 9,
            "charisma": 18,
        },
        "location": "Pearl Island",
        "money": {"gp": 300 * dnd.u.gp, "sp": 7 * dnd.u.sp, "cp": 18 * dnd.u.cp},
    },
    "Grunkus": {
        "player": "Dave",
        "class": "mage",
        "abilities": {
            "strength": 7,
            "dexterity": 10,
            "constitution": 14,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 10,
        },
        "location": "Allrivers",
        "money": {
            "sp": 19 * dnd.u.sp,
            "cp": 1 * dnd.u.cp,
        },
    },
}


def setup_db():
    for c, info in all_characters.items():
        player = info["player"]
        pid = tx.db.insert("players", name=player)
        eid = tx.db.insert("characters", player_id=pid, name=c)
        for coin, quantity in info["money"].items():
            tx.db.insert("money", owner_id=eid, coin=coin, amount=quantity.magnitude)


@app.control("setupdb")
class SetupDB:
    def get(self):
        try:
            setup_db()
            raise web.OK("OK")
        except Exception as e:
            raise e


def render_role(role):
    return {"dm": "the DM", "player": "a player"}.get(role, None)


def can_afford(price, wealth):
    return dnd.to_copper_pieces(price) <= dnd.to_copper_pieces(wealth)


def pull_money(eid):
    # return tx.db.execute(
    #    "select c.rowid, c.name, m.coin, m.amount from characters as c join money as m on c.rowid=m.owner_id"
    # )
    return tx.db.select("money", where="owner_id = ?", vals=[eid])


def add_money(eid, cointype, to_add):
    #    for each in pull_money(eid):
    #        coin = each["coin"]
    #        amount = each["amount"]
    #        if coin not in existing_money:
    #            existing_money[coin] = amount
    #        else:
    #            existing_money[coin] += amount
    existing = tx.db.select(
        "money", where=f"owner_id={eid} AND coin = ?", vals=[cointype]
    )[0]
    if not existing:
        tx.db.insert("money", owner_id=eid, coin=cointype, amount=to_add)
    else:
        new_amount = int(existing["amount"]) + int(to_add)
        tx.db.update(
            "money",
            where=f"owner_id={eid} AND coin = ?",
            amount=new_amount,
            vals=[cointype],
        )


def pull_characters(pid=None):
    if pid:
        return tx.db.select(
            "characters", what="rowid, *", where="player_id = ?", vals=[pid]
        )
    else:
        return tx.db.select("characters", what="rowid, *")


def pull_character(eid):
    return tx.db.select("characters", what="rowid, *", where="rowid = ?", vals=[eid])[0]


def pull_character_byname(pid, name):
    return tx.db.select(
        "characters",
        what="rowid, *",
        where="player_id = ? AND name = ?",
        vals=[pid, name],
    )[0]


def pull_players():
    return tx.db.select("players", what="rowid, *")


def pull_player(pid):
    return tx.db.select("players", what="rowid, *", where=f"rowid = ?", vals=[pid])[0]


def pull_inprogress_chargens():
    return tx.db.select("creation", what="player_id, step, state")


def chargen_step(pid):
    inprogress_chargens = pull_inprogress_chargens()
    for row in pull_inprogress_chargens():
        if row["player_id"] == pid:
            return row["step"]
    return 0


@app.control("dm/dashboard")
class DMDashboard:
    def get(self):
        chars = pull_characters()
        return app.view.dashboard(chars)


@app.control("dm/givemoney/character/{eid}/{coin}/{integer}")
class GiveMoney:
    def post(self, eid, coin, integer):
        return add_money(eid, coin, integer)


@app.wrap
def every_request(handler, main_app):
    tx.user.pid = tx.user.session.get("pid")
    tx.user.role = tx.user.session.get("role")
    tx.user.name = tx.user.session.get("name")
    tx.user.role_string = render_role(tx.user.role)
    yield


@app.control("")
class Home:
    """Profile and primary feed."""

    def get(self):
        """Render a profile summary and a reverse chronological feed of public posts."""
        return app.view.index(dnd.towns, dnd.registry)


@app.control("towns/{town}")
class Town:
    def get(self, town):
        info = dnd.towns.get(town)
        if not info:
            raise web.BadRequest
        has_market = dnd.has_market(town)
        if has_market:
            vendors = dnd.vendors
        else:
            vendors = dnd.limited_vendors
        industries = dnd.original_towns[town]["references"].keys()
        return app.view.town(
            town,
            info,
            dnd.registry,
            has_market,
            vendors,
            industries,
        )


@app.control("tradegoods/{tradegood}")
class TradeGood:
    def get(self, tradegood):
        info = dnd.registry.get(tradegood)
        if not info:
            raise web.BadRequest
        return app.view.tradegood(
            tradegood, info, dnd.registry, dnd.vendors, dnd.limited_vendors
        )


@app.control("x/map")
class Map:
    def get(self):
        return app.view.map("foo")


# TODO update this to use DB
@app.control("rules/{ability}")
class Ability:
    def get(self, ability):
        abilitymap = {
            s: [
                c
                for c, info in all_characters.items()
                if info["abilities"][ability] == s
            ]
            for s in range(1, 21)
        }
        return app.view.ability(ability, dnd.characters.abilities[ability], abilitymap)


@app.control("rules/{klass}")
class CharacterClass:
    def get(self, klass):
        return app.view.klass(klass, dnd.characters.classes[klass])


@app.control("rules/{race}")
class CharacterRace:
    def get(self, race):
        return app.view.race(race, dnd.characters.races[race])


@app.control("login-player")
class LogInPlayer:
    def get(self):
        return app.view.login_player(pull_players())


@app.control("login")
class LogIn:
    def get(self):
        return app.view.login()

    def post(self):
        role = web.form("role").role
        if not role:
            raise web.BadRequest("Must provide role: DM or Player")
        elif role == "dm":
            tx.user.session.update(role="dm")
            # ignore any name that might be in the form: those are player names
            tx.user.session.update(name="Maxwell")
        else:
            pid = web.form("pid").pid
            name = pull_player(pid)["name"]
            tx.user.session.update(role="player")
            tx.user.session.update(pid=int(pid))
            tx.user.session.update(name=name)
        raise web.SeeOther("/")


@app.control("logout")
class LogOut:
    def post(self):
        tx.user.session = {}
        raise web.SeeOther("/")


@app.control("dm")
class DM:
    def get(self):
        # TODO update this
        return app.view.dm([(c, info["player"]) for c, info in all_characters.items()])


@app.control("players/{pid}")
class Player:
    def get(self, pid):
        name = pull_player(pid)["name"]
        return app.view.player(pid, name, pull_characters(pid))


# TODO should this use a get query parameter to pass player (and character) meanig all I need is players, players/player, characters, character?player=foo
# TODO handle non unique player names; enforce unique character names PER PLAYER only (eg Ange and DAve can both play a Grunkus, but Ange cannot have TWO PCs named Grunkus)
@app.control("players/{pid}/characters/{eid}")
class PC:
    def get(self, pid, eid):
        # TODO get from database instead
        pc = pull_character(eid)["name"]
        return app.view.pc(pc, pull_money(eid))


@app.control("players/{pid}/characters/{pc}")
class PCByName:
    def get(self, pid, pc):
        eid = pull_character_byname(pid, pc)["rowid"]
        return app.view.pc(pc, pull_money(eid))


character_creation_steps = {
    1: "/create/rolls",
    2: "/create/assign",
}


@app.control("create/start")
class StartCharacterCreation:
    def get(self):
        if not tx.user.pid:
            raise web.SeeOther("/login")
        else:
            raise web.SeeOther(f"/players/{tx.user.pid}")

    def post(self):
        if not tx.user.pid:
            raise web.BadRequest("not logged in as player")
        else:
            step = chargen_step(tx.user.pid)
            if step:
                # TODO put this under unified /characters/create/step/X
                raise web.SeeOther(
                    character_creation_steps.get(step, "/notimplemented")
                )
            else:
                tx.db.insert("creation", player_id=tx.user.pid, step=1, state={})
                raise web.SeeOther("/create/rolls")


@app.control("create/rolls")
class CharacterCreationRolls:
    def get(self):
        if not tx.user.pid:
            raise web.SeeOther("/login")
        # TODO check if they are already on step 2; if so, redirect to '/create/assign'
        # step = tx.db.select('creation', what='step', where='player_id = ?', vals=[tx.user.pid])
        return app.view.rolls()

    def post(self):
        rolls = []
        for n in range(1, 7):
            x = web.form()[f"roll-{n}"]
            rolls.append(int(x))
        tx.db.update(
            "creation",
            step=2,
            state={"rolls": rolls, "abilities": {}, "class": None, "race": None},
            where="player_id = ?",
            vals=[tx.user.pid],
        )
        raise web.SeeOther("/create/assign")


def chargen_state(pid):
    q = tx.db.select(
        "creation",
        what="json_extract(state, '$')",
        where="player_id = ?",
        vals=[pid],
    )
    return json.loads(q[0][0])


def chargen_abilities(pid):
    abilities = tx.db.select(
        "creation",
        what="json_extract(state, '$.abilities')",
        where="player_id = ?",
        vals=[pid],
    )
    return json.loads(abilities[0][0])


def chargen_rolls(pid):
    rolls = tx.db.select(
        "creation",
        what="json_extract(state, '$.rolls')",
        where="player_id = ?",
        vals=[pid],
    )
    return json.loads(rolls[0][0])


def chargen_class(pid):
    klass = tx.db.select(
        "creation",
        what="json_extract(state, '$.class')",
        where="player_id = ?",
        vals=[pid],
    )[0][0]
    if not klass:
        return None
    else:
        return json.loads(klass)


def chargen_race(pid):
    race = tx.db.select(
        "creation",
        what="json_extract(state, '$.race')",
        where="player_id = ?",
        vals=[pid],
    )[0][0]
    if not race:
        return None
    else:
        return json.loads(race)


@app.control("create/assign")
class CharacterCreationAssignment:
    def get(self):
        state = chargen_state(tx.user.pid)
        rolls = state["rolls"]
        abilities = state["abilities"]
        race = state.get("race", None)
        klass = state.get("class", None)
        return app.view.assign(rolls, abilities, race, klass)

    def post(self):
        state = chargen_state(tx.user.pid)
        rolls = state["rolls"]
        abilities = state["abilities"]
        race = state.get("race", None)
        klass = state.get("class", None)
        if rolls or not abilities:
            raise web.BadRequest("You haven't assigned all your ability score rolls")
        if not race:
            raise web.BadRequest("You haven't chosen a race")
        if not klass:
            raise web.BadRequest("You haven't chosen a class")
        return "POSTED"


@app.control("create/assign/{ability}")
class AssignAbility:
    def post(self, ability):
        state = chargen_state(tx.user.pid)
        rolls = state["rolls"]
        abilities = state["abilities"]
        try:
            num = int(web.form()[ability])
        except ValueError:
            raise web.BadRequest("You didn't enter a number before pressing Assign")
        rolls.remove(num)
        abilities[ability] = num
        state["rolls"] = rolls
        state["abilities"] = abilities
        tx.db.update(
            "creation",
            state=state,
            where="player_id = ?",
            vals=[tx.user.pid],
        )
        raise web.SeeOther("/create/assign")


@app.control("create/clear/{ability}")
class ClearAbility:
    def post(self, ability):
        state = chargen_state(tx.user.pid)
        rolls = state["rolls"]
        abilities = state["abilities"]
        score = abilities[ability]
        rolls.append(score)
        del abilities[ability]
        state["rolls"] = rolls
        state["abilities"] = abilities
        tx.db.update(
            "creation",
            state=state,
            where="player_id = ?",
            vals=[tx.user.pid],
        )
        raise web.SeeOther("/create/assign")


@app.control("create/assign/race")
class AssignRace:
    def post(self):
        state = chargen_state(tx.user.pid)
        r = web.form()["race"]
        state["race"] = r if r else None
        if r:
            # invalidate class not allowed for this race
            c = state.get("class")
            if c and c not in dnd.characters.races[r]["permitted classes"]:
                state["class"] = None
        tx.db.update(
            "creation",
            state=state,
            where="player_id = ?",
            vals=[tx.user.pid],
        )
        raise web.SeeOther("/create/assign")


@app.control("create/assign/class")
class AssignClass:
    def post(self):
        state = chargen_state(tx.user.pid)
        c = web.form()["class"]
        state["class"] = c if c else None
        tx.db.update(
            "creation",
            state=state,
            where="player_id = ?",
            vals=[tx.user.pid],
        )
        raise web.SeeOther("/create/assign")


# Keep it /completely/ separate from your current DND at first if you need to. Just stash into the db and `exec()` the Python in the textarea. Handle entering the following into the textarea:
#
#    background = "#39f"
#
# The DM enters that, and player's page's background turn blue. then start porting your code-the-dm-needs-to-have-access-to into this textarea, one teeny tiny chunk at a time. make sure the user and dm pages reflect the changes. bonus points for things that take on the order of minutes (say, tectonic calculations). start thinking about other dm's using this software. start thinking about merging/sync'ing the two textareas' contents. start thinking about merging those very same textareas with the state of the data on the user's screen. but start with the single-dm using python to modify in-game world state. that's the trivial case and it should be well within your capability to implement it.
#
# Leverage the `locals` and `globals`:
# https://docs.python.org/3/library/functions.html#exec
#
# Provide access to a /simplified/ "economy" but also a world map. If you wind up putting a bunch of /data/ inside the textarea then start thinking of a way to pull that data /out/ of the textarea and into /anywhere else on the page/ and /how/..
# You have to be pushing into this "new" territory during your thesis.. You need to be able to import tectonic's world into your system. You need to be able to pull Alexsi's ideas in (with effort, but quickly) to the magic python textarea.
# The magic python textarea should read pure. Provide helper functions as locals and allow modification of supplied globals to all for the configuration of the world state.


@app.control("rules/weapons")
class Weapons:
    def get(self):
        return app.view.weapons(dnd.weapons, dnd.registry)


@app.control("rules/saving-throws")
class SavingThrows:
    def get(self):
        return app.view.savingthrows()

