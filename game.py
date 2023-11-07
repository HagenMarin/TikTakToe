# Example file showing a circle moving on screen
import pygame
import numpy as np
import math
from time import sleep, time
import random
import copy
from architecture import ResNet18
from architecture import BasicBlock
import torch

use_cuda = torch.cuda.is_available()
#for debugging it is sometimes useful to set the device to cpu as it usually gives more meaningful error messages
#device = torch.device("cpu")
device = torch.device("cuda" if use_cuda else "cpu")
print("Training on device:"+str(device))
thenet = ResNet18(img_channels=1, num_layers=18, block=BasicBlock, num_classes=2)
thenet.load_state_dict(torch.load('model/TestModel.pickle'))
thenet.to(device)
thenet.eval()

critic = ResNet18(img_channels=1, num_layers=18, block=BasicBlock, num_classes=1)
critic.load_state_dict(torch.load('ppo_critic.pth'))
critic.to(device)
critic.eval()


maincolor = 'white'
backgroundcolor = 'black'
secondarycolor = 'gray'
debug = False
player = True

def drawX(pos):
    return [pos-pygame.Vector2(width/(mapsize*2),height/(mapsize*2)),pos+pygame.Vector2(width/(mapsize*2),height/(mapsize*2)),pos,pos+pygame.Vector2(-width/(mapsize*2),height/(mapsize*2)),pos+pygame.Vector2(width/(mapsize*2),-height/(mapsize*2))]
def checkValid(idx1,idx2):
    neighbor = False
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if map[x][y]:
                neighbor = True
    return not map[idx1][idx2] and neighbor
def checkWin(idx1,idx2,map,mapsize):
    currentP = map[idx1][idx2]
    count = 0
    for i in range(max(0,idx1-4),min(idx1+5,mapsize)):
        if map[i][idx2]==currentP:
            count += 1
        else:
            count = 0
        if count == 5:
            return True
    count = 0
    for i in range(max(0,idx2-4),min(idx2+5,mapsize)):
        if map[idx1][i]==currentP:
            count += 1
        else:
            count = 0
        if count == 5:
            return True
    count = 0
    leftsteps = 4
    rightsteps = 5
    if max(idx1-4,0) == 0 or max(idx2-4,0)==0:
        leftsteps = min(idx1,idx2)
    if min(idx1 + 5,mapsize) == mapsize or min(idx2 + 5,mapsize) == mapsize:
        rightsteps = min(mapsize-idx1, mapsize-idx2)
    for i in range(-leftsteps,rightsteps):
        x = idx1+i
        y = idx2+i
        if map[x][y] == currentP:
                count += 1
        else:
            count = 0
        if count == 5:
            return True
    leftsteps = 4
    rightsteps = 5
    if max(idx1-4,0) == 0 or min(idx2 + 4,mapsize)==mapsize:
        leftsteps = min(idx1,mapsize - idx2-1)
    if min(idx1 + 5,mapsize) == mapsize or max(idx2-5,-1) == -1:
        rightsteps = min(mapsize-idx1, idx2 + 1)
    #print(f"rightsteps:{rightsteps}, leftsteps:{leftsteps}")
    for i in range(-leftsteps,rightsteps):
        x = idx1 + i
        y = idx2 - i
        if map[x][y] == currentP:
            count += 1
            #print(f"x:{x},y:{y},count:{count}")
        else:
            count = 0
        if count == 5:
            return True
    return False
def evaluatePos(idx1,idx2,map,mapsize,automatedPlayer):
    if debug:
        print(f"Checking Move:({idx1},{idx2})")
    currentP = map[idx1][idx2]
    quandary = False
    maxblocked = False
    count = 0
    maxcount = 0
    connected = False
    blocked = False
    first = True
    for i in range(max(0,idx1-4),min(idx1+5,mapsize)):
        if i == idx1:
            connected = True
        if map[i][idx2]==currentP:
            count += 1
            if map[i-1][idx2] == currentP*-1 and not first:
                blocked = True
        else:
            if count>maxcount and connected:
                maxcount = count
                if blocked:
                    maxblocked = True
            count = 0
            connected = False
        if count == 5:
            return 10
        first = False
    count = 0
    connected = False
    blocked = False
    first = True
    lastmax = maxcount
    for i in range(max(0,idx2-4),min(idx2+5,mapsize)):
        if i == idx2:
            connected = True
        if map[idx1][i]==currentP:
            count += 1
            if map[idx1][i-1] == currentP*-1 and not first:
                blocked = True
        else:
            if count>maxcount and connected:
                maxcount = count
                if lastmax >= 3:
                    quandary = True
                if blocked:
                    maxblocked = True
                else:
                    maxblocked = False
            count = 0
            connected = False
        if count == 5:
            return 10
        first = False
    count = 0
    leftsteps = 4
    rightsteps = 5
    connected = False
    blocked = False
    first = True
    lastmax = maxcount
    if max(idx1-4,0) == 0 or max(idx2-4,0)==0:
        leftsteps = min(idx1,idx2)
    if min(idx1 + 5,mapsize) == mapsize or min(idx2 + 5,mapsize) == mapsize:
        rightsteps = min(mapsize-idx1, mapsize-idx2)
    for i in range(-leftsteps,rightsteps):
        x = idx1+i
        y = idx2+i
        if not i:
            connected = True
        if map[x][y] == currentP:
            count += 1
            if map[x-1][y-1] == currentP*-1 and not first:
                blocked = True
        else:
            if count>maxcount and connected:
                maxcount = count
                if lastmax >= 3:
                    quandary = True
                if blocked:
                    maxblocked = True
                else:
                    maxblocked = False
            count = 0
            connected = False
        if count == 5:
            return 10
        first = False
    count = 0
    leftsteps = 4
    rightsteps = 5
    connected = False
    blocked = False
    first = True
    lastmax = maxcount
    if max(idx1-4,0) == 0 or min(idx2 + 4,mapsize)==mapsize:
        leftsteps = min(idx1,mapsize - idx2-1)
    if min(idx1 + 5,mapsize) == mapsize or max(idx2-5,-1) == -1:
        rightsteps = min(mapsize-idx1, idx2 + 1)
    
    # print(f"rightsteps:{rightsteps}, leftsteps:{leftsteps}")
    for i in range(-leftsteps,rightsteps):
        x = idx1 + i
        y = idx2 - i
        if debug:
            print(f"x:{x},y:{y}")
        if not i:
            connected = True
        if map[x][y] == currentP:
            count += 1
            if not first and map[x-1][y+1] == currentP*-1:
                blocked = True
            #print(f"x:{x},y:{y},count:{count}")
        else:
            if count>maxcount and connected:
                maxcount = count
                if lastmax >= 3:
                    quandary = True
                if blocked:
                    maxblocked = True
                else:
                    maxblocked = False
            count = 0
            connected = False
        if count == 5:
            return 10
        first = False
    if debug:
        print(f'Maxcount at Move ({idx1},{idx2}) blocked:{maxblocked}')
    if currentP == automatedPlayer:
        if maxblocked:
            if quandary:
                return max(0,maxcount-3)
            else:
                return max(0,maxcount-3.5)
        else:
            if quandary:
                return max(0,maxcount-1)
            else:
                return max(0,maxcount-2)
    else:
        if maxblocked:
            if quandary:
                return max(0,maxcount-3)
            else:
                return max(0,maxcount-4)
        else:
            if quandary:
                return max(0,maxcount-1.5)
            else:
                return max(0,maxcount-3)
def resetGame():
    map = np.zeros((mapsize,mapsize))
    circdrawpositions = []
    xdrawpositions = []
    firstMove = True
    validmoves = []
    return map,circdrawpositions,xdrawpositions,firstMove,validmoves
def updateValidMoves(idx1,idx2,mapcopy,validMoves):
    if (idx1,idx2) in validMoves:
        validMoves.remove((idx1,idx2))
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if not mapcopy[x][y] and (x,y) not in validMoves:
                validMoves.append((x,y))
    return validMoves
def breadthSearch(validMoves,currentPlayer,map):
    moveScores = dict()
    random.shuffle(validMoves)
    for tuple in validMoves:
        moveScores[tuple] = 0
    
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        if evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer) == 10:
            if debug:
                print(f"Winning move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer * -1
        if evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer) == 10:
            if debug:
                print(f"Defending move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validMoves:
        validMovesCopy = copy.deepcopy(validMoves)
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        moveScores[(x,y)] = moveScores[(x,y)] + evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer)
        validMovesDepth1 = updateValidMoves(x,y,depth1mapcopy,validMovesCopy)
        if debug:
            print(f'Move:({x},{y}), validMoves afterwards:{validMovesDepth1}')
        for (x1,y1) in validMovesDepth1:
            #validMovesDepth1Copy = copy.deepcopy(validMovesDepth1)
            depth2mapcopy = np.array(depth1mapcopy,copy=True)
            depth2mapcopy[x1][y1] = currentPlayer * -1
            moveScores[(x,y)] = moveScores[(x,y)] - evaluatePos(x1,y1,depth2mapcopy,mapsize,currentPlayer)
            #validMovesDepth2 = updateValidMoves(x1,y1,depth2mapcopy,validMovesDepth1Copy)
            '''for (x2,y2) in validMovesDepth2:
                depth3mapcopy = np.array(depth2mapcopy,copy=True)
                depth3mapcopy[x2][y2] = currentPlayer
                moveScores[(x,y)] = moveScores[(x,y)] + int(evaluatePos(x2,y2,depth3mapcopy,mapsize)*0.5)
                validMovesDepth3 = updateValidMoves(x2,y2,depth3mapcopy,copy.deepcopy(validMovesDepth2))
                for (x3,y3) in validMovesDepth3:
                    depth4mapcopy = np.array(depth3mapcopy,copy=True)
                    depth4mapcopy[x3][y3] = currentPlayer * -1
                    moveScores[(x,y)] = moveScores[(x,y)] - int(evaluatePos(x3,y3,depth4mapcopy,mapsize)*0.2)'''
                        
    moveScores = sorted(moveScores.items(),key=lambda tuple : tuple[1])
    if debug:
        print(moveScores)
    return moveScores[-1][0],moveScores
def executeStrat(validMoves,currentPlayer,map):
    moveScores = dict()
    for tuple in validMoves:
        moveScores[tuple] = 0
    
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        if checkWin(x,y,depth1mapcopy,mapsize):
            return (x,y)
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer * -1
        if checkWin(x,y,depth1mapcopy,mapsize):
            return (x,y)
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        validMovesDepth1 = updateValidMoves(x,y,depth1mapcopy,copy.deepcopy(validMoves))
        for (x1,y1) in validMovesDepth1:
            depth2mapcopy = np.array(depth1mapcopy,copy=True)
            depth2mapcopy[x1][y1] = currentPlayer
            if checkWin(x1,y1,depth2mapcopy,mapsize):
                moveScores[(x,y)] = moveScores[(x,y)] + 10
    for (x,y) in validMoves:
        depth1mapcopy = np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer * -1
        validMovesDepth1 = updateValidMoves(x,y,depth1mapcopy,copy.deepcopy(validMoves))
        for (x1,y1) in validMovesDepth1:
            depth2mapcopy = np.array(depth1mapcopy,copy=True)
            depth2mapcopy[x1][y1] = currentPlayer * -1
            if checkWin(x1,y1,depth2mapcopy,mapsize):
                print(f"Found Move with depth 2. x:{x1},y:{y1}")
                moveScores[(x,y)] = moveScores[(x,y)] + 5
    moveScores = sorted(moveScores.items(),key=lambda tuple : tuple[1])
    return moveScores.pop()[0]
# pygame setup
pygame.init()
screensize = 1080
screen = pygame.display.set_mode((screensize, screensize))
clock = pygame.time.Clock()
running = True
dt = 0
mapsize = 15
map = np.zeros((mapsize,mapsize))
width = screen.get_width()
height = screen.get_height()
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
middle = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
circdrawpositions = []
xdrawpositions = []
validmoves = []
movescores = []
currentplayer = 1
firstMove = True
alreadypressed = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            print("Quitting")

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(backgroundcolor)
    # draw the grid
    for i in range(1,mapsize):
        pygame.draw.line(screen, secondarycolor,pygame.Vector2(width/mapsize * i,0),pygame.Vector2(width/mapsize * i,height),3)
        pygame.draw.line(screen, secondarycolor,pygame.Vector2(0,height/mapsize * i),pygame.Vector2(width,height/mapsize * i),3)
    # variable that keeps track if somebody won
    won = False
    # check if the left mouse button was pressed
    mouse1, _, _ = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_d] and not debug and not alreadypressed:
        debug = True
        alreadypressed = True
    elif keys[pygame.K_d] and not alreadypressed:
        debug = False
        alreadypressed = True
    if not keys[pygame.K_d]:
        alreadypressed = False
    if keys[pygame.K_p] and not player:
        player = True
        if debug:
            print(f"player mode:{player}")
        sleep(0.5)
    elif keys[pygame.K_p]:
        player = False
        if debug:
            print(f"player mode:{player}")
        sleep(0.5)
    if mouse1 or currentplayer == -1 or not player:
        if currentplayer == 1 and player:
            # get the mouse position and calculate the corrosponding indeces
            x,y = pygame.mouse.get_pos()
            index1 = math.floor(x*mapsize/width)
            index2 = math.floor(y*mapsize/height) 
        else:
            if firstMove:
                validmoves.append((int(mapsize/2),int(mapsize/2)))
            x = torch.tensor(map,dtype=torch.float32)
            x = torch.reshape(x,(1,1,mapsize,mapsize))
            x = x.to(device)
            out = thenet(x)
            print(f"Critic says:{critic(x)}")
            print(out)
            (index1,index2),movescores = breadthSearch(validmoves,currentplayer,map)
            if checkValid(round(out[0][0].item()),round(out[0][1].item())):
                print("Using Model")
                index1 = round(out[0][0].item())
                index2 = round(out[0][1].item())
        # check if the move is valid 
        if checkValid(index1,index2) or firstMove:
            firstMove = False
            map[index1][index2] = currentplayer
            validmoves = updateValidMoves(index1,index2,map,validmoves)
            won = checkWin(index1,index2,map,mapsize)
            # append the move position to the draw lists
            if currentplayer == 1:
                xdrawpositions.append(pygame.Vector2((index1+0.5)*width/mapsize,(index2+0.5)*height/mapsize))
            else:
                circdrawpositions.append(pygame.Vector2((index1+0.5)*width/mapsize,(index2+0.5)*height/mapsize))
            currentplayer = -1 * currentplayer
    
    # draw the Xs and the Os
    for pos in circdrawpositions:
        pygame.draw.circle(screen,maincolor,pos,width/(mapsize*2) - 2,5)
    for pos in xdrawpositions:
        pygame.draw.lines(screen,maincolor,False,drawX(pos),5)
    if debug:
        for (idx1,idx2),score in movescores:
            pos = pygame.Vector2((idx1)*width/mapsize,(idx2)*height/mapsize)
            pos1 = pygame.Vector2((idx1)*width/mapsize,(idx2 + 0.5)*height/mapsize)
            pygame.font.init()
            my_font = pygame.font.SysFont('Comic Sans MS', 24)
            my_font1 = pygame.font.SysFont('Comic Sans MS', 40)
            text_surface = my_font.render(f'{score}', False, secondarycolor)
            text_surface1 = my_font.render(f'{idx1},{idx2}',False,secondarycolor)
            screen.blit(text_surface, pos)
            screen.blit(text_surface1,pos1)

    # check if somebody won
    if won:
        # reset the Game
        map,circdrawpositions,xdrawpositions,firstMove,validmoves = resetGame()
        # create a Text overlay
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', 60)
        if currentplayer == -1:
            winner = "X"
        else:
            winner = "O"
        text_surface = my_font.render(f'{winner} Won the game!', False, maincolor)
        screen.blit(text_surface, pygame.Vector2(0,0))


    # flip() the display to put your work on screen
    pygame.display.flip()
    if won:
        # show the text overlay for 5 seconds(the game is paused)
        sleep(5)
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
