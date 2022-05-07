#"""
#>>> import dice
#>>> from dice import constant as c
#>>> dice.XdY(2,6)
#Dice(2d6)
#>>> dice.XdY(3,10)
#Dice(3d10)
#>>> dice.Xd6(3)
#Dice(3d6)
#>>> dice.Dice(2,6)
#Dice(2,6)
#>>> dice.4d6.roll()
#23
#>>> dice.4d6.min #propertized fun
#4 
#>>> dice.4d6.max #ditto
#24
#>>> dice.4d6.average 
#14
#>>> dice.4d6 + c(1)
#Dice(4d6+1)
#>>> dice.4d6 - c(1)
#Dice(4d6-1)
#>>> dice.4d6 + dice.3d6
#Dice(7d6)
#>>> dice.4d6 + dice.3d5
#Dice(4d6+3d5)
#"""

import random


class DicePool:
    def __init(self):
        # todo parse expression
        pass

    def roll(self):
        sum = 0
        for die in self.dice:
            # eg Die(size=3)
            sum += random.randint(1, die.size)
        for (op, value) in self.constants:
            # eg ('+', 1)
            sum = call(op, sum, value)
        return sum


# >>> dagger = Weapon("dagger", damage=dice.1d4, range=[ranges.Melee, ranges.Thrown], ...)
# >>> shortsword = Weapon("shortsword",
# damage=dice.1d6,
# range=[ranges.Melee], ...)
# >>> shortsword = Weapon("greatsword",
# damage=dice.2d6,
# hands=2,
# range=[ranges.Melee], ...)
# >>> albrecht = PC("fighter", strength=16, dexterity=10)
# >>> albrecht.wield(shortsword)
# >>> baldur = PC("mage", strength=7, dexterity=10)
# >>> baldur.wield(dagger)
# >>> albrecht.modifiers
# >>> albrecht.act(actions.attack, albrecht.primary_weapon, baldur)
# >>> def attack(self, weapon=None, defender):
# ...    # another way to do it: make attack a class, and on there define the string/whatever which it uses to search self.modifiers for applicable mods
# ...    # may gel better with action("attack") action("draw weapon") action("take off backpack") etc.
# ...    if not weapon:
# ...        weapon = self.primary_weapon
# ...    attack = dice.1d20.roll()
# ...    attack += sum(v for k, v in self.modifiers.items() if k.modifies('attack'))
# ...    if attack >= defender.armor_class:
# ...        damage = weapon.damage.roll()
# ...        defender.lose_hp(damage)
# ...    else:
# ...        return
#
#
## 17 str
# def ability_check(modified_score):
#  if modified_score == 0:
#    return check.Fail
#  else:
#    result = dice.d20.roll()
#  if result <= modified_score:
#    return check.Succeed
#  else:
#    if modified_score < 20:
#      return check.Fail
#    else:
#      # score is 20 or higher
#      # "second chance" roll
#      target = modified_score-20+1
#      second_chance = dice.d20.roll()
#      if second_chance <= target:
#        return check.Succeed
#      else:
#        return check.Fail
#
# str 18
# d20: 18, or lower Succ
# d20: 19,20 Fail
# 90% succ, 10% fail
#
# str 19
# d20: 19, or lower Succ
# d20: 20 Fail
# 95% succ, 5% fail
#
# str 20
# d20 19 or less -> Succ
# d20: 20  -> d20: 1 Succ
# d20: 20  -> d20: 2-20 Fail
# 96, 4 fail
#
# str 21
# d20 19 or less -> Succ
# d20: 20  -> d20: 1-2 Succ
# d20: 20  -> d20: 3-20 Fail
# 97%, 3% fail
#
# str 22
# d20 19 or less -> Succ
# d20: 20  -> d20: 1-3 Succ
# d20: 20  -> d20: 4-20 Fail
#
# str 21
# str 22
#
#
#
#
## (4+24)/2=14 ; as with .min and .max, way in which these are implemented will change how easy it is to add 2 Dice objects
# db.4d6.distribution
# db.4d6.permutations # ways ofarranging the 4 dice
# ....
# >>> dice.2d6.chance_to_equal(1)
# 0
# >>> dice.2d6.chance_to_equal(2)
# 1/12
# >>> dice.2d6.chance_to_equal(3)
# 2/12
# >>> dice.4d6.chance_x_or_higher(x)
# >>> dice.4d6.chance_x_or_lower(x)
