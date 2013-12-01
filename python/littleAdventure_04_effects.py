# part of http://ThePythonGameBook.com
# (c) 2013 by Horst JENS ( horst.jens@spielend-programmieren.at )
# license: gpl3, see http://www.gnu.org/copyleft/gpl.html
# written for python3
# little adventure game with different rooms
# you can walk between the rooms
# changes:
# pick up and drop items, inspect inventory
# STATUS: does not work
# TODO: 
# * ab action weitermachen
# * game unnötig machen?
# * user-interface von player klasse sauberer trennen

import random

class Game(object):
    """
    holds all information for a game. Later it may be
    possible to load / save different games
    """
    number = 0

    def __init__(self):
        self.number = Game.number
        Game.number += 1
        self.rooms = {} # dictionary of rooms, key is room number
        self.items = {} # dictionary of items, key is item number
        self.monsters = {} # dictionary of monsters, key is monster number
        self.players = {} # dictionary of players, key is player number
        self.effects = {} # dictionary of effects (for items), key is effect name



class Monster(object):
    number = 1 # number 1 should be reserved for player

    def __init__(self, game, where= 0, adjective="", description="",
         boss=False, carrier=False):
        self.number = Monster.number
        Monster.number += 1
        game.monsters[self.number] = self # add monster into game dict
        self.adjective = adjective
        self.location = where # room number
        self.description = description
        self.hitpoints = random.randint(5,15)
        self.player = False
        self.carrier = carrier # can carry items ?
        if description == "":
            if boss:
                self.adjective = random.choice((" deadly"," dangerous",
                        " creepy"," ugly"," killer"))
                self.description = random.choice(("Unicorn","Cat",
                        "Teddy Bear","Hamster","Rabbit"))
                self.hitpoints *= 5
            else:
                self.description = random.choice(("goblin","ork","troll",
                    "mice","rat","dwarf","cave drake"))

    def info(self):
        txt = "Monster number {}: {} {} with {} hitpoints\n".format(
            self.number, self.adjective, self.description, self.hitpoints)
        if self.carrier:
            txt += "This monster can carry items\n"
        return txt


class Player(Monster):
    playernumber = 1
    def __init__(self, game, where=0, name="hero"):
        """need game instance. primary key is the unique player number.
        later it may be possible to make a (turn-based?) multi player
        game
        The player should be the first monster instance and thus always
        having Monsters.number 0
        """
        Monster.__init__(self, game, where, carrier = True)
        self.playernumber = Player.number  # note that the player has also a Monster.number
        Player.playernumber += 1
        game.players[self.playernumber] = self
        self.name = name
        self.player = True
        self.description = "player" # overwrite monster
        self.adjective = "human"                     # overwrite monster
        #self.inventory = [] # list of itemnumbers (player carry items)
        self.maxcarry = 100 # kg
        self.carry = 0 # current mass of all carried items in kg
        #self.loaction = where # start room number

    def show_inventory(self, game):
        txt = ""
        txt += "\n==== Your inventory ====\n"
        txt += "number, description, mass (kg)\n"
        txt += "-------------------------\n"
        for itemnumber in game.items:
            if game.items[itemnumber] == self.number * -1: # my negative monster number
                txt+="{}...{}...{}\n".format(itemnumber,
                      game.items[i].description, gamme.items[i].mass)
        
        txt += "You're currently carrying {} kg, that is {:.2f}% of your capacity".format(
            self.carry, (self.carry / self.maxcarry)*100)
        return txt  

    def list_items(self, game):
        """returns list of itemnumber
        of the items in the inventory of the player"""
        txt = ""
        items = []
        for itemnumber in game.items:
            if game.items[itemnumber].location == self.number * -1: # negative monster number
               items.append(itemnumber)
               #txt += game.items[itemnumber].description
        return items

    def pickup_item(self, game):
        txt, items = game.rooms[self.location].list_items()
        if len(items) >0:
            output("please select item number to pick up\n")
            output(txt)
            i = select_number(items)
            m = game.items[i].mass 
            if m > self.maxcarry:
                return "You fail to pick up this item. Reason: You can only carry {} kg. \n and try to pick up {} kg. Become stronger and try again!".format(m, self.maxcarry)
            elif m + self.carry > self.maxcarry:
                return "You fail to pick up this item. Reason: You already carry {} kg. Picking up {} would exceed your max. carry capacity of {} kg. Drop some items first or become stronger!".format(self.carry, m, self.maxcarry)
            else:
                game.items[i].location = -1 * self.number # negative monster number
                self.carry += m
            
        else: 
            return "this room has no items so there is nothing to pick up\n"

    def drop_item(self, game):
        items = self.list_items(game)
        if len(items)>0:
            output(self.show_inventory(game))
            output("select itemnumber to drop\n")
            i = select_number(items)
            game.items[i].location = self.location # drop item in my room
            self.carry -= game.items[i].mass  # update player
            return "you drop the {} to the floor\n".format(game.items[i].description)
        else:
            return "you carry no items so you can drop nothing\n"           
            
   
    def use_item(game, player):
        items = self.list_items(game)
        if len(items)>0:
            output(self.show_inventory(game))
            output("select itemnumber to use\n")
            i = select_number(items)
            if game.items[i].effect == None:
                return "this item has no effect"
            return game.items[i].effect.action()
        else:
            return "you carry no items so you can use nothing"

        
class Item(object):
    number = 0

    def __init__(self, game, where=0, description="", mass=-1):
        """need game instance. primary key of all items is the unique
        item number, so that you can have several items with the same
        name"""
        self.number = Item.number
        Item.number += 1
        game.items[self.number] = self # add item into game dict
        self.effect = None
        self.location = where # positive values are room number,
                              # negative values refer to monster(!) number
        self.description=description
        if mass == -1:
            self.mass = round(random.randint(1,50))
        else:
            self.mass = mass
        if self.description == "":
            self.description = random.choice(("helmet","chestplate","pants",
                    "shoes","potion of instant healing","potion of strenght",
                    "potion of speed","potion of regeneration","gold","sword",
                    "bow","arrows","shield","teleport pill"))
        if self.description == "teleport pill":
            self.effect = "teleport"


    def info(self, game):
        txt =  "Item Number {}: ".format(self.number)
        txt += self.description + "\n"
        #if self.location >= 0:
        #   #txt +="\n current location: room {}, {}".format(self.location, game.rooms[self.location].description) 
        #else:
        #    txt += "\n currently carried by {}".format(game.monsters[self.location*-1].description)
        #return txt



class Effect(object):
    def __init__(self, game, effectname, description="", victim=0, 
                 arg1=0, arg2=0):
        #victim 0 means the effect is targeted at the player (monsternumber 0)
        self.effectname = effectname
        self.description = description
        self.victim = victim # if the effect is aimed at somebody
        #self.roomnumber=roomnunmber # if the effect is in a certain room only
        self.arg1 = arg1  # reserve
        self.arg2 = arg2  # reserve
        game.effects[self.effectname] = self
        
    def action(self, game):
        txt = "null effect"
        if self.effectname == "teleport":
            while True:
                target = random.choice(game.rooms)
                if target != 0:  # anywhere but the void room
                    break
            game.monster[self.victim].location = target
            txt = "the teleport effect works ! You are trasported by magic into room number {}".format(target)
        return txt
           

class Room(object):
    number = 0

    def __init__(self, game, description="", connections=[],
                 explored=False, itemchances=[0.5,0.25,0.1],
                 monsterchances=[0.3,0.2,0.1,0.05],
                 bosschances=[0.0], effect = None ):
        """need game instance"""
        self.number = Room.number # void room has number 0
        game.rooms[self.number] = self # add room into game dict
        Room.number += 1
        self.explored = explored # True or False
        self.description = description
        self.connections = connections
        self.itemchances = itemchances
        self.monsterchances = monsterchances
        self.bosschances = bosschances
        self.effect = effect
        # create items
        for chance in self.itemchances:  
            if random.random()< chance:
                newItem = Item(game, self.number) # create item in this room

        # create monsters
        for chance in self.monsterchances:
            if random.random() < chance:
                newMonster = Monster(game, self.number) # create monster in this room
        # create boss(es)
        for chance in self.bosschances:
            if random.random() < chance:
                newMonster = Monster(game, self.number, boss=True)


    def list_items(self, game):
        """return string with itemnumbers and item description 
        as well as list of itemnumbers"""
        txt = "items in this room:\n"
        items = []
        for itemnumber in game.items:
            if game.items[itemnumber].location == self.number:
                txt +=  "{}....{}\n".format(itemnumber, 
                     game.items[itemnumber].description)
                items.append(itemnumber)
        return txt, items

    def info(self, game):
        """return string with all information about this room"""
        txt = "Room number {}: ".format(self.number)
        txt += self.description + "\n"
        # itmes ?
        txt2 = ""
        itemcounter = 0
        for itemnumber in game.items:
            if game.items[itemnumber].location == self.number:
                itemcounter += 1
                txt2 +=  game.items[itemnumber].description + "\n"
        if itemcounter > 0:
            txt += "You see {} itmes here: \n".format(itemcounter) + txt2
        else:
            txt += "This room has no items\n"
        # monsters ?
        for monsternumber in monsters:
            monstercounter = 0
            txt2 = ""
            if game.monsters[monsternumber].location == self.number:
                if not game.monsters[monsternumber].player:
                    monstercounter +=1
                    txt2 += game.monsters[m].info() 
            if monstercounter > 0:
                txt +="You see {} monster(s) here:\n".format(monstercounter)
                txt += txt2
            else:
                txt += "No monsters in this room, fortunately.\n"
        # doors
        txt += "You see {} door(s).\n".format(len(self.connections))
        #txt += "\n"
        return txt

# this function use print, replace later with gui commands
def output(txt):
    """can be later replaced by gui or graphical output"""
    print(txt)

def select_number(list_of_numbers):
        """The player select *one* number of a list of numbers"""
        answer = ""
        while ((not answer.isdecimal()) or int(answer) not in list_of_numbers):
                answer=input("Please type selected number and press ENTER: ")
        return int(answer)

      

# this funciton use input, replace later with gui command
def nextAction(game, player):
    """ask the user to select only one of many options"""
    output("What do you want to do today ?")
    connections = game.rooms[player.where].connections
    names = [] # temp list of room names
    for c in connections:
        if game.rooms[c].explored:
            names.append(game.rooms[c].description)
        else:
            names.append("unknown room")
    output("0.........other actions")
    for d in enumerate(names, 1): # make list of tuples, start with 1
        output("{}.........{}".format(d[0], d[1]))
    #answer = ""
    #while ((not answer.isdecimal()) or (int(answer) < 0) or
    #       (int(answer) > len(connections))):
    #    answer = input("please type number and press ENTER:>")
    answer = select_number(range(len(names)+1))
    if answer != 0:
       return connections[int(answer)-1] # return new room number
    # other menu options, player remain in same room
    output("")
    output("What do you want to do today?")
    actions = {"d":"drop item",
               "i":"inspect inventory",
               "p":"pick up item",
               "u":"use item",
               "c":"cancel"}
    for a in actions:
        output("{}....{}".format(a, actions[a]))
    answer = ""
    while answer not in actions:
        answer = input("please type selected letter and press ENTER: ")
    if answer == "i":
        show_inventory(game, player)
    elif answer == "d":
        drop_item(game, player)
    elif answer == "p":
        pickup_item(game, player)
    elif answer == "u":
        use_item(game, player)
    return player.where # return the same room number



# create a game instance
g = Game()

# add rooms with  description and connections.
# Each room will have a unique number and add himself to game
# room number 0 .... void, game over, lowest possible room number
Room(g,"end of the world (game over)", [], explored=True)
# room number 1 .... starting lobby
Room(g,"starting lobby", [1, 4], explored = True)

Room(g,"first room", [0,2,6])
# room number 2
Room(g,"storage room", [1,5,7])
# room number 3
# the boss room has 1 to 6 minions and 1 to 3 bosses
Room(g,"boss chamber", [6], monsterchances=[1.0,0.9,0.8,0.5,0.5,0.5],
     bosschances = [1.0,0.15,0.05])
# room number 4

# room number 5
Room(g,"npc room", [2,9,10])
# room number 6
Room(g,"gear room", [1,3,10])
# room number 7
Room(g,"trader", [2,5,8])
# room number 8
Room(g,"enemy room", [3,7], monsterchances=[1.0,1.0,1.0,0.9,0.7,0.5,0.2])
# room number 9
Room(g,"empty room", [5,12], itemchances=[])
# room number 10
Room(g,"mini boss",  [5,6], monsterchances=[1.0,0.5,0.5,0.5], bosschances = [0.5])
# room number 11
Room(g,"random room", [10,12])
#room number 12
Room(g,"random room", [11,9])
# items
i=Item(g,"potion of instant healing",mass=0.25)
g.rooms[6].itemnumbers.append(i.number) # puts item i in room 6
# you can use another item for i
i=Item(g,"wheel of cheese",mass=0.50)
g.rooms[2].itemnumbers.append(i.number)
# add effects
e = Effect(g,"teleport",teleport=1)
e.description = "You wake up in a strange room"

# start player in lobby (room 0)
# where = 0 # the actual room number
p = Player(g, where=0) # create player in room 0

# main loop
while len(g.rooms[p.where].connections) > 0:
    if not g.rooms[p.where].explored:
        output("You explore a new room!")
        g.rooms[p.where].explored = True # explore this room
    output("\n\nYou are now here:\n\n{}".format(g.rooms[p.where].info(g)))
    p.where = nextAction(g, p)
    output("\n"*1)
output("\n"*1)
output("Thank you for playing. Have a nice real life")
