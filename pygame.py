# Squirrel Eat Squirrel (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
#Adrian Pun - AP
#Jeff Chen - JC
#Noaah Karim - NK
#Manroop Sandhu - MS

import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30 # frames per second to update the screen
WINWIDTH = 640 # width of the program's window, in pixels
WINHEIGHT = 480 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2) # NK half the width of the program's window, in pixels
HALF_WINHEIGHT = int(WINHEIGHT / 2) # NK half the height of the program's window, in pixels

GRASSCOLOR = (24, 255, 0) #NK Hue for grass
WHITE = (255, 255, 255) #NK Hue for white
RED = (255, 0, 0) #NK Hue for red

CAMERASLACK = 90     # how far from the center the squirrel moves before moving the camera
MOVERATE = 9         # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30    # how high the player bounces
STARTSIZE = 25       # how big the player starts off
WINSIZE = 300        # how big the player needs to be to win
INVULNTIME = 2       # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4     # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3        # how much health the player starts with

NUMGRASS = 80        # number of grass objects in the active area
NUMSQUIRRELS = 30    # number of squirrels in the active area
SQUIRRELMINSPEED = 3 # slowest squirrel speed
SQUIRRELMAXSPEED = 7 # fastest squirrel speed
DIRCHANGEFREQ = 2    # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

"""
This program has three data structures to represent the player, enemy squirrels, and grass background objects. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.
Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger squirrel before dying.
Enemy Squirrel data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'movex' - how many pixels per frame the squirrel moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the squirrel moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the squirrel's image, in pixels
    'height' - the height of the squirrel's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the squirrel bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the squirrel bounces
Grass data structure keys:
    'grassImage' - an integer that refers to the index of the pygame.Surface object in GRASSIMAGES used for this grass object
"""

def main():
    # NK Variables accessed outside the function
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES

    # NK Initialize pygame modules
    pygame.init()
    # NK Sets the frames per second to be based around the pygame clock
    FPSCLOCK = pygame.time.Clock()
    # NK Sets game window icon
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    # NK Sets game window size
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    # NK Sets game title at top of window
    pygame.display.set_caption('Squirrel Eat Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_SQUIR_IMG = pygame.image.load('squirrel.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    # NK Adds grass images together into a list
    GRASSIMAGES = []
    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    # NK Infinite loop that runs the game
    while True:
        runGame()


def runGame():
    #AP: Variables defined in the game
    invulnerableMode = False  # AP: default set up of the player where they aren't invunlerable at start (Determine if the player is invunlerable)
    invulnerableStartTime = 0 # AP: The count time variable when the player is invunlerable (default time = 0)
    gameOverMode = False      # AP: default set up of the player where they aren't game over at start (Determine if the player has lost)
    gameOverStartTime = 0     # AP: The count time variable when the player is lost (default time = 0)
    winMode = False           # AP: The default set up where the player hasn't won (Determine if the player has win)

    #AP: Set up for text when player loses
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE) #AP:Defined Variable that creates a 'surface' for text (using methods '.render') where it adapts BASICFONT (for fonts) 
                                                              # to print 'Game Over' with smooth edge since the second argument (determine if
                                                              # the smooth edge is wanted with boolean value) is true with the text being white as
                                                              #it has the variable WHITE on 3rd argument (defines color)
                                                              
    gameOverRect = gameOverSurf.get_rect() #AP:Defined a variable that creates a rect (rectangle) for the variable above (using method '.get_rect()')
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT) #AP:moves the center of the rect that has been previously defined(since it uses method '.center') to the designated 
                                                          #coordinate (320,240) since the two variables are previously defined. Note that the coordinate is format as (x,y) 
    #AP: End of the set up for text when player loses
    
    
    #AP: Set up for text when player wins
    winSurf = BASICFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE) #AP: Defined a variable that create a 'surface' for text (using methods '.render') where it adapts 
                                                                                  #BASICFONT (for fonts) to print 'You have achieved OMEGA SQUIRREL!' (It is a string.) with smooth edge since the 
                                                                                  #second argument (determine if the smooth edge is wanted with boolean variable) is 
                                                                                  #true with the text being white as it has the variable WHITE on 3rd argument (defines color)
                                                                                  
    winRect = winSurf.get_rect() #AP: Defined a variable that creates a rect (rectangle) for the variable above (using method '.get_rect()')
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)#AP: moves the center of the rect that has been previously defined (since it uses method '.center') to the designated coordinate (320,240) 
                                                    #since the two variables are previously defined. Note that the coordinate is format as (x,y) 

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE) #Defines another variable to print another box that creates a 'surface' for text (using methods '.render') where it 
                                                              #adapts BASICFONT (for fonts)  to print '(Press "r" to restart.)' with smooth edge since the second argument (determine if
                                                              # the smooth edge is wanted with boolean value) is true with the text being white as
                                                              #it has the variable WHITE on 3rd argument (defines color)
                                                              
    winRect2 = winSurf2.get_rect() #AP: Defined a variable that creates a rect (rectangle) for the variable above (using method '.get_rect()')
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)#AP: moves the center of the rect that has been previously defined (since it uses method '.center') to the designated coordinate 
                                                          #(320,270) -> note that the coordinate is changed since the author added 30 steps up to y coordinate (240+30 = 270)
                                                          #since the two variables are previously defined. Note that the coordinate is format as (x,y) 
    #AP: End of the set up for text when player wins

    #AP: Set up of camera view
    camerax = 0 #define camerax variable as 0 
    cameray = 0 #define cameray variable as 0
    #The camera view is in the origin (0,0) by default
    
    #set up of backgrounds
    grassObjs = []    # AP: Variable that defined a list that stores all grass objects (Default: empty)
    squirrelObjs = [] # AP: Variable that defined a list that stores all the non-player squirrel objects (Default: empty)
    
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0,
                 'health': MAXHEALTH} #AP:It is a variable that is a python dictionary that describes the appearance and behavior of the squirrel. 
                                        #surface is the size and face of squirrel. Using method '.transform.scale', it transforms the squirrel to
                                        #the L_SQUIR_IMG (image of squirrel stored) with size (25,25) -> (width of image, height of image)
                                        
                                        #AP: facing is the default direction of the squirrel facing. It is looking to left
                                        #size is the size in default (its size is 25)
                                        #x and y describe the horizontal and veritcal position of squirrel respectively (its position is 320 and 240 respectively)
                                        #squirrel doesn't bounce in default as bounce is 0
                                        #health determines how many health the squirrel has. Default is 3
                                        
    #AP: Here defines the default movement of squirrel (all are False in default to ensure the squrriel in rest unless users input movement)
    moveLeft  = False  #AP: boolean variable defined when the squirrel moves towards left (default is False)
    moveRight = False  #AP: boolean variable defined when the squirrel moves towards right (default is False)
    moveUp    = False  #AP: boolean variable defined when the squirrel moves towards up (default is False)
    moveDown  = False  #AP: boolean variable defined when the squirrel moves towards down (default is False)

    for i in range(10): #AP: for loop that run 10 times
        grassObjs.append(makeNewGrass(camerax, cameray)) #AP: get dictionary from makeNewGrass function and add them to the list (the function creates grass)
        grassObjs[i]['x'] = random.randint(0, WINWIDTH) #AP: get a random integer from 0 to WINWIDTH value and replace it in the 'x' in dictionary in index i 
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT) #AP: get a random integer from 0 to WINHEIGHT value and replace it in the 'y' in dictionary in index i 
        #AP: this for loop can make new grass because the area of grass and its rectangle of the image of the grass is created. 
        
    while True: #AP: main game loop (never exits until it breaks)
        #AP: check if the invulnerable mode should turn on
        if invulnerableMode and time.time() - invulnerableStartTime > INVULNTIME: #AP: if condition for invulnerable Mode is True and if time since epoch minus invulnerableStartTime is larger than INVULNTIME
            invulnerableMode = False #AP: reset variable if this condition enters

        #AP: for loop to move NPC squirrels
        for sObj in squirrelObjs: 
            sObj['x'] += sObj['movex'] #AP: determine the x direction of squirrel. It does so because the value of the key 'x' is redefined to add the random number of x velocity of 'movex' key's value
            sObj['y'] += sObj['movey'] #AP: determine the y direction of squirrel. It does so because the value of the key 'y' is redefined to add the random number of y velocity of 'movey' key's value
            sObj['bounce'] += 1 #AP: every time it moves the bounce key's value is added by 1
            if sObj['bounce'] > sObj['bouncerate']: #AP: if condition for the bounce key value is too high (i.e. higher the value is higher than the maximum bounce value that is set)
                sObj['bounce'] = 0 # AP: reset the bounce key's value to 0

            #Randomly change squirrel's direction
            if random.randint(0, 99) < DIRCHANGEFREQ: #AP: get a random integer and if it is 0 or 1 (i.e. less than the numeric variable DIRCHANGEFREQ, 2), enter if condition
                sObj['movex'] = getRandomVelocity() #AP: determine the new x direction of squirrel. It does so because the value of the key 'x' is redefined to add the random number of x velocity of 'movex' key's value 
                sObj['movey'] = getRandomVelocity() #AP: determine the new y direction of squirrel. It does so because the value of the key 'y' is redefined to add the random number of y velocity of 'movey' key's value
                if sObj['movex'] > 0: # if condition for if x is larger than 0
                    sObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sObj['width'], sObj['height'])) #AP: makes it faces right since it transform the image of 
                                                                                                            #the squirrel facing right to its squirrel width and height using method .transform (transform the image)
                                                                                                            #to transform to its designated width and height
                else: #AP: else condition if not larger than 0
                    sObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sObj['width'], sObj['height']))
                    #AP: makes it faces right since it transform the image of 
                    #the squirrel facing left to its squirrel width and height using method .transform (transform the image)
                    #to transform to its designated width and height


        # go through all the objects and see if any need to be deleted.
        for i in range(len(grassObjs) - 1, -1, -1): #AP: enter a for loop to let i start from the largest index number of list grassObjs until it reaches -1, jump -1 every time
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]): #AP: if condition for checking if when calling function isOutsideActiveArea return True for grass objects
                del grassObjs[i] #AP: if yes, delete the last item in the list (index i) (i.e. delete the furthest grass in game)
        for i in range(len(squirrelObjs) - 1, -1, -1): #AP: enter a for loop to let i start from the largest index number of list squirrelObjs until it reaches -1, jump -1 every time
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]): #AP: if condition for calling and checking if function isOutsideActiveArea return True for squirrels objects
                del squirrelObjs[i] #AP: if yes, delete the last item in the list (index i) (i.e. delete the furthest grass in game)

        # add more grass & squirrels if we don't have enough.
        while len(grassObjs) < NUMGRASS: #AP: enter while loop if the length of grassObjs is less than the designated value of minimum number of grass (NUMGRASS variable) until it reaches the minimum
            grassObjs.append(makeNewGrass(camerax, cameray)) #AP: add grass objects at the end of the list
        while len(squirrelObjs) < NUMSQUIRRELS: #AP: enter while loop if the length of squirrelObjs is less than the designated value of minimum number of NPC squirrels (NUMSQUIRREL variable) until it reaches the minimum
            squirrelObjs.append(makeNewSquirrel(camerax, cameray))#AP: add squirrel objects at the end of the list


        #AP: adjust camera angle
        playerCenterx = playerObj['x'] + int(playerObj['size'] / 2) #AP: define the center of player in x position as the x position of player plus half of the player's size (from dictionary of player; get 'x' and 'size' key)
        playerCentery = playerObj['y'] + int(playerObj['size'] / 2) #AP: define the center of player in y position as the y position of player plus half of the player's size (from dictionary of player; get 'x' and 'size' key)
        #AP: if camera position x is too right
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK: #AP: if condition to compare the sum of camerax position plus half window width minus player centre x to CAMERASLACK (how far squirrel moves from centre before camera moves)
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH #AP: if the camerax+halfWINWIDTH-playerCenterx is larger than CAMERASLACK, reset the camerax position to 
                                                                    #player center x plus how far squirrel moves from centre before camera moves minus half window width to move right to ensure it is tracking the squirrel
        #AP: else if camera position x is too left
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK: #AP: take the expression above and times negative in else if since they represent when the camera position is too left. 
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH #AP: did the same equation above but since player is moving left, the cameraslack is negative to make the camera move left to ensure it is tracking the squirrel
        
        #AP: if camera position y is too high

        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK: #AP: if condition to compare the sum of cameray position plus half window width minus player centre y to CAMERASLACK (how far squirrel moves from centre before camera moves)
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT #AP: if the cameray+halfWINWIDTH-playerCentery is larger than CAMERASLACK, reset the cameray position to 
                                                                    #player center y plus how far squirrel moves from centre before camera moves minus half window width to move up to ensure it is tracking the squirrel
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK: #AP: take the expression above and times negative in else if since they represent when the camera position is too low. 
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT #AP: did the same equation above but since player is moving down, the cameraslack is negative to make the camera move down to ensure it is tracking the squirrel

        DISPLAYSURF.fill(GRASSCOLOR) #use builtin variable and method DISPLAYSURF.fill to fill the grass color (just the color, not grass) 

        for gObj in grassObjs: #AP: call for loop to draw grass, range is the length of the list grassObjs
            gRect = pygame.Rect( (gObj['x'] - camerax,
                                  gObj['y'] - cameray,
                                  gObj['width'],
                                  gObj['height']) ) #AP: define gRect to create rectangles with properties:
                                                    #x position is random integer obtained previously in grassObjs[i]['x'] - camerax angle to draw outside of camerax range
                                                    #y position is random integer obtained previously in grassObjs[i]['y'] - cameray angle to draw outside of cameray range
                                                    #width is equal to the width of image (previously found in MakeNewGrass function)
                                                    #height is equal to the height of image (previously found in MakeNewGrass function)
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect) #AP: use method .blit to build grass image taken from the list GRASSIMAGE with respect of the properties of gRect defined above. 


        # draw the other squirrels
        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect( (sObj['x'] - camerax,
                                         sObj['y'] - cameray - getBounceAmount(sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                                         sObj['width'],
                                         sObj['height']) )#AP: define sObj['rect'] (rectangle/surface for squirrels) to create rectangles with properties:
                                                           #x position is random integer obtained previously in squirrelObjs[i]['x'] - camerax angle to draw outside of camerax range
                                                           #y position is random integer obtained previously in squirrelObjs[i]['x'] - cameray angle to draw outside of cameray range - bounce rate obtained from getBounceAmount function
                                                           #width is equal to the width of image (previously found in MakeNewSquirrel function)
                                                           #height is equal to the height of image (previously found in MakeNewSquirrel function)
            DISPLAYSURF.blit(sObj['surface'], sObj['rect']) #AP: use method .blit to build grass image taken from the list playerObj with respect of the properties of gRect defined above. 
            

#-- AP--
        # draw the player squirrel
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        # MS: this variable rounds the value for flashison to a single decimal place, and then every 0.1s the expression alternates between True and False      
        if not gameOverMode and not (invulnerableMode and flashIsOn):
        # MS: if the player has won and not invulnerable and also 
            playerObj['rect'] = pygame.Rect( (playerObj['x'] - camerax,
                                              playerObj['y'] - cameray - getBounceAmount(playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                                              playerObj['size'],
                                              playerObj['size']) )
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])
        # MS: this line converts the player's world position into a rectangle on the screen. it adjusts for camera scrolling and bounce animation so that pygame can detect a collision.

        # draw the health meter
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
        # MS: the event.type is the last action that took plae on the screen. if the user clicks the X out button, as in QUIT, then it exits the game.

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
            # MS: if the player clicks the UP arrow button or the W key on their keyboard, then turn off moving down, and turn on moving up. Since the user wants to move up.
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
            # MS: if the player clicks the DOWN arow or the S key on the keyboard, then essentially "turn on" moveDown by making it equal True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
            # MS: if the player clicks the LEFT arrow or the A key on the keybaord, then essentially "turn on" moving left by making the statement equal True
                    if playerObj['facing'] != LEFT: # change player image
            # MS: if the squirrels face is not facing left, continue with the rest of the code.
                        playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
            # MS: if the squirrels face is not facing left, it sets the image displayed on the screen to the preloaded left-facing picture.
                    playerObj['facing'] = LEFT
            # MS: update the squirrels direction
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
            # MS: if the player clicks the RIGHT arrow key or the d key on the keyboard, make "moveRight" equal to True so that the squirrel moves right.
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))
            # MS: if the squirrels image is not facing right, set the surface image displayed to show the preloaded right-facing picture.
                    playerObj['facing'] = RIGHT
            # MS: update the squirrels direction        
                elif winMode and event.key == K_r:
                    return
            # MS: if the player wins and presses restart on the game, exit the loop.

            elif event.type == KEYUP:
                # stop moving the player's squirrel
            # MS: if the pressed uo goes from being pressed down to up, then...
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
            # MS: the player stops moving left
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
            # MS: the player stops moving right
                elif event.key in (K_UP, K_w):
                    moveUp = False
            # MS: the player stops moving up
                elif event.key in (K_DOWN, K_s):
                    moveDown = False
            # MS: the player stops moving down

                elif event.key == K_ESCAPE:
                    terminate()
            # if the player hits the escape button, exit the program.

        if not gameOverMode:
            # MS: checks if the game is over. if gameOvermode==True, then it skips this block of code.
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            # MS: if the player moves left, it will subtract that amount of moves from the players current location in terms of the x axis.
            if moveRight:
                playerObj['x'] += MOVERATE
            # MS: if the player moves left, it will add that amount of moves from the players current x location in terms of the x axis.
            if moveUp:
                playerObj['y'] -= MOVERATE
            # MS: if the player moves up, subtract that amount of moves from the players current location in terms of the y axis. 
            if moveDown:
                playerObj['y'] += MOVERATE
            # MS: if the player moves down, add that amount of moves from the players current location in terms of the y-value of the players coordinate. 

            if (moveLeft or moveRight or moveUp or moveDown) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1
            # MS: if the player moves at all or if the bounce animation is already in action, then have the squirrel start to bounce or continue to bounce. 

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount
            # MS: if the player has reached the bounce limit, reset the bounce amount.

            # check if the player has collided with any squirrels
            for i in range(len(squirrelObjs)-1, -1, -1):
            # MS: start the loop at the last index, stop at index -1. bascially moving backwards by -1 through each index.
            # MS: a backwards loop is used so that when items are removed or replaced, it does not shift the indices and possibly break the loop.
                sqObj = squirrelObjs[i]
            # MS: goes into the squirrel dictionary
                if 'rect' in sqObj and playerObj['rect'].colliderect(sqObj['rect']):
                    # a player/squirrel collision has occurred

                    if sqObj['width'] * sqObj['height'] <= playerObj['size']**2:
                        # player is larger and eats the squirrel
                        playerObj['size'] += int( (sqObj['width'] * sqObj['height'])**0.2 ) + 1
                        # MS: if the player eats the squirrel, make the player larger in size. the bigger the squirrel, the bigger the player gets.
                        del squirrelObjs[i]
                        # MS: squirrel disapears after the players eats it.

                        if playerObj['facing'] == LEFT:
                            playerObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                        # MS: rescale the players image
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (playerObj['size'], playerObj['size']))
                        # MS: rescale the players image

                        if playerObj['size'] > WINSIZE:
                            winMode = True # turn on "win mode"
                        # MS: if the player is greater than the winning size, than the player has won.

                    elif not invulnerableMode:
                        # player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        # MS: prevents the player from taking too much damage in one collision.
                        playerObj['health'] -= 1
                        # MS: the players health is reduced.
                        if playerObj['health'] == 0:
                            gameOverMode = True # turn on "game over mode"
                            gameOverStartTime = time.time()
                        # MS: if the players health is equal to zero, the game is over.
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
            # MS: exit the loop after a few seconds
                return # end the current game

        # check if the player has won.
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
        # MS: if the player has won, display the the win screen
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        # MS: updates the pygame window
        FPSCLOCK.tick(FPS)


def drawHealthMeter(currentHealth): #AP: Define a function to draw health bar
    for i in range(currentHealth): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED,   (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10)) #AP: display a rectangle to draw red bars as many times as the current health (since it runs as many times as the current health)
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)#AP: display a rectangle to draw white bars as many times as the max health (since it runs as many times as the max health)
    #AP: this can outline the total health out of the max health

def terminate():
    #JC: ends the game and exits the terminal 
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)

def getRandomVelocity():
    # NK allows the squirrels to run at random speeds in the game
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        # NK generates random coordinates in a large zone around the camera
        # NK using the top left point of the camera as a basis
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # NK create a Rect object with the random coordinates and use colliderect()
        # NK to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        # NK returns True if the object's rectangle touches the camera's rectangle
        # NK and returns False if the object's rectangle does not overlap with the camera's rectangle
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewSquirrel(camerax, cameray):
    # JC: these defined variables set the basis for the size of all squirrels 
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    # JC: these defined variables give the squirrels a random size by multiplying their base size 
    #JC:  larger randint creates a larger image of the squirrel both vertically and horizontally 
    sq['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    # JC: randomly spawns the squirrels outside of the camera position 
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    # JC: assigns random velocity to squirrels in terms of horizontal and vertical velocity 
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    if sq['movex'] < 0: # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else: # squirrel is facing right
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    # JC: provides random bounce animation for squirrels 
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    gr = {}
    # JC: creates random size for grass images 
    # JC: chooses a random image of grass JC
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    # JC: larger get_width means the grass image is wider 
    # JC: larger get_height means the grass image is taller 
    gr['width']  = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    # JC: spawns the grass off camera 
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    # NK Return False if camerax and cameray are more than
    # NK a half-window length beyond the edge of the window.
    # NK calculates the differences between the top left point of the camera and the dimensions of the window, then assigns them as boundaries
    boundsLeftEdge = camerax - WINWIDTH 
    boundsTopEdge = cameray - WINHEIGHT
    # NK creates a rectangle three times the size of the window's dimensions using the boundaries as starting points
    # NK to represent the active area
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    # NK creates a rectangle using the position and dimensions of a given object
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    # NK checks if the rectangle encapsulating a given object is within the rectangle encapsulating the active area
    # NK returns True if the object is not inside the active area
    # NK returns False if it is inside the active area
    return not boundsRect.colliderect(objRect) 

if __name__ == '__main__':
    main()
