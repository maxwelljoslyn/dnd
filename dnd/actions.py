actions = {
    "Cancel Spell": {
        "cost": 0,
        "description": "While holding a cast spell, release it to no effect (instead of discharging it as normal.) The spell cannot be recast until it is prepared anew.",
    },
    "Change Facing, Unthreatened": {
        "cost": 0,
        "description": "Change which way you are facing.",
    },
    "Change Facing, Threatened": {
        "cost": 1,
        "description": "Change which way you are facing while you are within melee range of an enemy.",
    },
    "Drop Object": {
        "cost": 0,
        "description": "Drop an item you are carrying in one or both hands.",
    },
    "Reposition Stunned Ally While Moving": {
        "cost": 0,
        "description": "If you move into a stunned ally's hex, you may assist them into the hex you just exited at no cost. Cannot be done while running.",
    },
    "Activate Item": {
        "cost": 1,
        "description": """This cost is required to begin using any object, magic or mundane, which must somehow be started up or stimulated before use. The required time includes any steps the item itself goes through when activated, such as reshaping or changing colors, but does not include any time the item might need to gather energy or otherwise reach peak performance.

Examples: throwing a lever; pushing a button; speaking a command word; rubbing a ring; employing any magical device, including wands, staves, and rods.""",
    },
    "Adjust Item for Use": {
        "cost": 1,
        "description": """Orient or right an object which, once picked up, still needs to be positioned properly before use. Bows and crossbows do not need to be adjusted for use after they are drawn. Shields must be adjusted for use whether picked up or unslung from a belt.

Examples: rotating a shield and gripping its handle; positioning a compass; focusing with a magnifying glass.""",
    },
    "Apply Fluid": {
        "cost": 5,
        "description": "Includes applying poison to a weapon, soaking a torch in fuel, spreading glue on a surface, or oiling a rope. Both the fluid and the object must already be in hand. In the case of spreading fluid on a surface, 5 square feet can be covered; in the case of applying fluid to a rope or similar, 10 linear feet can be covered. Note that a combat hex (5 foot diameter) is 21.65 square feet.",
    },
    "Attack with Weapon": {
        "cost": 2,
        "description": "TODO",
    },
    "Awaken Other Quietly": {
        "cost": 3,
        "description": "Wake up a creature by shaking it awake.",
    },
    "Awaken Other Noisily": {
        "cost": 1,
        "description": "Wake up a creature by shouting at it.",
    },
    "Awaken Self": {
        "cost": 4,
        "description": """This refers to going from complete sleep to active, effective awareness. Once complete, you are entitled to your full normal AC, and can take other actions as desired.

This action is usually only available if a nearby creature is making noise, or if a creature has targeted you with a Awaken Other action.""",
    },
    "Change Shape": {
        "cost": 4,
        "description": """Transform your physical shape, such as via a supernatural ability, or a druid spell which turns the recipient into a fearsome beast.

If changing into a larger shape, any armor or helmet worn must save vs. crushing blow or lose 1 point of durability. Other worn items, including clothes, meld into your body as you transform. Held items are dropped.""",
    },
    "Adjust Lantern Illumination": {
        "cost": 1,
        "description": "Turn a lantern's key to raise or lower its level of illumination one step: open <--> half-open <--> shaded.",
    },
    "Close, Lock, or Unbuckle": {
        "cost": 2,
        "description": "Examples: closing a buckle; doing up a drawstring, such as for a saddlebag or backpack; locking a box or chest; locking or barring a door; tying shut a scroll case.",
    },
    "Maintain Spell": {
        "cost": 4,
        "description": "Continue the effect of a spell which requires sustained concentration after it has been discharged.",
    },
    "Discharge Spell": {
        "cost": 1,
        "description": "Release a cast spell to produce its effect. With certain exceptions for specific spells, you must discharge a spell the round it is cast, or else it will be lost and wasted as if you had chosen to dissipate it. Finally, until a held spell is discharged, the only other action you may take each round is moving 1 hex (at the normal cost.)",
    },
    "Mount Animal": {
        "cost": 4,
        "description": "Clamber up and straddle a horse or similarly-sized riding animal, including mules, donkeys, pegasi, and griffons.",
    },
    "Dismount Animal": {
        "cost": 3,
        "description": "Lower yourself down from astride a horse or similarly-sized riding animal, including mules, donkeys, pegasi, and griffons.",
    },
    "Dismiss Spell": {
        "cost": 1,
        "description": "End a spell you have cast with an ongoing effect, such as Charm Person, Rope Trick, or Wall of Fire. You do not need to have line of sight, nor be anywhere near the spell's effect, to dismiss it. Not to be confused with Cancel Spell.",
    },
    "Draw Weapon, Two-Handed": {
        "cost": 3,
        "description": "Begin wielding any weapon which *you* must use with two hands, even if that is not the case for others. Includes spears (even if they are to be thrown) and all bows and crossbows.",
    },
    "Draw Weapon, Heavy One-Handed": {
        "cost": 2,
        "description": "Begin wielding any weapon weighing 3 pounds or more.",
    },
    "Draw Weapon, Light One-Handed": {
        "cost": 1,
        "description": "Begin wielding any weapon weighing less than 3 pounds.",
    },
    "Drop to the Ground": {
        "cost": 1,
        "description": "Throw yourself to the ground, such as to get behind cover or present a smaller target. Once you are on the ground, before performing any other actions, you must spend 1 AP to reorient yourself.",
    },
    "Eat": {
        "cost": 1,
        "description": "Consume 1 ounce of food.",
    },
    "Drink": {
        "cost": 1,
        "description": "Consume 2 fluid ounces of liquid. Any liquid bestowing an effect on the drinker, such as an alcoholic beverage or a magic potion, must be fully consumed to take effect. A typical potion is 8 fluid ounces; a beer, 16 fluid ounces; a shot of liquor, 2 fluid ounces; a glass of wine, 4 fluid ounces.",
    },
    "Extinguish Candle": {
        "cost": 1,
        "description": "Put out a candle by any ordinary method, including blowing it out, pinching it out, or using a snuffer.",
    },
    "Extinguish Torch in Water": {
        "cost": 1,
        "description": "Put out a torch. Requires at least four inches of water.",
    },
    "Extinguish Torch Physically": {
        "cost": 2,
        "description": "Smother a torch with dirt or wet cloth. The torch can alternatively be stamped out, but this will break the torch stake.",
    },
    "Light a Torch": {
        "cost": 3,
        "description": "Ignite a prepared torch. The torch must already be soaked in fuel (see Apply Fluid), and the means to light it (open flame, match, etc.) must already be at hand. If the torch is waterlogged, only an open flame will light it, and this action will take double the normal AP.",
    },
    #'Load and Aim': {
    #'cost': 4
    # From this cost, we can see that an ordinary combatant will have to load and aim one round, and fire the next.
    #
    # The combatant can also decide to load and aim quickly, expending only 2 AP instead of 4, but the attack roll will have a -4 penalty. If the combatant has two attacks this round, they can forgo the second attack and instead load and fire in one round with no penalty.
    #
    # Once you have taken this action, you must fire at some point on your next turn (it doesn't have to be your first 2 AP.) Otherwise, you have missed your moment, and will have to load and aim again.
    #
    # },
    #'Load Crossbow, Heavy': {
    #'cost': 11
    # This is done by pointing the crossbow down, sinking its point into the ground to stabilize it, and then cranking until the drawstring catches on the nut, at which point it is tight enough to fire; the crossbow is then lifted and the bolt is inserted (the last 1 AP of the cost.) The weapon can be fired as soon as loading is completed, if sufficient AP remain.
    #
    # },
    #'Load Crossbow, Light': {
    #'cost': 7
    # This is done by bracing the crossbow against the body and cranking the cranequin until the drawstring catches on the nut, at which point it is tight enough to fire; the bolt can then be inserted (the last 1 AP of the cost.) Note that owing to its loading method, the light crossbow can be reloaded while on horseback, unlike its heavier counterpart. The weapon can be fired as soon as loading is completed, if sufficient AP remain.
    #
    # },
    #'Mount Animal': {
    #'cost': 4
    # Includes dismounting from horses and similarly-sized animals, as listed under "Dismount."
    #
    # },
    #'Open or unlock': {
    #'cost': 2
    # Includes opening or unlocking a chest, box, or door, as well as unbuckling straps or untying knots that hold some item closed.
    #
    # An unlocked door can be shouldered open for only 1 AP as part of moving through the hex it is in, but this means the combatant has committed to moving through the door without getting a chance to look through it.
    #
    # },
    #'Pick up Object': {
    #'cost': 1 or more
    # This refers to a Small or Medium humanoid picking up an object which is lying on the ground. 1 AP is required for an item up to 5 lbs; 2 AP for up to 8 pounds; 3 AP for up to 13 lbs; 4 AP for up to 21 lbs, and so on, up to the maximum weight which the combatant can carry.
    #
    # },
    #'Putting on Armor': {
    #'cost': 25 AP per point of Armor Class
    # This reflects the amount of time needed to put on and secure all the bits and pieces that go into a suit of armor. Enough of the armor can be put on with 25 AP that the character's Armor Class is lowered by 1; thus, if time is critical, partial armor can be worn (the exact body parts covered are not important.) Remember that as the character achieves enough armoring for an AC of 7, 5, or 3, his or her AP will decrease. Thus, the requisite 25 AP will take more rounds to achieve as heavier armors approach full readiness.
    #
    # An assistant can help in this process, reducing the cost per point from 25 to 15 AP. The assistant needs no special skills: they are just adding an extra pair of hands.
    #
    # },
    #'Pull In Rope': {
    #'cost': 1 AP per 5 feet
    # This refers to a character pulling a rope which is attached to some weight. This can be done as long as the rope's weight plus the character's carried equimnt does not exceed the character's maximum load; if it does, then additional pullers must be employed. Each puller must be spaced ten feet apart, i.e. with one hex separating him from the pullers before and behind him.
    #
    # },
    #'Search Backpack': {
    #'cost': 3-4 or 5-7 AP
    # This refers to opening a backpack and rummaging through its contents. Even a thing which might be obvious is made more difficult to retrieve by the problem of getting it without spilling other items. The combatant makes an Intelligence check: if successful, the time is in the shorter range; if unsuccessful, use the longer range.
    #
    # Searching does not include getting the backpack off the back and onto the ground ("Unsling Backpack"), opening it ("Open or unlock"), closing it once done ("Close or lock"), or putting it back on ("Sling Backpack".) This is why it's a good idea to carry the most important items on one's person ... which makes the question of what items go in your belt pouch an important one indeed.
    #
    # },
    #'Search Saddlebag': {
    #'cost': 1-2 or 3-4 AP
    # Unlike backpacks, saddlebags do not need to be removed from their carrier to be searched: they are designed to be accessed either from the mount or while standing next to it. Otherwise the rules are the same as for searching a backpack.
    #
    # },
    #'Stow Item at Waist': {
    #'cost': 2
    #
    # },
    #'Stow Item at Shoulder': {
    #'cost': 3
    #
    # },
    #'Stow or Retrieve Pocketed or Tied Item': {
    #'cost': 1 to 3 AP
    # Refers to taking an item out of, or replacing it into, its storage place in one's pockets or convenient (non-hidden) folds of one's clothing, as well as breaking off items tied to one's person by a string or strip of leather. This action obviously requires a free hand.
    #
    # Getting access to these items requires digging around in clothing, adjusting oneself, and shifting held or carried objects; the more things to dig through, the slower retrieval gets, and so the AP cost depends on how encumbered a character is.
    #
    # If the character's encumbrance penalty is 0, this action requires 1 AP; encumbrance penalty -1 or -2, and this action requires 2 AP; -3 or higher, and this action requires 3 AP.
    #
    # },
    #'Speak': {
    #'cost': variable AP
    # This refers to shouted communication while taking the time to ensure the words are heard accurately over the noise of battle. The cost depends on how far the recipient is from the speaker.
    #
    # Within 1 hex: 1 AP per 8 words
    # Within 2 hexes: 1 AP per 6 words
    # Within 5 hexes: 1 AP per 4 words
    # Within 9 hexes: 1 AP per 2 words
    # Within 12 hexes: 1 AP per word
    #
    # Beyond 12 hexes (60 feet), one cannot make oneself heard over the din of combat.
    #
    # },
    #'Stand from Laying Position': {
    #'cost': 2
    # Time needed to get up and into a fighting stance.
    #
    # },
    #'Stand from Sitting Position': {
    #'cost': 1
    # Time needed to get up and into a fighting stance.
    #
    # If seated in a chair, the combatant can spend an additional 1 AP to take the chair in hand as an improvised weapon (may require both hands, if chair is heavy.)
    #
    # },
    #'Strap Shield to Arm': {
    #'cost': 10
    # With an attendant, time is reduced to 7 AP. As with putting on armor, the attendant needs no special skill, only both hands.
    #
    # The difference between strapping a shield and merely grasping it is that if a combatant holding a shield takes a hit which causes a bleeding wound, they will drop the shield.
    #
    # },
    "Tie Rope": {
        "cost": 5,
        "description": "Fasten a rope around a person or long rigid object (tree, column, post) such that it will bear weight. Certain sage abilities speed up this action.",
    },
    "Touch Ally": {
        "cost": 1,
        "description": "Discharge a touch spell on a creature which is willing to receive it.",
    },
    "Touch Enemy": {
        "cost": 2,
        "description": "Discharge a touch spell on an unwilling creature. As a type of attack, this action requires the same AP as attacking with a weapon.",
    },
    #'Unsling Backpack': {
    #'cost': 4 or 5 AP
    # Time necessary to shrug out of the backpack and get it down in front of the combatant while remaining aware of the combat situation. If the combatant's hands are not free, unslinging a backpack requires 5 AP. If at least one hand is free, it is only 4 AP.
    #
    # },
    "Unstrap Shield from Arm": {
        "cost": 3,
        "description": "Unstrap a shield from your arm, leaving it held in that arm's hand.",
    },
    "Unsling Shield from Shoulder": {
        "cost": 2,
        "description": "Remove a shield from a shoulder belt. Remember that gripping it for combat-readiness requires an additional 1 AP (see Adjust Item for Use.)",
    },
    "Untie Rope": {
        "cost": 3,
        "description": "The opposite of Tie Rope. The character finishes this action with the rope in one hand.",
    },
}
#
#'Attack': {
#'cost': 2
# This is the amount of time which one must spend focusing on the enemy's defense in order to take advantage of an opening and attempt an attack.
#
# Normally a combatant only gets one attack per round. They cannot attack twice even if they have 4 AP; even though the time is available, they are not skilled enough to perceive a second suitable opening in enemy defenses.
#
# More skilled or dangerous combatant, such as high-level fighters and creatures with special anatomies, make more attacks within the 2 AP time frame. If such a combatant has an odd number of attacks, e.g. 3 per round, then the first AP allows the minority of the attacks (e.g. 1) and the second AP allows the remaining attacks (e.g. 2).
