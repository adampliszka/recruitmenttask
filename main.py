The algorithm is far from perfect, and currently it manages to explore the space for up to S=121,104, while the greedy approach would net a result of 2,401. I've started my application two days ago, and this is what I wrote during two days, hopefully if I had more time I could have finished the task fully.
In case it's easier for someone, 

SOLUTION:
Variables: A (the x-coordinate size), B (the y-coordinate size), an initial position (x_0, y_0) and position of the apple (x_a, y_a)
The game is played on a torus
Constraints: A,B>=1, AB<1000000, moves <= 35AB
We're minimizing the number of moves sent to the engine, not the steps in the algorithm.

I define origin of the coordinate system as the starting position (which doesn't sacrifice specificity on a torus) so that the starting position is (1,1), i.e. x_t=x-x_0 where x is the current x coordinate, and x_t is the translated x coordinate, same with the y dimension. The coordinates in the game engine form a system of modular arithmetic, such that x=x%A and y=y%B, but I will use coordinates that don't follow this rule. Instead, I will be viewing the torus as an infinite tiling of rectangles, where visiting a space in one rectangle marks this space visited in all rectangles. From now on, unless stated otherwise, I am using this system.

The only feedback we are getting is the fact that after X moves, if the game hasn't ended we know that X <= 35AB, which as the only piece of information is worth paying attention to.

There are two cases which aren't explicitly contradicted: one is that the Snake game is like the popular one where the snake moves on its own every tick and the input changes direction, but this has a trivial solution, e.g. hitting left at first, waiting for a million ticks, clicking down, then immediately left, and repeating this procedure until victory.
It's obvious from contextual cues that this is not the one I'm supposed to solve, and I need to manually move the snake each time like a game piece on a board.

As every command moves the snake to another space within identical distance, every command is a new visited coordinate, and thus any procedure which doesn't revisit the same space twice is equivalent, as are any procedures which at every point in time have revisited previous spaces n amount of times. For known A and B, an example would be a procedure which first explores the space 1x1, then explores the edge of the space to expand the region to 2x2, and so on, until it reaches min(A,B) x min(A,B), and then explores the remaining rectangle recursively just like it explored the first part - exploring squares until there is no more to explore. Because of the wraparound, we always have an empty field next to us after finishing the square, so we can guarantee no duplicates.

As for every size S+1 the problem is a subset of the problem for size S, the best approach will be to at first assume S=1 and then progressively enlarge S, now exploring the search area not covered previously.

For every size of the field, we need to explore all the possible values of A and B. E.g. for a field of the size 100, we need to explore the possibilities 10x10, 1x100, 100x1 and everything in between, i.e. all the values of A and B such that A,B<=100 and AB<=100. Those rectangles will obviously be constrained by a hyperbola - for a size S, the hyperbola will be y(x)=S/x. 
For the worst-case size, i.e. 1000000, the absolute maximum size of search will be the integral from 1/1000000 to 1000000 of the function y(x)=1000000/x, which when integrated numerically with step of 1 works out to 13970034, or around 14S. This means that assuming the worst-case scenario where we backtrack every pixel, it would be 26S, so this suggests it likely is possible to explore the area with backtracking (and therefore certainty of our position) while meeting the <=35S constraint, especially when you consider that while to draw a 10x10 square you need 100 steps, to backtrack you need only 20, so this is still a worst case scenario that applies only to 1xB and Ax1 rectangles, and the true upper bound is somewhere between 2x14S and S+2sqrt(S).

Because we view the torus as a tiling, the task boils down to "drawing" a space constrained hyperbola with the visited squares, and then expanding the hyperbola progressively. I will choose steps where every step the central square will grow by 1 (e.g. from 100x100 to 101x101), so S will grow a quadratic rate. Depending on the margins we achieve, this could theoretically pose a problem where we don't explore the intermediate values fast enough, so if testing does show that problem, it will need to be solved.
Because I do not expect to intentionally leave empty spaces surrounded by searched spaces, I will store the current state of the search-space via a dictionary (implemented as a hash table - for faster lookups) storing the heights of the area searched for each x coordinate. E.g. {1:3, 2:2, 3:1} means:
[]
[] []
[] [] []
This representation could be improved, e.g. by providing the description only up to the half-way point, but as my optimisations aren't symmetric, I will leave it as it is, as I don't judge it worth the effort for now.

I've decided to write the code in Python, as Jupyter allows for rapid iteration, and I didn't need any real complex dependency structures or object-orientedness in this case.
During the implementation, the problem presented itself that it's very impractical to expand the furthest reaches of the graph every time, so a greedy approach won't work. I implemented a solution that periodically expands the edges so I need to return less often.
The algorithm uses the greedy approach until the next iteration would need to touch the first column of the graph - then, budget is allocated, and this iteration is used for expanding the furthest regions. I've been adjusting the parameters, and the current version of the algorithm has the main problem of estimating the number of steps those expansions will take. If I had more time, I would try developing a better heuristic for that, thinking about how one would actually calculate the upper bound rigorously for my algorithm, or simply just run the iteration "virtually", and if we go over budget, then try adjusting the parameters until it passes. However, I've ran out of time, so this is as far as I got.


ALGORITHM (to work with the game engine, just add the sendSignal to the sendSignalInternal method):
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
