from decimal import *
from math import ceil
from .RecipeDefinitions import *
from .ResourcePriceCalculator import towns, pricesPerProductionUnit, averageServiceReferences, pseudoAverageRefPercent, allServiceNames
import random

#set up the Decimal environment
getcontext().prec = 6

def findCost(city, name):
    rawMatSum = 0
    recipe = recipeStorage[name]
    for r,count in recipe.subRaws:
        base = pricesPerProductionUnit[city][r][0]
        multiplied = base * Decimal(count)
        rawMatSum += multiplied
    subRecipeSum = 0
    for r,count in recipe.subRecipes:
        # recursion! this can eventually be made more efficient by memoization,
        # i.e. by storing the result of each call to findCost in a dictionary,
        # then wrapping findCost in a method which, when given a recipe name,
        # first looks in that dictionary to see if the recipe cost has already been calculated
        base = findCost(city, r)
        # recursion
        multiplied = base * Decimal(count)
        subRecipeSum += multiplied
    componentCost = rawMatSum + subRecipeSum
    serviceNum = towns[city].services[recipe.service]
    serviceModifier = (1 / serviceNum) * pseudoAverageRefPercent
    serviceCost = (componentCost * serviceModifier * Decimal(recipe.difficulty))
    finalCost = componentCost + serviceCost
    return finalCost

def getDisplayPrice(priceInCP):
    """Given an exact price in Decimal coppers, return the rounded price,
    formatted for display in appropriate amounts of copper/silver/gold."""
    # first, round up: the difference represents merchant and tradesman profit
    rounded = ceil(priceInCP)
    divided = rounded / 100
    return divided

def baseNumberAvailable(price):
    """Given the price of an object, return a minimum and maximum number of units available for purchase.
    The number returned will not be random, but in practice we'll want to add some randomization."""
    if price < 0.1:
        return (15,25)
    if price < 0.5:
        return (10,20)
    if price < 1:
        return (5,15)
    if price < 3:
        return (5,12)
    if price < 5:
        return (5,10)
    if price < 10:
        return (3,10)
    if price < 20:
        return (3,9)
    if price < 50:
        return (3,8)
    if price < 75:
        return (3,7)
    if price < 100:
        return (3,6)
    if price < 250:
        return (2,5)
    if price < 400:
        return (1,4)
    if price < 650:
        return (0,3)
    if price < 800:
        return (0,2)
    else:
        return (0,1)

def randomNumberAvailable(price, baseRange):
    random.seed()
    baseAvail = random.randint(baseRange[0],baseRange[1])
    if baseAvail == 0:
        # slight chance that it actually WILL be available
        roll = random.randint(1,20)
        if roll == 1:
            return 1
        else:
            return 0
    else:
        rolls = []
        rolls.append(random.randint(1,4))
        # exploding availability die: if you get a 6 the amount to add or subtract gets bigger by another die
        # thus there will occasionally be ordinary products which are completely unavailable,
        # or ones with low availability which one can suddenly purchase several of
        while rolls[-1] == 4:
            rolls.append(random.randint(1,4))
        roll = sum(rolls)
        adjustmentIsPositive = random.choice([True, False])
        if adjustmentIsPositive:
            return baseAvail + roll
        else:
            temp = baseAvail - roll
            # don't want a negative number available
            if temp <= 0:
                return 0
            else:
                return temp


def evalRecipe(city, name):
    recipe = recipeStorage[name]
    basePrice = findCost(city, name)
    price = getDisplayPrice(basePrice)
    numAvail = randomNumberAvailable(price, baseNumberAvailable(price))
    return (recipe, price, numAvail)

def display(name, skeleton, info):
    """Formats a recipe's name and its already-calculated info, based on a given template skeleton."""
    recipeData = info[0]
    price = info[1]
    numAvail = info[2]
    priceString = str(price) + " GP"
    displayWeight = str(Decimal(recipeData.weight[0]).quantize(Decimal('0.01')))
    displayUnitCount = str(Decimal(recipeData.unit[0]).quantize(Decimal('0.01')))
    displayUnitName = recipeData.unit[1]
    if recipeData.unit == recipeData.weight:
        displayUnitCount = "--"
        displayUnitName = ""
    return skeleton.format(name,priceString,displayWeight,recipeData.weight[1],displayUnitCount,displayUnitName,recipeData.description, "(" + str(numAvail) + ")")


terminalOutputSkeleton = "{0:36}| {1:>10}|{2:>8} {3:>2}|{4:>8} {5:6}|{7:>4} {6}"
latexOutputSkeleton = "{0} & {1} & {2} & {3} & {4} & {5} & {7} & {6}"
htmlOutputSkeleton = "<tr><td>{0} </td><td> {1} </td><td> {2} </td><td> {3} </td><td> {4} </td><td> {5} </td><td> {7} </td><td> {6}</td></tr>"

# TODO: parameterize to cities named on the command line (any number of)
def main():
    town = "Veder Vek"
    print("At",town + ":")
    names = list(recipeStorage.keys())
    names.sort()
    # part of evaluating a recipe is determining its availability, based on its price
    # if we want the terminal-printed and latex-PDF availabilities (or any other future random value) to be the same,
    # we only want to call evaluate once,
    # then store the results of those calls to send as the info parameter whenever we make a call to display
    evaluatedRecipes = {}
    print("{0:36}  {1:>10} {2:>8} {3:>2} {4:>8} {5:6} {6}".format("Name","Price","Weight","","Units",""," (#) Description"))
    for n in names:
        if n in semiGoods:
            pass
        else:
            info = evalRecipe(town,n)
            evaluatedRecipes[n] = info
            print(display(n,terminalOutputSkeleton,info))
    print("Number of recipes:",len(names))
    with open("RecipePrinter.tex","w") as f:
        f.write(r"\documentclass{article}" + "\n" + r"\usepackage{booktabs}\usepackage{longtable}\usepackage[a4paper,margin=0.6in,landscape]{geometry}\title{Price Table: " + town + r"}" + "\n" + r"\renewcommand{\tabcolsep}{3pt}\begin{document}\maketitle")
        f.write('\n')
        f.write(r"\hskip-2.0cm\begin{longtable}" + r"{lrrlrlll}")
        f.write('\n')
        f.write(r"\multicolumn{1}{l}{\em{Item}} & \multicolumn{1}{c}{\em{Price}} & \multicolumn{1}{c}{\em{Weight}} & & \multicolumn{1}{c}{\em{Units}} & & \multicolumn{1}{c}{\em{Avail.}} & \multicolumn{1}{l}{\em{Description}}\endhead")
        f.write(r"\toprule")
        f.write('\n')
        for n in names:
            if n in semiGoods:
                pass
            else:
                f.write(display(n,latexOutputSkeleton,evaluatedRecipes[n]))
                f.write(r"\\")
                f.write("\n")
                if names.index(n) == len(names) - 1:
                    pass
                else:
                    f.write(r"\midrule")
                f.write("\n")
        f.write(r"\bottomrule")
        f.write(r"\end{longtable}")



        f.write(r"\end{document}")
    with open("Prices.html","w") as f:
        f.write(r"<!DOCTYPE html>")
        f.write(r"<head><title>Prices</title></head>")
        f.write(r"<body><h1>Prices at " + town + r"</h1>")
        f.write(r"<p>Number of recipes: " + str(len(names)) + "</p>")
        f.write(r"<table border = \"1\">")
        f.write("</td><td>".join(["<tr><td>Name","Price","Weight","","Num","Units","Num. Avail.","Description</td></tr>"]))
        for n in names:
            if n in semiGoods:
                pass
            else:
                f.write(display(n,htmlOutputSkeleton,evaluatedRecipes[n]))
                f.write("\n")
        f.write(r"</table>")


        
if __name__ == "__main__":
    main()
