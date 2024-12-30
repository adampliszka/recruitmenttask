import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import networkx as nx
from scipy.optimize import curve_fit
#%%
mpl.use('TkAgg')
#%%
'''it should be possible to exploit the symmetry and reduce the size of dicts by 2, but it would be risky with the asymmetric optimisation I did, and would take too long to exploit just for 2x gains in computation'''
#it turned out to be a bit of a headache, should have done it from the start - it was obvious, but didn't expect that it would be so bad
#good lesson for the future, and good thing I didn't try changing it in the middle
#I should have made every iteration do two passes, then I could fold the turnaround into the iteration I think?
global currentX 
global currentY 
global moves
global points
global duplicates
global scheduledExpansion
#%%
def sendSignalInternal(direction):
    sendSignal(direction)   #for the task requirements
    global currentY
    global currentX
    global moves
    global points
    global duplicates
    moves += 1
    match direction:
        case "UP":
            currentY+=1
            #print("up")
        case "DOWN":
            currentY-=1
            #print("down")
        case "RIGHT":
            currentX+=1
            #print("right")
        case "LEFT":
            currentX-=1
            #print("left")
    if (currentX, currentY) in points:
        #print(f"DUPLICATE: {currentX},{currentY}")
        duplicates+=1
    else:
        points.add((currentX,currentY))
#%%
def drawHyperbola(coefficient, coeff2, margin, iterations, silent=False):
    global currentX
    global currentY
    global moves
    global points
    global duplicates
    global scheduledExpansion
    maxK=iterations
    if not silent:
        plt.figure(figsize=(20, 20))
    startedUpNotRight = True 
    explored = dict([(1, 1)])
    toExplore = dict([(1, 1)])
    currentX = 1
    currentY = 1
    moves = 0
    duplicates = 0
    points = set()
    budget = 0
    theoreticalTotal = 0
    scheduledExpansion = 0
    
    costsNormal = [0]
    costsExpanded = [0]
    expandedLastOne = False
    
    expandByLast = 0
    if not silent:
        plt.ion()
        
    for k in range(2,maxK): #K^2=S
        if k == 100:
            coefficient += 15
        if k == 200:
            coefficient += 15
        if k == 300:
            coefficient += 25
        if k == 320:
            coefficient += 80
        if not silent:
            print(f"iteration: {k}")
        if expandedLastOne:
            expandedLastOne = False
            costsExpanded.append(moves)
            costsNormal.append(costsNormal[-1] + (costsNormal[-1] - costsNormal[-2]))
        else:
            costsNormal.append(moves)
        #------------FIND THE AREA TO EXPLORE------------
        for A in range(k**2):
            toExplore[A+1]=k**2//(A+1)  #total area to be explored at the end of iteration
        #-------EXPAND AREA TO REDUCE BACKTRACKING-------
        #depending on the stage we're in, we will commit the extra resources we have towards filling in advance
        #the further from origin, the less often we want to visit
        budget = np.floor(35*(k**2) - moves) if k>2 else 0   #calculate the budget
        
        costWithoutExpansion = costsNormal[-1] + (costsNormal[-1] - costsNormal[-2]) if k>3 else 0
        costWithoutExpansion *= 1.1
        if not silent:
            print(costWithoutExpansion)
        budgetEstimate = abs(budget - costWithoutExpansion) if k > 3 else 0 #I think I can skip costWithoutExpansion but todo tomorrow
        commitedBudget = (budgetEstimate - 2 * k**2) / coefficient if k > 5 else 0
        if (k+1)**2 > explored.get(1, 0) and k > 5:
            print("expanding")
            
            sumAboveMidpoint = 0
            for y in range(1, k):
                sumAboveMidpoint += ((k ** 2 // y) - k)**2  #the area above the midpoint
            for xCoord in range(1, k):
                toExplore[xCoord] = max(toExplore.get(xCoord,0), int(explored.get(xCoord, 0) + (commitedBudget * ((toExplore.get(xCoord, 0) - k) ** 2)) / sumAboveMidpoint))
                #budget allocated more or less based on distance from origin
            for xCoord in range(1, k):  #mirror across the diagonal
                maxValue = toExplore.get(xCoord, 0)
                minValue = toExplore.get(xCoord + 1, 0)
                for xCoordToMirror in range(maxValue, minValue, -1):
                    toExplore[xCoordToMirror] = xCoord
        # else:
        #     expandByLast = expandBy
        #------------DELETE UNNEEDED COLUMNS------------
        #we'll start with the first column that needs to be filled and finish with the last one, the rest are deleted
        firstToFill = 1
        lastToFill = max(toExplore)
        while toExplore.get(firstToFill, 1) <= explored.get(firstToFill, 0) and firstToFill < max(toExplore):
            firstToFill+=1
        while toExplore.get(lastToFill, 1) <= explored.get(lastToFill,0) and lastToFill > 1:
            lastToFill-=1
        if firstToFill >= lastToFill:
            continue
            
        for xCoord in range(1, firstToFill):
            del toExplore[xCoord]
        for xCoord in range(max(toExplore), lastToFill, -1):
            del toExplore[xCoord]
        #-------CONNECT GAPS TO REDUCE BACKTRACKING------
        #need to backtrack anyway, so might as well fill in empty spaces so the region is contiguous for no cost
        if startedUpNotRight:
            if toExplore.get(firstToFill+1,0) < toExplore.get(firstToFill,0) and explored.get(firstToFill+1,0) < toExplore.get(firstToFill,0):  #probably redundant
                toExplore[firstToFill+1]=toExplore.get(firstToFill,0)
        else:
            level = toExplore.get(lastToFill,0) + 1 #the level to fill up to
            xToFillUp = lastToFill
            while toExplore.get(xToFillUp,0) < level and xToFillUp > firstToFill and explored.get(xToFillUp,0) < level: 
                toExplore[xToFillUp]=level
                xToFillUp-=1
        #the area will be contiguous which will help with the search, and in this problem, it shouldn't cost moves
        #this has the problem that while we need to do it anyway, so it's theoretically free, it's going to be long until those will be useful
        #it can't be helped, but filling the long backtrack-y regions ahead of time is expected to be useful, so I will implement this later
        #EDIT: implemented
        for xToFill in range(firstToFill + 1, lastToFill+1):
            if toExplore.get(xToFill,0) <= explored.get(xToFill-1,0):
                toExplore[xToFill]=explored.get(xToFill-1,0)+1
        #------FIND THE NEW POINTS FOR VISUALISATION-----
        leftToExplore=set()             #the cells not yet explored
        for wantedX, wantedY in toExplore.items():
            for howManyAbove in range(np.abs(wantedY - explored.get(wantedX, 0))):
                leftToExplore.add((wantedX, explored.get(wantedX,0) + howManyAbove + 1))
        if len(leftToExplore) == 0: #the only important part of this code block when not visualising
            continue
        if not silent:
            plt.scatter(*zip(*leftToExplore))
        theoreticalTotal += len(leftToExplore)
        #---------------EXPLORE THE SPACES---------------
        xStart = 1
        yStart = 1
        xEnd = 1
        yEnd = 1
        if startedUpNotRight:   #the first column/row is always paired with next of same height, so we move to the top/right, fill the first row/column, mark explored, and do to the rest
            xStart = min(toExplore) #leftmost highest unexplored point
            yStart = toExplore.get(xStart, 0)
            xEnd = max(toExplore)   #rightmost lowest unexplored point
            yEnd = explored.get(xEnd, 0) + 1
        else:
            xStart = max(toExplore) #rightmost lowest unexplored point
            yStart = explored.get(xStart, 0) + 1
            xEnd = min(toExplore)   #leftmost highest unexplored point
            yEnd = toExplore.get(xEnd, 0)

        while currentX > xStart:    #TODO: optimise this so it doesn't go over previously explored areas
            sendSignalInternal("LEFT")
            if explored.get(currentX,0) < currentY:
                explored[currentX] = currentY
        while currentY > yStart:
            sendSignalInternal("DOWN")
            if explored.get(currentX,0) < currentY:
                explored[currentX] = currentY
        while currentY < yStart:
            sendSignalInternal("UP")
            if explored.get(currentX,0) < currentY:
                explored[currentX] = currentY
        while currentX < xStart:
            sendSignalInternal("RIGHT")
            if explored.get(currentX,0) < currentY:
                explored[currentX] = currentY

        if startedUpNotRight:
            sendSignalInternal("RIGHT")
        else:
            sendSignalInternal("UP")
            
        if not silent:
            plt.scatter(currentX, currentY, color='white')
        while currentX != xEnd or currentY != yEnd :
            if startedUpNotRight:
                if currentY > explored.get(currentX, 0) + 1:  #can move down
                    sendSignalInternal("DOWN")
                else:
                    if currentY > toExplore.get(currentX + 1, 0):  #can't move right - shouldn't happen with a contiguous monotonic area
                        break
                    explored[currentX] = toExplore.get(currentX, 0)
                    sendSignalInternal("RIGHT")
                    haveToComeBack = True   #for rectangles, enforces a snaking pattern
                    if currentY <= explored.get(currentX, 0) + 1:  #can't move down
                        haveToComeBack = False
                    while currentY < toExplore.get(currentX, 0):
                        sendSignalInternal("UP")
                    if not haveToComeBack:
                        explored[currentX] = toExplore.get(currentX, 0)
                        sendSignalInternal("RIGHT")
            else:
                if currentY < toExplore.get(currentX, 0):  #can move up
                    sendSignalInternal("UP")
                else:
                    if currentY <= explored.get(currentX - 1, 0):  #can't move left
                        break
                    explored[currentX] = toExplore.get(currentX, 0)
                    sendSignalInternal("LEFT")
                    haveToComeBack = True   #for rectangles, enforces a snaking pattern
                    if currentY >= toExplore.get(currentX, 0):  #can't move up
                        haveToComeBack = False
                    while currentY > explored.get(currentX, 0)+1:
                        sendSignalInternal("DOWN")
                    if not haveToComeBack:
                        explored[currentX] = toExplore.get(currentX, 0)
                        sendSignalInternal("LEFT")
        #----------------UPDATE THE STATE----------------
        startedUpNotRight = not startedUpNotRight
        explored.update(toExplore)  #update the currently explored area
        #----------------PRINT STATISTICS----------------
        if not silent:
            plt.scatter(currentX, currentY, color='black')
            print(f"moves: {moves}; limit: {35*((k)**2)}, {"passed" if moves < (35*((k)**2)) else "failed"}")
            print(f"points plotted: {theoreticalTotal}, theoretical duplicates: {moves-theoreticalTotal}, {"passed" if theoreticalTotal < (35*((k)**2)) else "failed"}")
            print(f"counted duplicates: {duplicates}, theoretical best: {moves - duplicates}, {"passed" if moves - duplicates < (35*((k)**2)) else "failed"}\n")
        if moves > (35 * ((k) ** 2)):
            print(f"k={k}, moves: {moves}; limit: {35*((k)**2)},failed")
            return False
    if not silent:
        plt.show()
        
        plt.figure(figsize=(20, 20))
        plt.scatter(*zip(*points))
        plt.scatter(currentX, currentY, color='black')   
        plt.show()
    else:
        pass
        # print(f"k={k}, moves: {moves}; limit: {35*((k)**2)},failed")
    return True

drawHyperbola(2.3, 1.1, 1, 1000, silent=False)
