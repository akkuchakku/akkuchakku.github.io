import os, sys, math, random, time

# try:
#     os.system('py -m pip install --upgrade pip')
#     os.system('py -m pip install --upgrade pygame') #Windows

# except:
#     os.system('python3 -m pip install --upgrade pip')
#     os.system('python3 -m pip install -U pygame --user --upgrade') #Mac

import pygame
from pygame.locals import *
pygame.init()
pygame.mixer.init()

#variables

FPS = 60

xlimit, ylimit = 600, 500 #grid limit
xscreen, yscreen = 600, 500 #screen limit
interval = 100
subinterval = 50

screen = pygame.display.set_mode((xscreen, yscreen), pygame.RESIZABLE)
pygame.display.set_caption("Tower of Trials")

hfont = 'files/blackchancery.ttf' #header font
ifont = 'files/cmunbx.ttf' #icon font


#constants

player = ''
gameMode = ''
animation = 'On'
sounds = 'On'
powerScale = 1
sideText = ''

deathMsg = [
    'Oh no you lost :(', 'Try again!', 'Maybe try another hero.', 'Try to upgrade the right stats', 'Try a new tactic.'
    ]

winMsg = [
    'You have defeated the Evil Space Wizard!', 'You have reached the top of the tower!', 'You Won!'
    ]

fileStore = [eval(line) for line in open('files/fileStore.txt')]

infoStore = eval(open('files/infoStore.txt').read())
playerStore = eval(open('files/playerStore.txt').read())
sbStore = eval(open('files/scoreboard.txt').read()) #scoreboard
musicStore = [
    'sounds/forest.wav',
    'sounds/desert.wav',
    'sounds/ocean.wav',
    'sounds/ice.wav',
    'sounds/ruins.wav',
    'sounds/city.wav',
    'sounds/airship.wav',
    'sounds/castle.wav',
    'sounds/volcano.wav',
    'sounds/space.wav',
    'sounds/boss.wav'
    ]


playGame = False
background = ''

file = fileStore[0]

character = ['player', 'Knight', pygame.image.load('cards/knight.png'), 0, 0, 0, 0, pygame.image.load('misc/fire.png')]

#preload constant images
#highlights
hlOpt = pygame.image.load('misc/option.png')
hlMove = pygame.image.load('misc/move.png')
hlAtk = pygame.image.load('misc/attack.png')
hlAb = pygame.image.load('misc/ability.png')

#icons
ihealth = pygame.image.load('misc/health.png')
idamage = pygame.image.load('misc/damage.png')
ispeed = pygame.image.load('misc/speed.png')
idefence = pygame.image.load('misc/defence.png')

icoin = pygame.image.load('misc/coin.png')
ipause = pygame.image.load('misc/pause.png')

#other
menuScroll = pygame.image.load('misc/scroll.png')
rectButton = pygame.image.load('misc/button.png')
arrowButton = pygame.image.load('misc/arrow.png')
gridLine = pygame.image.load('misc/grid.png')

towerBg = pygame.image.load('bg/tower.jpg')

#sounds
clickSound = pygame.mixer.Sound('sounds/buttonclick.wav')
atkSound = pygame.mixer.Sound('sounds/attack.wav')
mvSound = pygame.mixer.Sound('sounds/move.wav')
ablSound = pygame.mixer.Sound('sounds/ability.wav')
portalSound = pygame.mixer.Sound('sounds/portal.wav')


#Classes
class card: #cards on the grid
    coins = 0
    
    def __init__(self, type='blank', name='blank', file='blank', hp=0, dmg=0, spd=0, dfc=0, projectile=''):
        self.type = type
        self.name = name
        try:
            self.file = pygame.image.load(file) #try to preload image
        except:
            self.file = file

        self.hp = int(hp)
        self.dmg = int(dmg)
        self.spd = int(spd)
        self.dfc = int(dfc)

        try:
            self.proj = pygame.image.load(projectile)
        except:
            self.proj = projectile

        self.maxhp = int(hp)


class gridSquare: #each square on the grid

    highlight = 'none'

    def __init__(self, pos, card):
        self.pos = pos #first number = x, second number = y
        self.sqrObj = card

#Functions

def playSound(SFX):
    if sounds == 'On':
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(SFX)
        pygame.mixer.music.unpause()

def playMusic(song):
    if sounds == 'On':
        pygame.mixer.music.stop()
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(-1)

def convertCoords(stringCoord): #convert grid position to actual coordinates

    #pos = position on grid, coord = pixel positioning on screen

    xpos, ypos = stringCoord[:2]
    xpos, ypos = int(xpos), int(ypos)

    xCoord, yCoord = (xpos*interval - interval), (ypos*interval - interval)
    xCoord += round((xscreen - xlimit)/2)
    yCoord += round((yscreen - ylimit)/2)

    return int(xCoord), int(yCoord)

def moveStep(start, end): #converts two coords into a series of Left/Right/Up/Down steps
    startx, starty = int(start[0]), int(start[1])
    endx, endy, = int(end[0]), int(end[1])

    string = ''

    if startx > endx: #Left
        string  = string + ( 'L' * abs(startx - endx))
    elif startx < endx: #Right
        string  = string + ( 'R' * abs(startx - endx))
    else: #no x movement
        pass

    if starty > endy: #Up
        string  = string + ( 'U' * abs(starty - endy))
    elif starty < endy: #Down
        string  = string + ( 'D' * abs(starty - endy))
    else: #no y movement
        pass

    return string

def bg(): #draw bg
    screen.fill ((0, 0, 0))
    screen.blit(pygame.transform.scale(pygame.image.load(background), (xscreen, yscreen)), (0, 0)) #background

def displayOption(): #highlight tiles within range when player is selected
    xpos, ypos = int(selectRec[0].pos[0]), int(selectRec[0].pos[1])

    newxpos, newypos = xpos - selectRec[0].sqrObj.spd, ypos - selectRec[0].sqrObj.spd

    for i in range(selectRec[0].sqrObj.spd * 2 + 1):
        editGrid(f'{newxpos}{ypos}', 'highlight', 'option')
        editGrid(f'{xpos}{newypos}', 'highlight', 'option')

        newxpos += 1
        newypos += 1


def resize(): #resize screen
    global xscreen, yscreen, xlimit, ylimit, interval, subinterval

    xscreen, yscreen = pygame.display.get_surface().get_size()
    xinterval, yinterval = round((xscreen)/6), round((yscreen)/5)
    
    if xinterval <= yinterval:
        interval = xinterval
    elif xinterval > yinterval:
        interval = yinterval
    subinterval = round(interval/2)
    xlimit, ylimit = interval*6, interval*5

def alpha(size, opacity, pos): #create a transparent rect
    rect = pygame.Surface(size)  # size
    rect.set_alpha(opacity)
    rect.fill((0,0,0)) # fill and set alpha
    screen.blit(rect, pos)

def write(text, fontType, fontSize, colour, pos, xshift, yshift, getRect=False): #write text. Text will be centre alligned.
    text = pygame.font.Font(fontType, fontSize).render(text, True, colour)
    rect = text.get_rect()
    xpos = pos[0]-round(rect[2]/2)+xshift
    ypos = pos[1]-round(rect[3]/2)+yshift
    screen.blit(text, (xpos, ypos))
    
    if getRect == True:
        return (xpos, ypos, rect[2], rect[3])
            

def blockPrint(coord, textList, colour, fontSize, fontType, xshift=0, yshift=0): #function that displays text on multiple lines
    #standard fontSize: round(interval/8)
    
    yshift += fontSize
    
    for line in textList:
        write(line, fontType, fontSize, colour, coord, xshift, yshift)
        yshift += fontSize

def cardFile(fileName): #open a level's respective file
    global background

    cardStore = []
    file = open(fileName)
    for line in file:
        stats = line.strip().split(':')
        if line.startswith('#') == False: # only add lines that do not start with '#'
            cardStore.append(stats)

    background = str(cardStore[0])[2:-2]
    cardStore = cardStore[1:]

    return cardStore

def drawCards(cardStore): #randomly draw cards for the level
    cardList = [
        character,
        ['portal', 'portal', pygame.image.load('cards/portal.png'), 0, 0, 0, 0, '']
        ] #always include player and exit portal

    #separate different types of cards
    enemyList = []
    specialList = []

    #sort items
    for item in cardStore:
        if item[0] == 'enemy':
            enemyList.append(item)  
        elif item[0] == 'special':
            specialList.append(item)
        elif item[0] == 'boss':
            cardList.append(item)


    for i in range(random.randint(3, 5)): # select enemies
        cardList.append(random.choice(enemyList))
    for i in range(random.randint(0, 1)): #select special cards
        cardList.append(random.choice(specialList))

    for i in range(25 - len(cardList)): #fill the rest of the list with blank cards
        cardList.append(['blank', 'blank', 'empty', 0, 0, 0, 0, ''])

    random.shuffle(cardList) #shuffle order of cards

    return cardList


def createGrid(file):
    if file == 'none':
        cardList = [['blank', 'blank', 'empty', 0, 0, 0, 0, ''] for i in range(25)] # blank card object (exists as a blank tile)
    else:
        cardList = drawCards(cardFile(file)) #open file, randomly draw cards

    #creating grid objects and assigning position
    assign = 11
    grid = []
    for item in cardList:
        if item[0] != 'player': #player's stats do not scale they have to be upgraded
            health = int(item[3])*powerScale #enemy stats increase over time due to the powerScale
            damage = int(item[4])*powerScale
            defense = int(item[6])*powerScale
            
            #card() syntax: card_type, name, file_name, health, damage, speed, defense
            
            grid.append(gridSquare(str(assign), card(item[0], item[1], item[2], health, damage, item[5], defense, item[7]))) 
        else:
            grid.append(gridSquare(str(assign), card(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])))

                        
        #incrementing variable that assigns coords
        if assign % 5 == 0:
            assign += 6
        else:
            assign += 1

    #set coin amounts
    for item in grid:
        if item.sqrObj.type == 'enemy':

            health = item.sqrObj.maxhp
            damage = item.sqrObj.dmg
            speed = item.sqrObj.spd
            defence = item.sqrObj.dfc

            coinTotal = (health + defence) * round((powerScale + speed)/6) + damage * random.randint(10, 20) #coin bounty for each enemy
            
            item.sqrObj.coins = int(coinTotal)
        elif item.sqrObj.type == 'special':
            item.sqrObj.coins = random.randint(5, 10) * powerScale

    return grid

empty = gridSquare('00', card('none', 'none', 'none', 0, 0, 0, 0, '')) #empty card object (exists as a placeholder)
selectRec = [empty, empty] #selection record

fixedGrid = createGrid('none') #this grid does not change (used to draw grid lines etc)
grid = createGrid(fileStore[0][0])


def editGrid(targetPos, targetObject, setObject): #used to edit cards on the grid during a level
    global grid
    global coins
    for i, item in enumerate(grid):
        if item.pos == targetPos:
            match targetObject:
                case 'highlight':
                    grid[i].highlight = setObject
                case 'hp':
                    if setObject >= 1 or grid[i].sqrObj.type == 'player':
                        grid[i].sqrObj.hp = round(setObject)
                    elif setObject < 1 and grid[i].sqrObj.type != 'player':
                        coins += grid[i].sqrObj.coins
                        grid[i].sqrObj = card()
                case 'dmg':
                    grid[i].sqrObj.dmg += setObject
                    grid[i].sqrObj.dmg = round(grid[i].sqrObj.dmg)
                case 'spd':
                    grid[i].sqrObj.spd += setObject
                    grid[i].sqrObj.spd = round(grid[i].sqrObj.spd)
                case 'dfc':
                    grid[i].sqrObj.dfc += setObject
                    grid[i].sqrObj.dfc = round(grid[i].sqrObj.dfc)
                
                case 'name':
                    grid[i].sqrObj.name = setObject
                case _:
                    pass

def select(obj): #function to get selected square and determine action (move or attack)

    global selectRec
    global grid
    global action

    #[0] = first selection, [1] second selection
    objx, objy = int(obj.pos[0]), int(obj.pos[1])

    if selectRec[1].sqrObj.name == 'none':
        if selectRec[0].sqrObj.name == 'none' and obj.sqrObj.type == 'player':#if selection record is empty and player icon is pressed

            selectRec[0] = obj #(first click)
            displayOption()
            editGrid(obj.pos, 'highlight', 'move')



        elif selectRec[0].sqrObj.name != 'none': #if player icon has been clicked but not move player
            if selectRec[0].pos != obj.pos: #if the second square selected is not the same as the player
                move = False
                playerx, playery = int(selectRec[0].pos[0]), int(selectRec[0].pos[1])

                #(second click)
                #check square is within move range

                if (abs(playerx - objx) <= selectRec[0].sqrObj.spd and playery == objy) ^ (abs(playery - objy) <= selectRec[0].sqrObj.spd and playerx == objx): #check along x and y axis
                    move = True

                #determine whether player is attacking or moving
                if move == True:
                    selectRec[1] = obj
                    for item in grid:
                        editGrid(item.pos, 'highlight', 'none')

                    if obj.sqrObj.hp > 0:
                        action = 'attack'
                        editGrid(selectRec[0].pos, 'highlight', 'attack')
                        editGrid(selectRec[1].pos, 'highlight', 'attack')

                    else:
                        action = 'move'
                        editGrid(selectRec[0].pos, 'highlight', 'move')
                        editGrid(selectRec[1].pos, 'highlight', 'move')


            else: #if player is selected again, cancel
                selectRec = [empty, empty]
                for item in grid:
                    editGrid(item.pos, 'highlight', 'none')

def display(): #default display function
    bg()
    for square in grid: #for each square
        match square.highlight: #display card highlight
            case 'option':
                screen.blit(pygame.transform.scale(hlOpt, (interval, interval)), convertCoords(square.pos))
            case 'move':
                screen.blit(pygame.transform.scale(hlMove, (interval, interval)), convertCoords(square.pos))
            case 'attack':
                screen.blit(pygame.transform.scale(hlAtk, (interval, interval)), convertCoords(square.pos))
            case 'ability':
                screen.blit(pygame.transform.scale(hlAb, (interval, interval)), convertCoords(square.pos))
            case _:
                pass

        #Display cards and stat icons

        isize =  round(interval/4)#icon size
        fsize = round(interval/6)
        yshift = round(interval/40) #text shift on y axis (for the number displayed on the icons)
        #xshift defined later since it is dependent on chr length of number

        left =  int(convertCoords(square.pos)[0])
        right = int(convertCoords(square.pos)[0]) + interval - isize
        up =    int(convertCoords(square.pos)[1])
        down =  int(convertCoords(square.pos)[1]) + interval - isize

        #get and display card images
        if square.sqrObj.name != 'blank': #blank cards are not shown
            screen.blit(pygame.transform.scale(square.sqrObj.file, (interval, interval)), convertCoords(square.pos))

            #stat icons
            statStore = [
                [square.sqrObj.hp, ihealth, (left, up)],      #hp
                [square.sqrObj.dmg, idamage, (right, up)],    #damage
                [square.sqrObj.spd, ispeed, (left, down)],    #speed
                [square.sqrObj.dfc, idefence, (right, down)]  #defence
                ]
            
            for item in statStore:
                xshift = round(fsize/(2*len(str(item[0]))))
                               
                screen.blit(pygame.transform.scale(item[1], (isize, isize)), item[2])
                screen.blit(pygame.font.Font(ifont, fsize).render(str(item[0]), True, (0, 0, 0)), (int(item[2][0])+xshift, int(item[2][1])+yshift))

    for square in fixedGrid:
        pygame.draw.rect(screen, (0, 0, 0), (convertCoords(square.pos)[0], convertCoords(square.pos)[1], interval, interval), 1)
    pygame.draw.rect(screen, (0, 0, 0), (convertCoords('11')[0], convertCoords('11')[1], interval*5, interval*5), 3)

    #side panel
    #draw side panel
    alpha((interval, interval*5), 128, convertCoords('61'))
    
    #border
    pygame.draw.rect(screen, (0, 0, 0), (convertCoords('61')[0], convertCoords('61')[1], interval, interval), 1)
    pygame.draw.rect(screen, (0, 0, 0), (convertCoords('62')[0], convertCoords('62')[1], interval, interval), 1)
    pygame.draw.rect(screen, (0, 0, 0), (convertCoords('63')[0], convertCoords('63')[1], interval, interval*2), 1)
    pygame.draw.rect(screen, (0, 0, 0), (convertCoords('65')[0], convertCoords('65')[1], interval, interval), 1)

    #Top Icons
    fontSize = round(interval/4)

    #coin counter
    write('Coins', hfont, round(interval/6), (255, 255, 255), convertCoords('62'), subinterval, round(subinterval/2))
    write(str(coins), hfont, round(interval/6), (255, 255, 255), convertCoords('62'), subinterval, round(subinterval*3/4))

    xpos = convertCoords('62')[0] + round(fontSize/2)
    ypos = convertCoords('62')[1] + round(fontSize*5/2)
    
    #pause and shop
    screen.blit(pygame.transform.scale(icoin, (fontSize, fontSize)), (xpos, ypos))
    xpos = convertCoords('72')[0] - round(fontSize*3/2)
    screen.blit(pygame.transform.scale(ipause, (fontSize, fontSize)), (xpos, ypos))

    #Level Counter
    fontSize = round(interval/5)

    lvlcounter = 0
    if gameMode == 'Story': 
        lvlcounter = f'World {fileIndex+1}.{level%worldSize+1}'
    elif gameMode == 'Endless':
        lvlcounter = f'Level {level+1}'

    
    lvlname1, lvlname2 = fileStore[fileIndex][1].split(':')

    #level info
    blockPrint(convertCoords('61'),
               [
                   gameMode.title(),
                   lvlcounter,
                   '',
                   lvlname1,
                   lvlname2
        ],
               (255, 255, 255),
               round(interval/6),
               hfont,
               subinterval
               )
    #right click info
    screen.blit(pygame.transform.scale(menuScroll, (interval, interval*2)), convertCoords('63'))
    write('Card Details', hfont, round(interval*3/20), (0, 0, 0), convertCoords('63'), subinterval, subinterval)
    blockPrint(convertCoords('64'), sideText, (0, 0, 0), round(interval/8), ifont, subinterval, -round(subinterval/2))

    #draw ability icon
    if ability[3] == True:
        screen.blit(pygame.transform.scale(hlAb, (interval, interval)), convertCoords('65'))
        screen.blit(pygame.transform.scale(playerInfo[4], (round(interval/4), round(interval/4))), convertCoords('65'))
        write(f'Level: {ability[2]}', ifont, round(interval/6), (0, 0, 0), convertCoords('65'), subinterval, round(interval/3))
        write(f'Uses: {ability[1]}', ifont, round(interval/6), (0, 0, 0), convertCoords('65'), subinterval, round(interval*2/3))
    else:
        screen.blit(pygame.transform.scale(playerInfo[4], (round(interval/4), round(interval/4))), convertCoords('65'))
        write(f'Level: {ability[2]}', ifont, round(interval/6), (255, 255, 255), convertCoords('65'), subinterval, round(interval/3))
        write(f'Uses: {ability[1]}', ifont, round(interval/6), (255, 255, 255), convertCoords('65'), subinterval, round(interval*2/3))

    
def animate(image, start, end, num=''): #used to animate movement (card movement, projectile movement)

    xpos, ypos = int(convertCoords(start.pos)[0]), int(convertCoords(start.pos)[1])
    endCoords = convertCoords(end.pos)

    #get movement direction
    direction = moveStep(start.pos, end.pos)[0]

    shift = interval/3

    if num == '': #if there is no total damage value, play move sound
        playSound(mvSound)
        netDmg = -1
    else:
        netDmg = num
        
    while 1:
        #main display
        display()
        screen.blit(pygame.transform.scale(image, (interval, interval)), (xpos, ypos))
        pygame.display.update()

        match direction: #shift the image
            case 'L':
                xpos += -shift
                if xpos < endCoords[0]:
                    break
            case 'R':
                xpos += shift
                if xpos > endCoords[0]:
                    break
            case 'U':
                ypos += -shift
                if ypos < endCoords[1]:
                    break
            case 'D':
                ypos += shift
                if ypos > endCoords[1]:
                    break

    
    if num != '': #play attack sound
        playSound(atkSound)
        
    elif netDmg >= 0: #play block effect
        screen.blit(pygame.transform.scale(image, (interval, interval)), (xpos, ypos))
        i = 0
        while i < FPS:
            screen.blit(pygame.transform.scale(idefence, (interval, interval)), convertCoords(end.pos))
            pygame.display.update()
            i += 1

def reachPortal(): #reach portal animation
    global grid

    playSound(portalSound)

    size = interval
    degree = 0
    loop = True

    while loop:

        #position
        pos = convertCoords(selectRec[0].pos)[0] + (interval - size)/2, convertCoords(selectRec[0].pos)[1] + (interval - size)/2

        #display
        display()
        screen.blit(pygame.transform.scale(pygame.transform.rotate(player.sqrObj.file, degree), (size, size)), (pos, pos))

        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        #increment (rotate)
        size += -round(interval/20)
        degree += -90

        #checks
        if size <= 0:
            loop = False

def pause(): #pause menu
    global animation, sounds, selectRec
    pygame.mixer.music.pause() #pause sounds

    while 1:
        resize()
        display()

        alpha((xscreen, yscreen), 224, (0, 0))

        fontSize = round(interval/4)

        #draw pause icon for aesthetics
        screen.blit(pygame.transform.scale(ipause, (subinterval, subinterval)), (convertCoords('11')[0] + round(interval/4), convertCoords('11')[1] + round(interval/4)))

        #pause menu options
        quitGame = write('--Main Menu--', hfont, fontSize, (255, 255, 255), convertCoords('32'), interval, subinterval, True)
        animateToggle = write(f'--Animations: {animation}--', hfont, fontSize, (255, 255, 255), convertCoords('32'), interval, interval, True)
        soundToggle = write(f'--Sound: {sounds}--', hfont, fontSize, (255, 255, 255), convertCoords('33'), interval, subinterval, True)
        
        
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        #detect options
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #check for quit events
            
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #mouse click

                #check for option select
             
                if quitGame[0] < mouse[0] < quitGame[0]+quitGame[2] and quitGame[1] < mouse[1] < quitGame[1]+quitGame[3]:
                    playSound(clickSound)
                    selectRec = [empty, empty]
                    pygame.mixer.music.stop()
                    return False
                    
                elif animateToggle[0] < mouse[0] < animateToggle[0]+animateToggle[2] and animateToggle[1] < mouse[1] < animateToggle[1]+animateToggle[3]:
                    playSound(clickSound)
                    if animation == 'On':
                        animation = 'Off'
                    else:
                        animation = 'On'

                elif soundToggle[0] < mouse[0] < soundToggle[0]+soundToggle[2] and soundToggle[1] < mouse[1] < soundToggle[1]+soundToggle[3]:
                    playSound(clickSound)
                    if sounds == 'On':
                        sounds = 'Off'
                    else:
                        sounds = 'On'
                        
                else:
                    if sounds == 'Off':
                        pygame.mixer.music.stop()
                    else:
                        pygame.mixer.music.unpause()
                    return True
                
            elif event.type == pygame.KEYDOWN:
                if sounds == 'Off':
                    pygame.mixer.music.stop()
                else:
                    pygame.mixer.music.unpause()
                return True
                

def shop(): #shop screen
    global coins, php, pdmg, pspd, pdfc
    global abilityScale

    shift = random.randint(0,2)
    buy = '1'

    while 1:
        resize()
        display()

        alpha((xscreen, yscreen), 224, (0, 0)) #transparent bg
        fsize = round(interval/4) #font size
        f2size = round(interval/5)
        f3size = round(interval/6)

        #cost variables
        hpCost  = (php*5 + shift)*int(buy)
        dmgCost = (pdmg*5 + shift)*int(buy)
        spdCost = (pspd*100 + shift)*int(buy)
        dfcCost = (pdfc*10 + shift)*int(buy)

        upgradeCost = (abilityScale * playerInfo[13] * ability[2] + shift)*int(buy)
        abilityCost = (abilityScale * playerInfo[13] * ability[2] + shift)*int(buy)
        

        #draw gridlines
        pygame.draw.rect(screen, (255, 255, 255), (convertCoords('11')[0], convertCoords('11')[1], interval*6, interval), 1)
        pygame.draw.rect(screen, (255, 255, 255), (convertCoords('52')[0], convertCoords('52')[1], interval*2, interval*4), 1)

        #display shop
        screen.blit(pygame.transform.scale(icoin, (subinterval, subinterval)), (convertCoords('11')[0] + round(interval/4), convertCoords('11')[1] + round(interval/4)))
        write(f'Coins: {coins}', hfont, fsize, (255, 255, 255), convertCoords('21'), interval, subinterval)
        write(f'Buy: {buy}', hfont, fsize, (255, 255, 255), convertCoords('41'), interval, subinterval)

        #stat icons
        statStore = [
            [php, hpCost, '13', '12', '22', ihealth],      #hp
            [pdmg, dmgCost, '33', '32', '42', idamage],    #damage
            [pspd, spdCost, '15', '14', '24', ispeed],    #speed
            [pdfc, dfcCost, '35', '34', '44', idefence]  #defence
            ]
            
        for item in statStore:
            #draw each stat shop option
            screen.blit(pygame.transform.scale(item[5], (interval, interval)), convertCoords(item[3]))
            screen.blit(pygame.transform.scale(arrowButton, (interval, interval)), convertCoords(item[4]))
            write(f'Cost: {item[1]}', hfont, fsize, (255, 255, 255), convertCoords(item[2]), interval, subinterval)
            write(str(item[0]), ifont, fsize, (0, 0, 0), convertCoords(item[3]), subinterval, subinterval)

        #ability shop
        #display ability shop
        screen.blit(pygame.transform.scale(playerInfo[4], (interval, interval)), convertCoords('62'))
        write(str(ability[0]), hfont, f2size, (255, 255, 255), convertCoords('52'), subinterval, subinterval)

        #ability level
        screen.blit(pygame.transform.scale(arrowButton, (interval, interval)), convertCoords('64'))
        write(f'Level: {ability[2]}', ifont, f3size, (255, 255, 255), convertCoords('54'), subinterval, round(interval/3))
        write(f'Cost: {upgradeCost}', ifont, f3size, (255, 255, 255), convertCoords('54'), subinterval, round(interval*2/3))

        #ability uses
        screen.blit(pygame.transform.scale(arrowButton, (interval, interval)), convertCoords('65'))
        write(f'Uses: {ability[1]}', ifont, f3size, (255, 255, 255), convertCoords('55'), subinterval, round(interval/3))
        write(f'Cost: {abilityCost}', ifont, f3size, (255, 255, 255), convertCoords('55'), subinterval, round(interval*2/3))

        #determine info to display
        abilityInfo = []
        match ability[0]:
            case 'Amulet':
                abilityInfo = ['Increases damage', 'health and defence', f'by {25+25*ability[2]}%']
                
            case 'Thorns':
                abilityInfo = [f'Reflects {25+25*ability[2]}%', 'of damage taken']
                
            case 'Cloak':
                abilityInfo = ['Invisible for', 'one turn', 'and deals', f'{25+25*ability[2]}% more', 'damage']
                
            case 'Old Magic':
                if 100 - 25*ability[2] <= 0:
                    abilityInfo = ['Deals {25*ability[2] - 100}% of', 'enemy defence', 'as damage and', 'enemy defence is', 'ineffective']
                else:
                    abilityInfo = ['Enemy defence', f'is {25*ability[2]}% less', 'effective']
                
            case 'Revive':
                abilityInfo = ['Revives on death', f'with {25+25*ability[2]}% health']
                
            case 'Soul Jar':
                abilityInfo = ['Each kill restores', f'{50+25*ability[2]}% of enemy', 'health']

            case 'Riftwalk':
                abilityInfo = ['Teleport to any', 'empty tile', 'before taking', 'a turn and', 'increases shield by', f'{-25+25*ability[2]}%']
                        
        blockPrint(convertCoords('53'), abilityInfo, (255, 255, 255), round(fsize/2), ifont, interval, round(subinterval/2))
        
            
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        #detect options
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #mouse click
                if convertCoords('22')[0] < mouse[0] < convertCoords('22')[0]+interval and convertCoords('22')[1] < mouse[1] < convertCoords('22')[1]+interval:
                    playSound(clickSound)
                    if hpCost <= coins:
                        coins += -hpCost
                        php += int(buy)
                        
                elif convertCoords('42')[0] < mouse[0] < convertCoords('42')[0]+interval and convertCoords('42')[1] < mouse[1] < convertCoords('42')[1]+interval:
                    playSound(clickSound)
                    if dmgCost <= coins:
                        coins += -dmgCost
                        pdmg += int(buy)
                        
                elif convertCoords('24')[0] < mouse[0] < convertCoords('24')[0]+interval and convertCoords('24')[1] < mouse[1] < convertCoords('24')[1]+interval:
                    playSound(clickSound)
                    if spdCost <= coins:
                        coins += -spdCost
                        pspd += int(buy)
                        
                elif convertCoords('44')[0] < mouse[0] < convertCoords('44')[0]+interval and convertCoords('44')[1] < mouse[1] < convertCoords('44')[1]+interval:
                    playSound(clickSound)
                    if dfcCost <= coins:
                        coins += -dfcCost
                        pdfc += int(buy)
                        
                elif convertCoords('64')[0] < mouse[0] < convertCoords('64')[0]+interval and convertCoords('64')[1] < mouse[1] < convertCoords('64')[1]+interval:
                    playSound(clickSound)
                    if upgradeCost <= coins:
                        coins += -upgradeCost
                        ability[2] += int(buy)

                elif convertCoords('65')[0] < mouse[0] < convertCoords('65')[0]+interval and convertCoords('65')[1] < mouse[1] < convertCoords('65')[1]+interval:
                    playSound(clickSound)
                    if abilityCost <= coins:
                        coins += -abilityCost
                        ability[1] += int(buy)
                        abilityScale += 1
                    
                else:
                    return
            elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == pygame.TEXTINPUT and str(event.text) in [str(num) for num in range(0,10)] and len(buy) <= 2:
                if buy == '0':
                    buy = str(event.text)
                else:
                    buy += str(event.text)
            elif event.type == pygame.KEYDOWN and event.key == K_BACKSPACE:
                buy = buy[:-1]
                if buy == '':
                    buy = '0'
                
def playerSelect():

    while 1:
        resize()
        screen.fill((0, 0, 0))
        bgPos = round((xscreen - xlimit)/2), round((yscreen - ylimit)/2)
        screen.blit(pygame.transform.scale(towerBg, (xlimit, ylimit)), bgPos) #background

        alpha((xscreen, yscreen), 128, (0, 0))
        
        write('Chose a Hero', hfont, subinterval, (255, 255, 255), convertCoords('31'), interval, subinterval)

        #playerStore order: chr name, Chr pos, chr file, ability pos, ability file, name pos, hp, dmg, spd, dfc, descrip pos, ability description, projectile, ability cost
        for item in playerStore:
            if item[0] != 'Dark Knight':
                pygame.draw.rect(screen, (255, 255, 255), (convertCoords(item[1])[0], convertCoords(item[1])[1], interval*2, interval*2), 1) #draw boxes
        
                screen.blit(pygame.transform.scale(item[2], (interval, interval)), convertCoords(item[1]))
                screen.blit(pygame.transform.scale(item[4], (interval, interval)), convertCoords(item[3]))
                write(str(item[0]), hfont, round(interval/6), (255, 255, 255), convertCoords(item[5]), subinterval, round(subinterval/2))

                #stats: text, xshift, yshift, image icon
                statPos = [
                    [item[6], round(subinterval/2), subinterval, ihealth],
                    [item[7], round(subinterval/2)*3, subinterval, idamage],
                    [item[8], round(subinterval/2), round(subinterval/2)*3, ispeed],
                    [item[9], round(subinterval/2)*3, round(subinterval/2)*3, idefence]
                    ]
                for statItem in statPos:
                    screen.blit(pygame.transform.scale(statItem[3], (round(interval/4), round(interval/4))), (convertCoords(item[5])[0]+statItem[1]-round(interval/8), convertCoords(item[5])[1]+statItem[2]-round(interval/8)))
                    write(str(statItem[0]), ifont, round(interval/8), (0, 0, 0), convertCoords(item[5]), statItem[1], statItem[2])

                blockPrint(convertCoords(item[10]), item[11], (255, 255, 255), round(interval/8), ifont, subinterval, round(subinterval/2))


        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        #detect options
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT  or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
                
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #mouse click
                
                for line in playerStore:
                    xpos = convertCoords(line[1])[0]
                    ypos = convertCoords(line[1])[1]
                    
                    if xpos < mouse[0] < xpos+interval*2 and ypos < mouse[1] < ypos+interval*2:
                        playSound(clickSound)
                        return playerStore.index(line)

def scoreboard():
    global lbStore

    def get2(list):
        return list[2]

    #sort list before displaying
    sbStore.sort(key = get2, reverse = True)
    sbStore.sort(reverse = True)
    
    while 1:
        resize()
        screen.fill((0, 0, 0))
        bgPos = round((xscreen - xlimit)/2), round((yscreen - ylimit)/2)
        screen.blit(pygame.transform.scale(towerBg, (xlimit, ylimit)), bgPos) #background

        alpha((xscreen, yscreen), 128, (0, 0))

        #draw gridlines

        pygame.draw.rect(screen, (0, 0, 0), (convertCoords('11')[0], convertCoords('11')[1], interval*6, interval), 1)
        pygame.draw.rect(screen, (0, 0, 0), (convertCoords('12')[0], convertCoords('12')[1], interval*3, interval*4), 1)
        pygame.draw.rect(screen, (0, 0, 0), (convertCoords('42')[0], convertCoords('42')[1], interval*3, interval*4), 1)

        write('Scoreboard', hfont, subinterval, (255, 255, 255), convertCoords('31'), interval, subinterval)


        #headers        
        write('Level', hfont, round(subinterval/2), (255, 255, 255), convertCoords('12'), subinterval, subinterval)
        write('Hero', hfont, round(subinterval/2), (255, 255, 255), convertCoords('22'), subinterval, subinterval)
        write('Coins', hfont, round(subinterval/2), (255, 255, 255), convertCoords('32'), subinterval, subinterval)
        write('Level', hfont, round(subinterval/2), (255, 255, 255), convertCoords('42'), subinterval, subinterval)
        write('Hero', hfont, round(subinterval/2), (255, 255, 255), convertCoords('52'), subinterval, subinterval)
        write('Coins', hfont, round(subinterval/2), (255, 255, 255), convertCoords('62'), subinterval, subinterval)


        posList = [
            ['13', '23', '33', round(interval/3)],
            ['13', '23', '33', round(interval*2/3)],
            ['14', '24', '34', round(interval/3)],
            ['14', '24', '34', round(interval*2/3)],
            ['15', '25', '35', round(interval/3)],
            ['15', '25', '35', round(interval*2/3)],
            ['43', '53', '63', round(interval/3)],
            ['43', '53', '63', round(interval*2/3)],
            ['44', '54', '64', round(interval/3)],
            ['44', '54', '64', round(interval*2/3)],
            ['45', '55', '65', round(interval/3)],
            ['45', '55', '65', round(interval*2/3)]
            ]

        #draw scores
        for i in range(0, min(12, len(sbStore))):
            ref = posList[i]
            entry = sbStore[i]

            write(str(entry[0]), ifont, round(subinterval/3), (255, 255, 255), convertCoords(ref[0]), subinterval, ref[3])
            write(str(entry[1]), ifont, round(subinterval/3), (255, 255, 255), convertCoords(ref[1]), subinterval, ref[3])
            write(str(entry[2]), ifont, round(subinterval/3), (255, 255, 255), convertCoords(ref[2]), subinterval, ref[3])

        pygame.display.update()
        pygame.time.Clock().tick(FPS)
        
        endLoop = False
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                endLoop = True
        if endLoop == True:
            break

def guide():
    pageIndex = 0
    pageList = []
    page = []

    for line in open('files/gameGuide.txt'):
        line = line.rstrip('\n')
        if line == 'pg':
            pageList.append(page)
            page = []
        else:
            page.append(line)
    
    while 1:
        resize()
        screen.fill((0, 0, 0))
        bgPos = round((xscreen - xlimit)/2), round((yscreen - ylimit)/2)
        screen.blit(pygame.transform.scale(towerBg, (xlimit, ylimit)), bgPos) #background
        alpha((xscreen, yscreen), 128, (0, 0))

        write('Guide', hfont, subinterval, (255, 255, 255), convertCoords('31'), interval, subinterval)

        #arrows (used to move screens)
        if pageIndex > 0:
            screen.blit(pygame.transform.scale(pygame.transform.rotate(arrowButton, 90), (subinterval, interval)), convertCoords('13'))
        if pageIndex < len(pageList)-1:
            screen.blit(pygame.transform.scale(pygame.transform.rotate(arrowButton, -90), (subinterval, interval)), (convertCoords('63')[0]+subinterval, convertCoords('63')[1]))

        fsize = round(interval/8)
        h1size = round(interval/4)
        h2size = round(interval/6)
        yshift = round(subinterval/3)
        
        #display correct page          
        for line in pageList[pageIndex]:
            if line.startswith('h1') == True:
                yshift += round(subinterval/3)
                write(line[2:], hfont, h1size, (255, 255, 255), convertCoords('42'), 0, yshift)
                yshift += round(subinterval/3)
            elif line.startswith('h2') == True:
                yshift += round(subinterval/3)
                write(line[2:], hfont, h2size, (255, 255, 255), convertCoords('42'), 0, yshift)
                yshift += round(subinterval/3)
            else:
                blockPrint(convertCoords('42'), eval(line), (255, 255, 255), fsize, ifont, 0, yshift)
                yshift += round(subinterval/3)*len(eval(line))
        

        pygame.display.update()
        pygame.time.Clock().tick(FPS)
            
        endLoop = False
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN: #check buttons
                if  convertCoords('13')[0] < mouse[0] < convertCoords('13')[0]+subinterval and convertCoords('13')[1] < mouse[1] < convertCoords('13')[1]+interval and pageIndex > 0:
                    playSound(clickSound)
                    pageIndex += -1
                elif convertCoords('63')[0]+subinterval < mouse[0] < convertCoords('63')[0]+interval and convertCoords('63')[1] < mouse[1] < convertCoords('63')[1]+interval and pageIndex < len(pageList)-1:
                    playSound(clickSound)
                    pageIndex += 1
                else: #if somewhere else is clicked, close guide
                    endLoop = True
        if endLoop == True:
            break

def menu():
    global playGame, gameMode
    global character, playerInfo
    global php, pdmg, pspd, pdfc, mph, mdmg

    playMusic('sounds/menu theme.wav')

    while 1:
        resize()
        screen.fill((0, 0, 0))
        bgPos = round((xscreen - xlimit)/2), round((yscreen - ylimit)/2)
        screen.blit(pygame.transform.scale(towerBg, (xlimit, ylimit)), bgPos) #background

        fontSize = round(interval/4)

        #options
        #gameStart
        gameStart = (convertCoords('32')[0], convertCoords('32')[1], interval*2, subinterval)
        screen.blit(pygame.transform.scale(rectButton, (interval*2, subinterval)), (gameStart[0], gameStart[1]))
        write('--Start Game--', hfont, fontSize, (0, 0, 0), (gameStart[0], gameStart[1]), interval, round(subinterval/2))

        #endless
        endless = (convertCoords('32')[0], convertCoords('32')[1]+round(interval*3/4), interval*2, subinterval)
        screen.blit(pygame.transform.scale(rectButton, (interval*2, subinterval)), (endless[0], endless[1]))
        write('--Endless--', hfont, fontSize, (0, 0, 0), (endless[0], endless[1]), interval, round(subinterval/2))

        #scores
        scores = (convertCoords('33')[0], convertCoords('33')[1]+subinterval, interval*2, subinterval)
        screen.blit(pygame.transform.scale(rectButton, (interval*2, subinterval)), (scores[0], scores[1]))
        write('--Scoreboard--', hfont, fontSize, (0, 0, 0), (scores[0], scores[1]), interval, round(subinterval/2))

        #guidebook
        guidebook = (convertCoords('33')[0], convertCoords('34')[1]+round(interval*1/4), interval*2, subinterval)
        screen.blit(pygame.transform.scale(rectButton, (interval*2, subinterval)), (guidebook[0], guidebook[1]))
        write('--Guide--', hfont, fontSize, (0, 0, 0), (guidebook[0], guidebook[1]), interval, round(subinterval/2))
        
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

        #detect options
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            #check buttons
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #mouse click
                if gameStart[0] < mouse[0] < gameStart[0]+gameStart[2] and gameStart[1] < mouse[1] < gameStart[1]+gameStart[3]:
                    playSound(clickSound)
                    playGame = True
                    gameMode = 'Story'
                    break
                
                elif endless[0] < mouse[0] < endless[0]+endless[2] and endless[1] < mouse[1] < endless[1]+endless[3]:
                    playSound(clickSound)
                    playGame = True
                    gameMode = 'Endless'
                    break
                
                elif scores[0] < mouse[0] < scores[0]+scores[2] and scores[1] < mouse[1] < scores[1]+scores[3]:
                    playSound(clickSound)
                    scoreboard()
                
                elif guidebook[0] < mouse[0] < guidebook[0]+guidebook[2] and guidebook[1] < mouse[1] < guidebook[1]+guidebook[3]:
                    playSound(clickSound)
                    guide()

        if playGame == True: #if game is started, call character select and setup variables
            pygame.mixer.music.stop()            
            playerInfo = playerStore[playerSelect()]
            php, pdmg, pspd, pdfc = playerInfo[6], playerInfo[7], playerInfo[8], playerInfo[9]
            character = ['player', playerInfo[0], playerInfo[2], php, pdmg, pspd, pdfc, playerInfo[12]]
            match playerInfo[0]:
                case 'Knight':
                    ability[0] = 'Amulet'
                case 'Paladin':
                    ability[0] = 'Thorns'
                case 'Rogue':
                    ability[0] = 'Cloak'
                case 'Mage':
                    ability[0] = 'Old Magic'
                case 'Priest':
                    ability[0] = 'Revive'
                case 'Necromancer':
                    ability[0] = 'Soul Jar'
                case 'Dark Knight':
                    ability[0] = 'Riftwalk'

            break

def end(death): #game end screen
    pygame.mixer.music.stop()    
    if death == True: #msg based on death state
        msg = random.choice(deathMsg)
    else:
        msg = random.choice(winMsg)
        
    if gameMode == 'Story':
        reached = f'World {fileIndex+1}.{level%worldSize+1}'
    else:
        reached = f'Level: {level+1}'
        
    while 1:
        resize()
        display()
        
        alpha((xscreen, yscreen), 224, (0, 0))

        #display world reached, hero and coins
        write(reached, hfont, round(subinterval/3), (255, 255, 255), convertCoords('23'), interval, subinterval)
        write(str(playerInfo[0]), hfont, round(subinterval/3), (255, 255, 255), convertCoords('33'), interval, subinterval)
        write(f'Coins: {coins}', hfont, round(subinterval/3), (255, 255, 255), convertCoords('43'), interval, subinterval)

        write(str(msg), hfont, round(interval/4), (255, 255, 255), convertCoords('42'), 0, subinterval)
        
        pygame.display.update()
        pygame.time.Clock().tick(FPS)
        
        
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1  or event.type == pygame.KEYDOWN: #mouse click
                return
        

def enemy(enemy, path): #enemy attack/move
    global playGame, sbStore

    #check player is in range
    playerx, playery = int(player.pos[0]), int(player.pos[1])
    enemyx, enemyy = int(enemy.pos[0]), int(enemy.pos[1])

    switch = 'move'
    if (abs(playerx - enemyx) <= enemy.sqrObj.spd and playery == enemyy) ^ (abs(playery - enemyy) <= enemy.sqrObj.spd and playerx == enemyx):
        switch = 'attack'

    match switch:
        case 'move':
            step = str(random.choice(path))
            newx, newy = enemyx, enemyy

            moveRange = min(enemy.sqrObj.spd, path.count(step))

            for i in range(moveRange):
                match step: #move enemy
                    case 'L':
                        newx += -1
                    case 'R':
                        newx += 1
                    case 'U':
                        newy += -1
                    case 'D':
                        newy += 1

            newpos = f'{newx}{newy}'
            for item in grid:
                if item.pos == newpos and item.sqrObj.type == 'blank':
                    nameStore = enemy.sqrObj.name
                    editGrid(enemy.pos, 'name', 'blank')
                    if animation == 'On':
                        animate(enemy.sqrObj.file, enemy, item)

                    #swap locations
                    temp = enemy.pos
                    enemy.pos = item.pos
                    item.pos = temp

                    editGrid(enemy.pos, 'name', nameStore)
                    editGrid(enemy.pos, 'highlight', 'move')
                

        case 'attack':
            dmgTotal = min(0, -(enemy.sqrObj.dmg - player.sqrObj.dfc))
            editGrid(enemy.pos, 'highlight', 'attack')

            #NOTE: default image faces right
            match path[0]:
                case 'L':
                    damageIcon = pygame.transform.rotate(enemy.sqrObj.proj, -270)
                case 'R':
                    damageIcon = pygame.transform.rotate(enemy.sqrObj.proj, -90)
                case 'U':
                    damageIcon = pygame.transform.rotate(enemy.sqrObj.proj, 0)
                case 'D':
                    damageIcon = pygame.transform.rotate(enemy.sqrObj.proj, -180)
            if animation == 'On':
                animate(damageIcon, enemy, player, dmgTotal)

            editGrid(player.pos, 'hp', player.sqrObj.hp + dmgTotal) #change enemy hp

            if reflect == True:
                editGrid(enemy.pos, 'hp', enemy.sqrObj.hp - enemy.sqrObj.dmg*(0.25*ability[2]))
            
            if dmgTotal >= 0:
                editGrid(player.pos, 'dfc', -powerScale)
            
            if player.sqrObj.hp <= 0: #if player has at least one use on the revive item
                if ability[0] == 'Revive' and ability[1] > 0:
                    playSound(ablSound)
                    editGrid(player.pos, 'highlight', 'ability')
                    editGrid(player.pos, 'hp', php*(0.25+0.25*ability[2]))
                    ability[1] += -1
                    
                else:
                    if gameMode == 'Endless':
                        entry = [level, playerInfo[0], coins]
                        sbStore.append(entry)

                        #add to file
                        f = open('files/scoreboard.txt', 'w') #overwrite file
                        f.write('[\n')
                        for line in sbStore:  #write each entry to file
                            f.write(f'{line},\n')
                        f.write(']')
                        f.close()
                        
                    playGame = False
                    #end screen
                    end(True)
                    


#Game Loop
while 1:

    if playGame == False: #game is not playing (set defaults, return to menu)

        #Reset Defaults
        
        coins = 0

        worldSize = 3
        powerScale = 1
        abilityScale = 1 # scales cost of buying ability uses. Each time one is purchased, ability scale is incremented

        
        #Ability flags
        reflect = False
        cloak = False
        pierce = 1
        lifeSteal = False

        #syntax: name: ability name, ability uses, ability level, ability active
        ability = ['none', 1, 1, False]
        
        menu()
        level = 0
        if gameMode == 'Story':
            fileIndex = 0
        else:
            fileIndex = random.randint(0, 10)
        file = fileStore[fileIndex]
        playMusic(musicStore[fileIndex])

    #world transition
    if gameMode == 'Story' and level % worldSize == 0 or level >= worldSize*10: 
        while 1:            
            resize()
            screen.fill((0, 0, 0))
            write(f'World {fileIndex+1}', hfont, round(subinterval/2), (255, 255, 255), convertCoords('42'), 0, subinterval)
            write(str(file[1]).replace(':', ' '), hfont, subinterval, (255, 255, 255), convertCoords('43'), 0, 0)
            blockPrint((convertCoords('44')[0], convertCoords('44')[1]-subinterval), file[2], (255, 255, 255), round(interval/8), ifont)
            
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
                        
            endLoop = False
            for event in pygame.event.get(): #check for quit events
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.KEYDOWN: 
                    endLoop = True
            if endLoop == True:
                break
            
    character = ['player', playerInfo[0], playerInfo[2], php*playerInfo[6], pdmg*playerInfo[7], pspd, pdfc, playerInfo[12]]
    grid = createGrid(file[0])
    if animation == 'On':             
        for opacity in range(0, 257, 20):
            display()
            alpha((xscreen, yscreen), 256 - opacity, (0, 0))
                        
            pygame.display.update()
            pygame.time.Clock().tick(FPS)

    while 1: #level loop
        #screen resize
        resize()

        #find player location
        for item in grid:
            if item.sqrObj.type == 'player':
                player = item

        #mouse input
        mouse = pygame.mouse.get_pos()
        action = 'none'
        for event in pygame.event.get(): #check for quit events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #left mouse click
                if convertCoords('65')[0] < mouse[0] < convertCoords('65')[0] + interval and convertCoords('65')[1] < mouse[1] < convertCoords('65')[1] + interval:
                    if ability[1] > 0 and ability[3] == False:
                        #when ability is used

                        #initial values
                        ipos = player.pos
                        ihp = player.sqrObj.hp
                        idmg = player.sqrObj.dmg
                        ispd = player.sqrObj.spd
                        idfc = player.sqrObj.dfc

                        match ability[0]:
                            case 'Amulet': #activate buff
                                playSound(ablSound)
                                editGrid(player.pos, 'highlight', 'ability')
                                ability[1] += -1
                                ability[3] = True
                                editGrid(ipos, 'hp', ihp + ihp*(0.25+0.25*ability[2]))
                                editGrid(ipos, 'dmg', idmg*(0.25+0.25*ability[2]))
                                editGrid(ipos, 'dfc', idfc*(0.25+0.25*ability[2]))
                                
                            case 'Thorns': #activate buff
                                playSound(ablSound)
                                editGrid(player.pos, 'highlight', 'ability')
                                ability[1] += -1
                                ability[3] = True
                                reflect = True
                                
                            case 'Cloak': #activate buff
                                playSound(ablSound)
                                editGrid(player.pos, 'highlight', 'ability')
                                ability[1] += -1
                                ability[3] = True
                                editGrid(ipos, 'dmg', idmg*(0.25+0.25*ability[2]))
                                cloak = True
                                
                            case 'Old Magic': #activate buff
                                playSound(ablSound)
                                editGrid(player.pos, 'highlight', 'ability')
                                ability[1] += -1
                                ability[3] = True
                                pierce = 1 - 0.25*ability[2]
                                
                            case 'Revive':
                                pass
                                
                            case 'Soul Jar': #activate buff
                                playSound(ablSound)
                                editGrid(player.pos, 'highlight', 'ability')
                                ability[1] += -1
                                ability[3] = True
                                lifeSteal = True

                            case 'Riftwalk': #check for teleport destination
                                playSound(ablSound)
                                screen.blit(pygame.transform.scale(hlAb, (interval, interval)), convertCoords('65'))
                                screen.blit(pygame.transform.scale(playerInfo[4], (round(interval/4), round(interval/4))), convertCoords('65'))
                                write(f'Level: {ability[2]}', ifont, round(interval/6), (0, 0, 0), convertCoords('65'), subinterval, round(interval/3))
                                write(f'Uses: {ability[1]}', ifont, round(interval/6), (0, 0, 0), convertCoords('65'), subinterval, round(interval*2/3))
                                pygame.display.update()
                                
                                ability[1] += -1
                                editGrid(ipos, 'dfc', idfc*(-0.25+0.25*ability[2]))
                                endtp = False
                                while 1:
                                    resize()
                                    mouse = pygame.mouse.get_pos()
                                    for event in pygame.event.get(): #check for quit events
                                        if event.type == QUIT:
                                            pygame.quit()
                                            sys.exit()

                                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #left mouse click
                                            target = ''
                                            for item in grid:
                                                xCoord, yCoord = convertCoords(item.pos)
                                                if xCoord < mouse[0] < (xCoord + interval) and yCoord < mouse[1] < (yCoord + interval):
                                                    target = item

                                            if target != '' and target.sqrObj.name == 'blank':
                                                playSound(ablSound)
                                                temp = player.pos
                                                player.pos = target.pos
                                                target.pos = temp
                                                editGrid(player.pos, 'highlight', 'move')
                                                editGrid(target.pos, 'highlight', 'move')
                                                endtp = True
                                    if endtp == True:
                                        break
                                                
                                    
                                
                            case _:
                                print('problem')
                            
                
                for item in grid:
                    xCoord, yCoord = convertCoords(item.pos)
                    if xCoord < mouse[0] < (xCoord + interval) and yCoord < mouse[1] < (yCoord + interval):
                        select(item) #get clicked grid location

                    #check pause and shop buttons using coordinates
                    xCoord = convertCoords('62')[0] + round(round(interval/4)/2)
                    yCoord = convertCoords('62')[1] + round(round(interval/4)*5/2)
            
                if  xCoord < mouse[0] < xCoord + round(interval/4)  and  yCoord < mouse[1] < yCoord + round(interval/4):
                    shop()

                xCoord = convertCoords('72')[0] - round(round(interval/4)*3/2)

                if  xCoord < mouse[0] < xCoord + round(interval/4)  and  yCoord < mouse[1] < yCoord + round(interval/4):
                    playGame = pause()
                    if playGame == False:
                        break
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #right mouse click

                for item in grid:
                    xCoord, yCoord = convertCoords(item.pos)
                    if xCoord < mouse[0] < (xCoord + interval) and yCoord < mouse[1] < (yCoord + interval):
                        sideText = infoStore[item.sqrObj.name]
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_o: #pressing O opens shop (Open Shop)
                shop()
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p  or event.key == K_ESCAPE): #pressing P or ESC opens pause
                playGame = pause()
                if playGame == False:
                    break

        #determine action (move player, attack or nothing)
        if action == 'move':
            nameStore = selectRec[0].sqrObj.name
            editGrid(selectRec[0].pos, 'name', 'blank')
            
            if animation == 'On':
                animate(player.sqrObj.file, selectRec[0], selectRec[1])

            # change character coordinates to destination and append back to main grid
            if selectRec[1].sqrObj.name == 'portal': #if player reaches portal, play animation and start next level

                portalOpen = True
                if level == worldSize*10 and gameMode == 'Story':
                    for item in grid:
                        if item.sqrObj.type == 'boss':
                            portalOpen = False
                    
                if portalOpen == True: #if portal can be entered
                    selectRec[0].pos = selectRec[1].pos

                    #end level
                    for item in grid:
                        editGrid(item.pos, 'highlight', 'none')
                    if animation == 'On':
                        reachPortal()
                    display()
                    selectRec = [empty, empty]
                    
                    if level >= worldSize*10 and gameMode == 'Story': #if entering portal after bossfight
                        playGame = False
                        end(False)
                        
                    break
                else: #swap positions
                    temp = selectRec[0].pos
                    selectRec[0].pos = selectRec[1].pos
                    selectRec[1].pos = temp
                    editGrid(selectRec[0].pos, 'name', nameStore)

                    if animation == 'On':
                        i = 0
                        while i < FPS:
                            screen.blit(pygame.transform.scale(idefence, (interval, interval)), convertCoords(selectRec[1].pos))
                            pygame.display.update()
                            i += 1
                    
                    selectRec = [empty, empty]
                    for item in grid:
                        editGrid(item.pos, 'highlight', 'none')

            else: #swap positions
                temp = selectRec[0].pos
                selectRec[0].pos = selectRec[1].pos
                selectRec[1].pos = temp
                editGrid(selectRec[0].pos, 'name', nameStore)

            #clear highlight and selectRec (reset)
            editGrid(selectRec[0].pos, 'highlight', 'none')
            selectRec = [empty, empty]
            for item in grid:
                editGrid(item.pos, 'highlight', 'none')


        elif action == 'attack':

            direction = moveStep(selectRec[0].pos, selectRec[1].pos)

            #NOTE: default image faces right
            match direction[0]:
                case 'L':
                    projectile = pygame.transform.rotate(player.sqrObj.proj, -270)
                case 'R':
                    projectile = pygame.transform.rotate(player.sqrObj.proj, -90)
                case 'D':
                    projectile = pygame.transform.rotate(player.sqrObj.proj, -180)
                case 'U':
                    projectile = pygame.transform.rotate(player.sqrObj.proj, 0)

            dmgTotal = min(0, -(selectRec[0].sqrObj.dmg - selectRec[1].sqrObj.dfc*pierce))

            if animation == 'On':
                animate(projectile, selectRec[0], selectRec[1], dmgTotal)

            if lifeSteal == True and (selectRec[1].sqrObj.hp + dmgTotal) <= 0:
                editGrid(player.pos, 'hp', player.sqrObj.hp + selectRec[1].sqrObj.maxhp*(0.50+0.25*ability[2]))
                
            editGrid(selectRec[1].pos, 'hp', selectRec[1].sqrObj.hp + dmgTotal) #change enemy hp
            
            if dmgTotal >= 0:
                editGrid(selectRec[1].pos, 'dfc', -powerScale) #weaken defence on full block
                
            selectRec = [empty, empty]
            for item in grid:
                editGrid(item.pos, 'highlight', 'none')

        display()
        ## enemy attack phase
        if action == 'attack' or action == 'move': #if player moves or attacks
            if cloak == False:
                for obj in grid:
                    if obj.sqrObj.type == 'enemy' or obj.sqrObj.type == 'boss':
                        enemy(obj, moveStep(obj.pos, player.pos))
                        if playGame == False:
                            break
            else:
                editGrid(player.pos, 'highlight', 'ability')
                cloak = False
                ability[3] = False

        pygame.display.update()
        pygame.time.Clock().tick(FPS)
        
        #if playgame is false at the end the loop, break loop
        if playGame == False:
            break

    #game end
    editGrid(player.pos, 'highlight', 'ability')
    ability[3] = False
    sideText = ''
    reflect = False
    pierce = 1
    lifeSteal = False
    
    level += 1 #increment level
    if gameMode == 'Story':            
        if level % worldSize == 0 or level >= worldSize*10: #3 levels per world
            if animation == 'On':
                 for opacity in range(0, 257, 20):
                    display()
                    alpha((xscreen, yscreen), opacity, (0, 0))     
                    
                    pygame.display.update()
                    pygame.time.Clock().tick(FPS)
                    
            if playGame == True:
                fileIndex += 1
                powerScale += 1
                file = fileStore[fileIndex] #change world
                playMusic(musicStore[fileIndex])

    elif gameMode == 'Endless':
        fileIndex = random.randint(0, 9)
        file = fileStore[fileIndex] #change world
        playMusic(musicStore[fileIndex])
        if level % worldSize == 0:
            powerScale += 1



#Made by Aakash Chakkinkal 2022
#HSC SDD Major Project
