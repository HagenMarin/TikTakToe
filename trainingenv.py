import numpy as np
import math
from time import sleep, time
import random
import copy
from pathlib import Path
import pickle
import torch
from numba import njit



@njit
def checkValid(idx1,idx2,mapsize):
    neighbor = False
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if map[x][y]:
                neighbor = True
    return not map[idx1][idx2] and neighbor
@njit
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
@njit
def evaluatePos(idx1,idx2,map,mapsize,automatedPlayer,debug):
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
def resetGame(mapsize):
    map = np.zeros((mapsize,mapsize))
    firstMove = True
    validmoves = []
    return map,firstMove,validmoves
@njit
def updateValidMoves(idx1,idx2,mapcopy,validMoves,mapsize):
    if (idx1,idx2) in validMoves:
        validMoves.remove((idx1,idx2))
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if not mapcopy[x][y] and (x,y) not in validMoves:
                validMoves.append((x,y))
    return validMoves
@njit
def breadthSearch(validMoves,currentPlayer,map,debug,mapsize):
    moveScores = dict()
    
    for tuple in validMoves:
        moveScores[tuple] = 0.0
    
    for (x,y) in validMoves:
        depth1mapcopy = map.copy() # np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        if evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer,debug) == 10:
            if debug:
                print(f"Winning move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validMoves:
        depth1mapcopy = map.copy() #np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer * -1
        if evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer,debug) == 10:
            if debug:
                print(f"Defending move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validMoves:
        validMovesCopy = validMoves.copy()#copy.deepcopy(validMoves)
        depth1mapcopy = map.copy()#np.array(map, copy=True)
        depth1mapcopy[x][y] = currentPlayer
        moveScores[(x,y)] = moveScores[(x,y)] + evaluatePos(x,y,depth1mapcopy,mapsize,currentPlayer,debug)
        validMovesDepth1 = updateValidMoves(x,y,depth1mapcopy,validMovesCopy,mapsize)
        if debug:
            print(f'Move:({x},{y}), validMoves afterwards:{validMovesDepth1}')
        for (x1,y1) in validMovesDepth1:
            #validMovesDepth1Copy = copy.deepcopy(validMovesDepth1)
            depth2mapcopy = depth1mapcopy.copy()#np.array(depth1mapcopy,copy=True)
            depth2mapcopy[x1][y1] = currentPlayer * -1
            moveScores[(x,y)] = moveScores[(x,y)] - evaluatePos(x1,y1,depth2mapcopy,mapsize,currentPlayer,debug)
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

def main():
    cwd = Path.cwd()
    debug = False
    player = False
    totalcount = 0
    starttime = time()
    lasttime = starttime
    batch_size = 128
    # pygame setup
    running = True
    dt = 0
    mapsize = 15
    map = np.zeros((mapsize,mapsize))
    validmoves = []
    movescores = []
    currentplayer = 1
    firstMove = True
    alreadypressed = False
    searchcount = 0
    timetotal = 0
    movecount = 0
    images = torch.zeros((128,1,15,15),dtype=torch.float32)
    labels = torch.zeros((128,2),dtype=torch.float32)
    samples = 0
    batchcount = 0
    for i in range(200000):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window

        # fill the screen with a color to wipe away anything from last frame
        # variable that keeps track if somebody won
        won = False
        # check if the left mouse button was pressed
        
        
        

        if firstMove:
            validmoves.append((int(mapsize/2),int(mapsize/2)))
            
        if len(validmoves) != 0:
            random.shuffle(validmoves)
            (index1,index2),movescores = breadthSearch(validmoves,currentplayer,map,debug,mapsize)
            searchcount += 1
            movecount += 1
            if movecount > 15*15:
                print(validmoves)
                print(map)
                quit()
            '''if not checkValid(index1,index2) and not firstMove:
                
                print(f"index1:{index1},index2:{index2}")
                print(map)
                quit()'''
            # check if the move is valid 
            '''if checkValid(index1,index2) or firstMove:
                firstMove = False'''
            if currentplayer == -1:
                x = torch.tensor(map)
                map[index1][index2] = currentplayer
            else:
                x = torch.tensor(map*-1)
                map[index1][index2] = currentplayer
            labels[samples][0] = index1
            labels[samples][1] = index2    
            images[samples][0] = x
            
            samples += 1
            validmoves = updateValidMoves(index1,index2,map,validmoves,mapsize)
            won = checkWin(index1,index2,map,mapsize)
            # append the move position to the draw lists
            currentplayer = -1 * currentplayer
            firstMove = False
            if samples == batch_size:
                filename = str(cwd)+ '/train_batches_regr_'+str(batch_size)+'/batch_'+str(batchcount)+'.pickle'
                print(filename)
                with open(filename, 'wb+') as handle:
                    pickle.dump((images,labels), handle, protocol=pickle.HIGHEST_PROTOCOL)
                samples = 0
                batchcount += 1
        else:
            won = True
        
        # draw the Xs and the Os

        # check if somebody won
        if won:
            movecount = 0
            # reset the Game
            map,firstMove,validmoves = resetGame(mapsize)
            totalcount += 1
            if totalcount%100 == 0:
                print(f"Count:{totalcount}, time since start:{time()-starttime}, time for last:{time()-lasttime}, average num search per game:{searchcount/totalcount}")
                lasttime = time()
            # create a Text overlay



    # flip() the display to put your work on screen
    
    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.

if __name__=="__main__":
    main()