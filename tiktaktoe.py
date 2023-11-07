import numpy as np
import torch
import random
import pygame
from numba import njit
from time import sleep

@njit
def _breadthSearch(validmoves,currentplayer,debug,map,mapsize,automatedPlayer):
    moveScores = dict()
    
    for tuple in validmoves:
        moveScores[tuple] = 0.0
    
    for (x,y) in validmoves:
        depth1mapcopy = map.copy() # np.array(map, copy=True)
        depth1mapcopy[x][y] = currentplayer
        if _evaluatePos(x,y,depth1mapcopy,debug,mapsize,automatedPlayer) == 10:
            if debug:
                print(f"Winning move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validmoves:
        depth1mapcopy = map.copy() #np.array(map, copy=True)
        depth1mapcopy[x][y] = currentplayer * -1
        if _evaluatePos(x,y,depth1mapcopy,debug,mapsize,automatedPlayer) == 10:
            if debug:
                print(f"Defending move at ({x},{y})")
            return (x,y),sorted(moveScores.items(),key=lambda tuple : tuple[1])
    for (x,y) in validmoves:
        validMovesCopy = validmoves.copy()#copy.deepcopy(validMoves)
        depth1mapcopy = map.copy()#np.array(map, copy=True)
        depth1mapcopy[x][y] = currentplayer
        moveScores[(x,y)] = moveScores[(x,y)] + _evaluatePos(x,y,depth1mapcopy,debug,mapsize,automatedPlayer)
        validMovesDepth1 = _updateValidMoves(x,y,depth1mapcopy,validMovesCopy,mapsize)
        if debug:
            print(f'Move:({x},{y}), validMoves afterwards:{validMovesDepth1}')
        for (x1,y1) in validMovesDepth1:
            #validMovesDepth1Copy = copy.deepcopy(validMovesDepth1)
            depth2mapcopy = depth1mapcopy.copy()#np.array(depth1mapcopy,copy=True)
            depth2mapcopy[x1][y1] = currentplayer * -1
            moveScores[(x,y)] = moveScores[(x,y)] - _evaluatePos(x1,y1,depth2mapcopy,debug,mapsize,automatedPlayer)
                        
    moveScores = sorted(moveScores.items(),key=lambda tuple : tuple[1])
    if debug:
        print(moveScores)
    return moveScores[-1][0],moveScores
@njit
def _evaluatePos(idx1,idx2,map,debug,mapsize,automatedPlayer) -> int:
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
@njit
def _updateValidMoves(idx1 : int,idx2 : int,mapcopy : np.array,validMoves : list[tuple],mapsize: int) -> list[tuple]:
    if (idx1,idx2) in validMoves:
        validMoves.remove((idx1,idx2))
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if not mapcopy[x][y] and (x,y) not in validMoves:
                validMoves.append((x,y))
    return validMoves
@njit
def _checkWin(idx1,idx2, map,mapsize):
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
def _checkValid(idx1,idx2,mapsize,map):
    if not (idx1>0 and idx1<mapsize) or not (idx2>0 and idx2<mapsize):
        return False
    neighbor = False
    for x in range(max(idx1-1,0),min(idx1 + 2,mapsize)):
        for y in range(max(idx2-1,0),min(idx2 + 2,mapsize)):
            if map[x][y]:
                neighbor = True
    return not map[idx1][idx2] and neighbor

class env():

    def __init__(self, mapsize: int):
        self.mapsize = mapsize
        self.map = np.zeros((mapsize,mapsize))
        self.validmoves = []
        self.currentplayer = 1
        self.firstMove = True
        self.debug = False
        self.automatedPlayer = -1
        self.movecount = 0
        self.done = False
        self.rendering = False
        self.maincolor = 'white'
        self.backgroundcolor = 'black'
        self.secondarycolor = 'gray'
    def step(self,action: np.array) -> (torch.tensor, int, bool, int):
        if self.rendering:
            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill(self.backgroundcolor)
            # draw the grid
            for i in range(1,self.mapsize):
                pygame.draw.line(self.screen, self.secondarycolor,pygame.Vector2(self.width/self.mapsize * i,0),pygame.Vector2(self.width/self.mapsize * i,self.height),3)
                pygame.draw.line(self.screen, self.secondarycolor,pygame.Vector2(0,self.height/self.mapsize * i),pygame.Vector2(self.width,self.height/self.mapsize * i),3)
        action = action[0]
        reward = 0
        self.done = False
        if self.firstMove:
            self.validmoves.append((int(self.mapsize/2),int(self.mapsize/2)))
            
        if len(self.validmoves) != 0:
            if self.movecount > 15*15:
                print(self.validmoves)
                print(self.map)
                quit()
            if self.currentplayer == -1:
                index1 = round(action[0])
                index2 = round(action[1])
                if not self.checkValid(index1,index2):
                    if self.rendering:
                        print(f"invalid move:{action}")
                    self.firstMove = False
                    reward = -1
                    #obs = torch.tensor(self.map,dtype=torch.float32)
                    #obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))
                    #return obs,reward,self.done,self.movecount
                    self.movecount += 1
                    index1, index2 = self.validmoves[0]
                    self.map[index1][index2] = self.currentplayer
                    self.currentplayer = self.currentplayer * -1
                    self.validmoves = self.updateValidMoves(index1,index2,self.map,self.validmoves)
                    if self.rendering:
                        self.circdrawpositions.append(pygame.Vector2((index1+0.5)*self.width/self.mapsize,(index2+0.5)*self.height/self.mapsize))
                    if self.checkWin(index1,index2):
                        self.done = True
                        obs = torch.tensor(self.map,dtype=torch.float32)
                        obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))
                        return obs,reward,self.done,self.movecount
                else:
                    reward += 1
                    self.movecount += 1
                    self.map[index1][index2] = self.currentplayer
                    self.currentplayer = self.currentplayer * -1
                    self.validmoves = self.updateValidMoves(index1,index2,self.map,self.validmoves)
                    if self.rendering:
                        self.circdrawpositions.append(pygame.Vector2((index1+0.5)*self.width/self.mapsize,(index2+0.5)*self.height/self.mapsize))
                    if self.checkWin(index1,index2):
                        self.done = True
                        reward = 50 + 500/self.movecount
                        obs = torch.tensor(self.map,dtype=torch.float32)
                        obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))
                        return obs,reward,self.done,self.movecount
            self.movecount += 1
            
            random.shuffle(self.validmoves)
            if random.random() > 0.9:
                (index1,index2),movescores = self.breadthSearch()
            else:
                index1,index2 = self.validmoves[0]
            self.map[index1][index2] = self.currentplayer
            if self.rendering:
                self.xdrawpositions.append(pygame.Vector2((index1+0.5)*self.width/self.mapsize,(index2+0.5)*self.height/self.mapsize))
                for pos in self.circdrawpositions:
                    pygame.draw.circle(self.screen,self.maincolor,pos,self.width/(self.mapsize*2) - 2,5)
                for pos in self.xdrawpositions:
                    pygame.draw.lines(self.screen,self.maincolor,False,self.drawX(pos),5)
                pygame.display.flip()
                sleep(0.2)
            if self.checkWin(index1,index2):
                self.done = True
                reward = -10
                obs = torch.tensor(self.map,dtype=torch.float32)
                obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))
                return obs,reward,self.done,self.movecount
            self.validmoves = self.updateValidMoves(index1,index2,self.map,self.validmoves)
            # append the move position to the draw lists
            self.currentplayer = -1 * self.currentplayer
            self.firstMove = False
        else:
            self.done = True
        obs = torch.tensor(self.map,dtype=torch.float32)
        obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))

        return obs,reward,self.done,self.movecount
    #@njit
    def breadthSearch(self):
        return _breadthSearch(self.validmoves,self.currentplayer,self.debug,self.map,self.mapsize,self.automatedPlayer)
    #@njit
    def evaluatePos(self,idx1,idx2,map) -> int:
        return _evaluatePos(idx1,idx2,map,self.debug,self.mapsize,self.automatedPlayer)
    #@njit
    def updateValidMoves(self,idx1 : int,idx2 : int,mapcopy : np.array,validMoves : list[tuple]) -> list[tuple]:
        return _updateValidMoves(idx1,idx2,mapcopy,validMoves,self.mapsize)
    #@njit
    def checkWin(self,idx1,idx2):
        return _checkWin(idx1,idx2,self.map,self.mapsize)
    #@njit
    def checkValid(self,idx1,idx2):
        return _checkValid(idx1,idx2,self.mapsize,self.map)
    def reset(self) -> torch.tensor:
        if self.rendering:
            self.rendering = False
            pygame.quit()
        self.map = np.zeros((self.mapsize,self.mapsize))
        self.firstMove = True
        self.validmoves = []
        self.movecount = 0
        if self.currentplayer == -1:
            obs = torch.tensor(self.map,dtype=torch.float32)
            obs = torch.reshape(obs,(1,self.mapsize,self.mapsize))
            return obs
        else:
            obs, _, _, _ = self.step(np.array([self.mapsize,self.mapsize])) # pass an invalid action, since it should ignore the action anyways
            return obs
    def render(self):
        if not self.rendering:
            self.rendering = True
            pygame.init()
            self.screensize = 1080
            self.screen = pygame.display.set_mode((self.screensize, self.screensize))
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
            self.circdrawpositions = []
            self.xdrawpositions = []
        return
    def drawX(self,pos):
        return [pos-pygame.Vector2(self.width/(self.mapsize*2),self.height/(self.mapsize*2)),pos+pygame.Vector2(self.width/(self.mapsize*2),self.height/(self.mapsize*2)),pos,pos+pygame.Vector2(-self.width/(self.mapsize*2),self.height/(self.mapsize*2)),pos+pygame.Vector2(self.width/(self.mapsize*2),-self.height/(self.mapsize*2))]
