from tkinter import *
from PIL import Image, ImageTk
from random import choice,randint,random
from math import sqrt,cos,sin,pi,atan,floor
from threading import Timer,stack_size
from copy import deepcopy
import gc

## Game constants
gameSize = 50
framerate = 60
BOARD_SIZE = 12*gameSize

## Player stats
PLAYER_SIZE = gameSize*0.25
PLAYER_SPEED = 7
PLAYER_HEALTH = 100
PLAYER_BASE_REGEN = 2 #par seconde

## Enemy stats
CLASSIC_ENEMY_HEALTH = 80
CLASSIC_ENEMY_SPEED = 2.5
CLASSIC_ENEMY_REACH = gameSize*3
CLASSIC_ENEMY_SIZE = gameSize*0.3
CLASSIC_WEIGHT = 20

TANK_ENEMY_HEALTH = 220
TANK_ENEMY_SPEED = 2
TANK_ENEMY_REACH = gameSize*0.8
TANK_ENEMY_SIZE = gameSize*0.35
TANK_WEIGHT = 25

MAGE_ENEMY_HEALTH = 60
MAGE_ENEMY_SPEED = 1.8
MAGE_ENEMY_REACH = gameSize*7.5
MAGE_ENEMY_SIZE = gameSize*0.28
MAGE_WEIGHT = 30

## Player weapons stats
SINGLE_DAMAGE = 100
SINGLE_SPEED = 2
SINGLE_LIFESPAN = 40
SINGLE_AMOUNT = 1
SINGLE_ARC = 0
SINGLE_PROJ_SIZE = 0.2
SINGLE_PROJ_SPEED = 6
SINGLE_GUIDING_FACTOR = 0

## Enemy weapons stats
CLASSIC_WEAPON_DAMAGE = 6
CLASSIC_WEAPON_SPEED = 1
CLASSIC_WEAPON_LIFESPAN = 40
CLASSIC_WEAPON_AMOUNT = 1
CLASSIC_WEAPON_ARC = 0
CLASSIC_WEAPON_PROJ_SIZE = 0.17
CLASSIC_WEAPON_PROJ_SPEED = 5
CLASSIC_WEAPON_GUIDING_FACTOR = 0

TANK_WEAPON_DAMAGE = 8
TANK_WEAPON_SPEED = 0.8
TANK_WEAPON_LIFESPAN = 30
TANK_WEAPON_AMOUNT = 1
TANK_WEAPON_ARC = 0
TANK_WEAPON_PROJ_SIZE = 0.2
TANK_WEAPON_PROJ_SPEED = 20
TANK_WEAPON_GUIDING_FACTOR = 0

MAGE_WEAPON_DAMAGE = 10
MAGE_WEAPON_SPEED = 0.8
MAGE_WEAPON_LIFESPAN = 90
MAGE_WEAPON_AMOUNT = 3
MAGE_WEAPON_ARC = 20
MAGE_WEAPON_PROJ_SIZE = 0.2
MAGE_WEAPON_PROJ_SPEED = 8
MAGE_WEAPON_GUIDING_FACTOR = 0
## Game variables
gameStopped = False
frames = 0
wave = 0
waveWeight = 100
waveOver = True
nbUpgradesShown = 3

hpMult = 1
dmgMult = 1
spdMult = 1
firingSpeedMult = 1
lifespanMult = 1
projSpeedMult = 1
projSizeMult = 1
guidingMult = 1

playerHpMult = 1
playerDmgMult = 1
playerSpeedMult = 1
playerProjSpeedMult = 1
playerFiringSpeedMult = 1
playerLifespanMult = 1
playerProjectilesBonus = 0
playerProjectilesMult = 1
playerArcMult = 1
playerArcBonus = 0
playerGuidingMult = 1
playerGuidingBonus = 0
playerProjSizeMult = 1
playerRegenMult = 1



## Useful lists
enemies = []
player_projectiles = []
enemy_projectiles = []
upgrade_items = []

upgrades_list = ["Placeholder","HP1","Dmg1","PlusOneProjectile","DoubleProjectiles","FiringSpeed","PlayerSpeed","Guiding","Regen","UpgradeSlots1","UpgradeSlots2","UpgradeSlots3"]
common_upgrades_list = ["HP1","Regen","PlayerSpeed"]
rare_upgrades_list = ["FiringSpeed","Dmg1"]
epic_upgrades_list = ["Guiding"]
legendary_upgrades_list = ["PlusOneProjectile"]
one_time_upgrades_list = ["DoubleProjectiles","UpgradeSlots1","UpgradeSlots2","UpgradeSlots3"]

temp_common_upgrades = []
temp_rare_upgrades = []
temp_epic_upgrades = []
temp_legendary_upgrades = []

current_upgrades_shown = []

def entities_dist(ent1,ent2):
    return sqrt((ent1.x-ent2.x)**2+(ent1.y-ent2.y)**2)

def stats_for_class(weaponType):
    """Renvoie (Attaque, Vitesse -Tirs /s-, Durée -frames-, Nombre de projectiles, Arc de tir, Taille de projectile -selon gameSize-, Vitesse proj -px /frame-, Guidage -de 0 à 100-) """
    if weaponType == "SINGLE":
        return (SINGLE_DAMAGE, SINGLE_SPEED, SINGLE_LIFESPAN, SINGLE_AMOUNT, SINGLE_ARC, SINGLE_PROJ_SIZE, SINGLE_PROJ_SPEED, SINGLE_GUIDING_FACTOR)
    if weaponType == "CLASSIC_ENEMY":
        return (CLASSIC_WEAPON_DAMAGE*dmgMult, firingSpeedMult*CLASSIC_WEAPON_SPEED, CLASSIC_WEAPON_LIFESPAN, CLASSIC_WEAPON_AMOUNT, CLASSIC_WEAPON_ARC, projSizeMult*CLASSIC_WEAPON_PROJ_SIZE, CLASSIC_WEAPON_PROJ_SPEED*projSpeedMult, CLASSIC_WEAPON_GUIDING_FACTOR)
    if weaponType == "TANK_ENEMY":
        return (TANK_WEAPON_DAMAGE*dmgMult, firingSpeedMult*TANK_WEAPON_SPEED, TANK_WEAPON_LIFESPAN, TANK_WEAPON_AMOUNT, TANK_WEAPON_ARC, projSizeMult*TANK_WEAPON_PROJ_SIZE, TANK_WEAPON_PROJ_SPEED*projSpeedMult, TANK_WEAPON_GUIDING_FACTOR)
    if weaponType == "MAGE_ENEMY":
        return (MAGE_WEAPON_DAMAGE*dmgMult, firingSpeedMult*MAGE_WEAPON_SPEED, MAGE_WEAPON_LIFESPAN, MAGE_WEAPON_AMOUNT, MAGE_WEAPON_ARC, projSizeMult*MAGE_WEAPON_PROJ_SIZE, MAGE_WEAPON_PROJ_SPEED*projSpeedMult, MAGE_WEAPON_GUIDING_FACTOR)

class Projectile:
    def __init__(self, x, y, speedVector, dmg, lifespan, size, guiding, isEnemy):
        self.x = x
        self.y = y
        self.speed_x, self.speed_y = speedVector
        self.dmg = dmg
        self.lifespan = lifespan
        self.size = gameSize*size/2
        self.guiding = guiding
        self.shape = can.create_oval(self.x-self.size,self.y-self.size,self.x+self.size,self.y+self.size, fill="orange")
        self.isEnemy = isEnemy
        self.gone = False

    def destroy(self):
        if not  self.gone:
            self.gone = True
            can.delete(self.shape)
            if self.isEnemy:
                enemy_projectiles.remove(self)
            else:
                player_projectiles.remove(self)

    def enemy_collision(self):
        for e in enemies:
            if entities_dist(self,e) <= self.size + e.size:
                e.damage(self.dmg)
                self.destroy()
                break

    def player_collision(self):
        if entities_dist(self,player) <= self.size + PLAYER_SIZE:
            player.damage(self.dmg)
            self.destroy()

    def find_closest_enemy(self):
        min_dist = 2*BOARD_SIZE
        min_ent = None
        for e in enemies:
            d = entities_dist(e,self)
            if d < min_dist:
                min_dist = d
                min_ent = e
        return e

    def move(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            can.delete(self.shape)
            self.destroy()

        guiding_x, guiding_y = 0,0
        if self.guiding != 0 and not self.isEnemy:
            e = self.find_closest_enemy()
            dist = entities_dist(e,self)
            guiding_power = 0
            guiding_x = (self.guiding+playerGuidingBonus)*playerGuidingMult*(e.x-self.x)/(dist**1.7*10)
            guiding_y = (self.guiding+playerGuidingBonus)*playerGuidingMult*(e.y-self.y)/(dist**1.7*10)

        self.speed_x += guiding_x
        self.speed_y += guiding_y
        dx = self.speed_x
        dy = self.speed_y
        self.x += dx
        self.y += dy
        can.move(self.shape,dx,dy)
        if self.isEnemy:
            self.player_collision()
        else:
            self.enemy_collision()

## Flambeau class
class Flambeau:
    def __init__(self,weaponType,holder, player=False):
        self.weaponType = weaponType
        self.atk, self.speed, self.lifespan, self.nbProj, self.arc, self.projSize, self.projSpeed, self.projGuiding = stats_for_class(weaponType)
        self.arc = self.arc*pi/180
        self.holder = holder
        self.isPlayer = player
        if self.isPlayer:
            self.shape = can.create_oval(self.holder.x-gameSize*0.1,self.holder.y-gameSize*0.1,self.holder.x+gameSize*0.1,self.holder.y+gameSize*0.1, fill="orange")
        self.canFire = True

    def reload(self):
        self.canFire = True

    def fire(self,aim_x,aim_y):
        if self.canFire:
            dist = sqrt((aim_x-self.holder.x)**2 + (aim_y-self.holder.y)**2)
            cos_ = (aim_x - self.holder.x)/dist
            sin_ = (aim_y - self.holder.y)/dist
            if cos_ > 0:
                angle = atan(sin_/cos_)
            elif cos_ < 0:
                angle = pi + atan(sin_/cos_)
            elif cos_==0 and sin_>0:
                angle = pi/2
            else:
                angle = 3*pi/2

            if self.weaponType == "SINGLE":
                nProj = (self.nbProj+playerProjectilesBonus)*playerProjectilesMult
                for i in range(nProj):
                    firingAngle = angle+(i/nProj-0.5)*(self.arc+playerArcBonus)*playerArcMult
                    vect = (cos(firingAngle)*self.projSpeed*playerProjSpeedMult, sin(firingAngle)*self.projSpeed*playerProjSpeedMult)
                    p = Projectile(self.holder.x, self.holder.y, vect, self.atk*playerDmgMult, self.lifespan*playerLifespanMult, self.projSize*playerProjSizeMult, self.projGuiding*playerGuidingMult, False)
                    player_projectiles.append(p)
            elif self.weaponType in ["CLASSIC_ENEMY","TANK_ENEMY","MAGE_ENEMY"]:
                for _ in range(self.nbProj):
                    firingAngle = angle+(random()-0.5)*self.arc
                    vect = (cos(firingAngle)*self.projSpeed*projSpeedMult, sin(firingAngle)*self.projSpeed*projSpeedMult)
                    p = Projectile(self.holder.x, self.holder.y, vect, self.atk*dmgMult, self.lifespan*lifespanMult, self.projSize*projSizeMult, self.projGuiding*guidingMult, True)
                    enemy_projectiles.append(p)

            self.canFire = False
            if self.isPlayer:
                Timer(1/(self.speed*playerFiringSpeedMult), self.reload).start()
            else:
                Timer(1/(self.speed*firingSpeedMult), self.reload).start()

## Player class
class Player:
    def __init__(self,health,color,flambeau,x,y, speed=5):
        self.health = health
        self.maxHp = health
        self.baseMaxHp = health
        self.x = x
        self.y = y
        self.shape = can.create_oval(self.x-PLAYER_SIZE,self.y-PLAYER_SIZE,self.x+PLAYER_SIZE,self.y+PLAYER_SIZE, fill=color)
        self.baseSpeed = speed
        self.canMove = False
        self.firing = False
        self.targetX = 500
        self.targetY = 350
        self.flambeau = Flambeau("SINGLE",self, True)


    def update_target(self, event):
        self.targetX,self.targetY = (event.x,event.y)

    def is_moving(self):
        self.canMove = True

    def stop_moving(self, event):
        self.canMove = False

    def is_firing(self, event):
        self.firing = True

    def stop_firing(self, event):
        self.firing = False

    def move(self):
        if self.canMove:
            dist2target = sqrt((self.targetX-self.x)**2+(self.targetY-self.y)**2)
            dx = (self.targetX - self.x)/dist2target*self.baseSpeed
            dy = (self.targetY - self.y)/dist2target*self.baseSpeed
            self.x += dx
            self.y += dy
            can.move(self.shape,dx,dy)
            can.move(self.flambeau.shape,dx,dy)

    def fire(self):
        if self.flambeau.canFire and self.firing:
            self.flambeau.fire(self.targetX,self.targetY)

    def damage(self, dmg):
        self.health -= dmg
        can.coords(hpDisplay, (0.5-0.2*self.health/PLAYER_HEALTH)*BOARD_SIZE,0.98*BOARD_SIZE,(0.5+0.2*self.health/PLAYER_HEALTH)*BOARD_SIZE,BOARD_SIZE)
        if self.health <= 0:
            self.die()
            pass

    def update_max_hp(self):
        self.maxHp = self.baseMaxHp*playerHpMult

    def regen(self, amount):
        self.health += min(amount,self.maxHp-self.health)
        can.coords(hpDisplay, (0.5-0.2*self.health/PLAYER_HEALTH)*BOARD_SIZE,0.98*BOARD_SIZE,(0.5+0.2*self.health/PLAYER_HEALTH)*BOARD_SIZE,BOARD_SIZE)

    def die(self):
        global gameStopped
        gameStopped = True
        can.create_text(0.5*BOARD_SIZE,0.5*BOARD_SIZE, text="YOU LOST", font=("Helvetica",80), fill="red2")

## Enemy classes
class Enemy:
    def damage(self, dmg):
        self.health -= dmg
        can.coords(self.healthBar, self.x-self.size*self.health/self.maxHp,self.y-self.size-0.006*BOARD_SIZE,self.x+self.size*self.health/self.maxHp,self.y-self.size-0.001*BOARD_SIZE)
        if self.health <= 0:
            self.die()
            pass

    def die(self):
        global waveOver
        can.delete(self.shape)
        can.delete(self.healthBar)
        enemies.remove(self)
        if enemies == []:
            waveOver = True


class ClassicEnemy(Enemy):
    def __init__(self,health,color,x,y):
        self.health = health
        self.maxHp = health
        self.x = x
        self.y = y
        self.size = CLASSIC_ENEMY_SIZE
        self.shape = can.create_oval(self.x-self.size,self.y-self.size,self.x+self.size,self.y+self.size, fill=color)
        self.healthBar = can.create_rectangle(self.x-self.size,self.y-self.size-0.006*BOARD_SIZE,self.x+self.size,self.y-self.size-0.001*BOARD_SIZE, fill="lime")
        self.baseSpeed = CLASSIC_ENEMY_SPEED * spdMult
        self.reach = CLASSIC_ENEMY_REACH
        self.flambeau = Flambeau("CLASSIC_ENEMY",self)

    def move(self):
        dist2target = entities_dist(self,player)
        if dist2target >= self.reach:
            dx = (player.x - self.x)/dist2target*self.baseSpeed
            dy = (player.y - self.y)/dist2target*self.baseSpeed
            self.x += dx
            self.y += dy
            can.move(self.shape,dx,dy)
            can.move(self.healthBar,dx,dy)

    def fire(self):
        if entities_dist(player,self) <= self.reach:
            self.flambeau.fire(player.x,player.y)


class TankEnemy(ClassicEnemy):
    def __init__(self,health,color,x,y):
        self.health = health
        self.maxHp = health
        self.x = x
        self.y = y
        self.size = TANK_ENEMY_SIZE
        self.shape = can.create_rectangle(self.x-self.size,self.y-self.size,self.x+self.size,self.y+self.size, fill=color)
        self.healthBar = can.create_rectangle(self.x-self.size,self.y-self.size-0.006*BOARD_SIZE,self.x+self.size,self.y-self.size-0.001*BOARD_SIZE, fill="lime")
        self.baseSpeed = TANK_ENEMY_SPEED * spdMult
        self.reach = TANK_ENEMY_REACH
        self.flambeau = Flambeau("TANK_ENEMY",self)

class MageEnemy(ClassicEnemy):
    def __init__(self,health,color,x,y):
        self.health = health
        self.maxHp = health
        self.x = x
        self.y = y
        self.size = MAGE_ENEMY_SIZE
        self.shape = can.create_oval(self.x-self.size,self.y-self.size,self.x+self.size,self.y+self.size, fill=color)
        self.healthBar = can.create_rectangle(self.x-self.size,self.y-self.size-0.006*BOARD_SIZE,self.x+self.size,self.y-self.size-0.001*BOARD_SIZE, fill="lime")
        self.baseSpeed = MAGE_ENEMY_SPEED * spdMult
        self.reach = MAGE_ENEMY_REACH
        self.flambeau = Flambeau("MAGE_ENEMY",self)


## Ranged
## Boss ?

def upgrade_picker(n, luck):
    global temp_common_upgrades, temp_rare_upgrades, temp_epic_upgrades, temp_legendary_upgrades
    picked = []
    for _ in range(n):
        u = None
        while u == None:
            print("loop cycle !")
            r = randint(1,100)
            if r<=50:
                if one_time_upgrades_list != []:
                    u = choice(one_time_upgrades_list)
                    one_time_upgrades_list.remove(u)
            elif r<=7:
                if temp_legendary_upgrades != []:
                    u = choice(temp_legendary_upgrades)
                    temp_legendary_upgrades.remove(u)
            elif r<=15:
                if temp_epic_upgrades != []:
                    u = choice(temp_epic_upgrades)
                    temp_epic_upgrades.remove(u)
            elif r<=40:
                if temp_rare_upgrades != []:
                    u = choice(temp_rare_upgrades)
                    temp_rare_upgrades.remove(u)
            else:
                if temp_common_upgrades != []:
                    u = choice(temp_common_upgrades)
                    temp_common_upgrades.remove(u)
        picked.append(u)
    return picked

def upgrade_tooltips(upgrade):
    if upgrade == "Placeholder":
        return ""
    elif upgrade == "HP1":
        return "+10% PV Max"
    elif upgrade == "Dmg1":
        return "+8% Dégâts"
    elif upgrade == "PlusOneProjectile":
        return "\n+1 Projectile\n-10% dégâts"
    elif upgrade == "DoubleProjectiles":
        return "\n\nx2 Projectiles\n-30% Vitesse tir\n-20% dégâts"
    elif upgrade == "FiringSpeed":
        return "+8% Vitesse de tir"
    elif upgrade == "PlayerSpeed":
        return "+15% Vitesse"
    elif upgrade == "Guiding":
        return "Projectiles guidés"
    elif upgrade == "Regen":
        return "+20% Regenération"
    elif upgrade[:-1] == "UpgradeSlots":
        return "+1 Choix d'amélioration"

def show_upgrade_screen():
    global gameStopped, temp_common_upgrades, temp_rare_upgrades, temp_epic_upgrades, temp_legendary_upgrades

    gameStopped = True
    listPos = [(0.5*BOARD_SIZE+0.3*BOARD_SIZE*cos(pi/2+i*2*pi/nbUpgradesShown),0.5*BOARD_SIZE-0.3*BOARD_SIZE*sin(pi/2+i*2*pi/nbUpgradesShown)) for i in range(nbUpgradesShown)]

    temp_common_upgrades = deepcopy(common_upgrades_list)
    temp_rare_upgrades = deepcopy(rare_upgrades_list)
    temp_epic_upgrades = deepcopy(epic_upgrades_list)
    temp_legendary_upgrades = deepcopy(legendary_upgrades_list)

    upgrades_list = upgrade_picker(nbUpgradesShown, 1)

    for i in range(nbUpgradesShown):
        r = can.create_rectangle(listPos[i][0]-0.06*BOARD_SIZE,listPos[i][1]-0.06*BOARD_SIZE,listPos[i][0]+0.06*BOARD_SIZE,listPos[i][1]+0.06*BOARD_SIZE, fill="white", width=3)
        im = can.create_image(listPos[i][0], listPos[i][1], image=upgrade_images[upgrades_list[i]])
        t = can.create_text(listPos[i][0],listPos[i][1]+0.08*BOARD_SIZE, text=upgrade_tooltips(upgrades_list[i]))

        upgrade_items.append(r)
        upgrade_items.append(im)
        upgrade_items.append(t)

        current_upgrades_shown.append(upgrades_list[i])



def select_upgrade(upgrade):
    global current_upgrades_shown,gameStopped,playerHpMult,playerDmgMult,playerSpeedMult,playerProjSpeedMult,playerFiringSpeedMult,playerProjectilesBonus,playerProjectilesMult,playerMultProjectiles,playerArcMult,playerArcBonus,playerGuidingMult,playerGuidingBonus,playerProjSizeMult,playerRegenMult, nbUpgradesShown

    current_upgrades_shown = []
    for item in upgrade_items:
        can.delete(item)

    if upgrade == "Placeholder":
        pass
    elif upgrade == "Dmg1":
        playerDmgMult *= 1.08
    elif upgrade == "HP1":
        playerHpMult *= 1.1
        player.update_max_hp()
        player.health = player.maxHp
    elif upgrade == "PlusOneProjectile":
        playerProjectilesBonus += 1
        playerArcBonus += 8 * (pi/180)
        playerFiringSpeedMult *= 0.9
    elif upgrade == "DoubleProjectiles":
        playerProjectilesMult = 2
        playerArcMult *= 1.8
        playerFiringSpeedMult *= 0.7
        playerDmgMult *= 0.8
    elif upgrade == "FiringSpeed":
        playerFiringSpeedMult *= 1.08
    elif upgrade == "PlayerSpeed":
        playerSpeedMult *= 1.15
    elif upgrade == "Guiding":
        playerGuidingBonus += 10
    elif upgrade == "Regen":
        playerRegenMult *= 1.20
    elif upgrade[:-1] == "UpgradeSlots":
        nbUpgradesShown += 1

    gameStopped = False

def spawn_coords(radius):
    randX, randY = player.x,player.y
    while sqrt((randX-player.x)**2+(randY-player.y)**2) < radius:
        randX = randint(0,BOARD_SIZE)
        randY = randint(0,BOARD_SIZE)
    return randX, randY

def spawn_wave(w):
    currentWeight = w
    while currentWeight >= 20:
        r = randint(1,100)
        if r<=20:
            x,y = spawn_coords(6*gameSize)
            e = MageEnemy(MAGE_ENEMY_HEALTH*hpMult, "gray70", x, y)
            enemies.append(e)
            currentWeight -= MAGE_WEIGHT
        elif r<=50:
            x,y = spawn_coords(3*gameSize)
            e = TankEnemy(TANK_ENEMY_HEALTH*hpMult, "gray30", x, y)
            enemies.append(e)
            currentWeight -= TANK_WEIGHT
        else:
            x,y = spawn_coords(4*gameSize)
            e = ClassicEnemy(CLASSIC_ENEMY_HEALTH*hpMult, "gray50", x, y)
            enemies.append(e)
            currentWeight -= CLASSIC_WEIGHT

def wave_handler():
    global wave,waveOver,waveWeight,hpMult,dmgMult,spdMult,projSpeedMult
    if waveOver:
        waveOver = False
        wave += 1
        can.itemconfig(waveDisplay, text="VAGUE "+str(wave))

        # if wave%2==1 and wave != 1:
        #     show_upgrade_screen()

        if wave != 0 and wave != 1:
            show_upgrade_screen()

        while gameStopped:
            pass

        if wave%5 == 0:
            hpMult *= 1.1
            dmgMult *= 1.1
        if wave%10 == 0:
            spdMult *= 1.05
            projSpeedMult *= 1.05
            waveWeight += 10

        spawn_wave(waveWeight)

def wait_for_game():
    if gameStopped:
        Timer(1/framerate, wait_for_game).start()
    else:
        frame_handler()

## Frame handler
def frame_handler():
    global frames
    frames += 1

    player.move()
    player.fire()
    if player.health < player.maxHp:
        player.regen(round(playerRegenMult*PLAYER_BASE_REGEN/framerate,2))
    for e in enemies:
        e.move()
        e.fire()

    for e_p in enemy_projectiles:
        e_p.move()
    for p_p in player_projectiles:
        p_p.move()

    wave_handler()

    if not gameStopped:
        Timer(1/framerate, frame_handler).start()
    else:
        wait_for_game()

def left_click_handler(event):
    if not gameStopped:
        player.is_moving()
    else:
        x,y = event.x,event.y
        listPos = [(0.5*BOARD_SIZE+0.3*BOARD_SIZE*cos(pi/2+i*2*pi/nbUpgradesShown),0.5*BOARD_SIZE-0.3*BOARD_SIZE*sin(pi/2+i*2*pi/nbUpgradesShown)) for i in range(nbUpgradesShown)]
        for i in range(len(listPos)):
            if (-0.06*BOARD_SIZE <= x-listPos[i][0] <= 0.06*BOARD_SIZE) and (-0.06*BOARD_SIZE <= y-listPos[i][1] <= 0.06*BOARD_SIZE):
                print(current_upgrades_shown[i])
                select_upgrade(current_upgrades_shown[i])



fen = Tk()
fen.title("Flambo !")

upgrade_images = {}

for u in upgrades_list:
    i = Image.open("Images/Upgrade"+u+".png")
    resized = i.resize((round(0.1*BOARD_SIZE),round(0.1*BOARD_SIZE)))
    upgrade_images[u] = ImageTk.PhotoImage(resized)

can = Canvas(fen, width=BOARD_SIZE, height=BOARD_SIZE, bg="MediumPurple1")
can.pack()

player = Player(PLAYER_HEALTH,"blue",0,4*gameSize,4*gameSize, PLAYER_SPEED)

waveDisplay = can.create_text(0.5*BOARD_SIZE,0.03*BOARD_SIZE,text="VAGUE 0", fill="black", font=("Helvetica",20))
hpDisplay = can.create_rectangle(0.3*BOARD_SIZE,0.98*BOARD_SIZE,0.7*BOARD_SIZE,BOARD_SIZE, fill="red", outline="red")

can.bind('<Motion>', player.update_target)
can.bind("<Button-1>", left_click_handler)
can.bind("<ButtonRelease-1>", player.stop_moving)
can.bind("<Button-3>", player.is_firing)
can.bind("<ButtonRelease-3>", player.stop_firing)


frame_handler()

fen.mainloop()