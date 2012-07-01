'''
Created on Jun 22, 2012
quick description and documentation in attached readme file. 
@author: colinwinslow
'''
import util
import numpy as np
from math import sqrt
import heapq

global distance_limit 
# sets the allowed range for variance in spacing from one pair of objects in the line to the next.
# if abs(ln(x)) rises above this limit, the object is not considered as a valid successor state
# by the pathfinding algorithm.
distance_limit = 1


global angle_limit 
#the max angle, in radians, that an object is allowed to deviate from the existing line.
angle_limit = .7


global min_line_length
#minimum number of objects considered to be a line
min_line_length=3

global angular_weight,distance_weight
#adjusts the weight of angle and distance variation in the cost function.
angular_weight = 1
distance_weight = 1

def main():
    np.seterr(all='raise')
    
    print "scene 14, step 8"
    findChains(util.get_objects(14, 8)) #final scene
    print""
    print "scene 4, step 5"
    findChains(util.get_objects(4, 5)) #14th folder
    

def findChains(inputObjectSet):
    '''finds all the chains, then returns the ones that satisfy constraints, sorted from best to worst.'''
    startingPairs = util.find_pairs(inputObjectSet)
    
    bestlines = []
    for pair in startingPairs:
        bestlines.append(chainSearch(pair[0], pair[1], inputObjectSet))
    print "best lines:"
    verybest = []
    for line in bestlines:
        if len(line)>=min_line_length+1:
            verybest.append(line)
    verybest.sort(key=lambda list: list[len(line)-1])#something isn't right here...
    for line in verybest:
         print  "cost: ", line[len(line)-1],util.lookup_objects(line)
    return verybest

        
            
def chainSearch(start, finish, points):
    node = Node(start, -1, [], 0)
    frontier = PriorityQueue()
    fringeDirectory = {util.totuple(start):node}
    frontier.push(node, 0)
    explored = set()
    loopcount = 0
    while frontier.isEmpty() == False:
#        loopcount+=1
#        print "popping frontier #",loopcount
        node = frontier.pop()
        frontier.isEmpty()
        try:fringeDirectory.pop(util.totuple(node.getState()))
        except: pass
        if node.getState().id == finish.id:
            path = node.traceback()
            path.insert(0, start.id)
            return path
        explored.add(util.totuple(node.getState()))
        for action in node.getSuccessors(points):
            child = action
            if util.totuple(child.state) not in explored and util.totuple(child.getState()) not in fringeDirectory:
#                    print"pushing to frontier", child.state.id
                    frontier.push(child, child.cost)
                    fringeDirectory[util.totuple(child.getState())] = child
            elif util.totuple(child.getState()) in fringeDirectory:
                
                if fringeDirectory[util.totuple(child.getState())].cost > child.cost:
#                    print fringeDirectory[util.totuple(child.getState())].cost, child.cost
                    frontier.push(child,child.cost)
                    fringeDirectory[util.totuple(child.getState())] = child
                
            
        


    


            
        
        
#def search(points, start, goal):
    
def angleCost(a, b, c):
    '''angle cost of going to c given we came from ab'''
    abDir = b - a
    bcDir = c - b
    difference = util.findAngle(abDir, bcDir)
    if np.isnan(difference): return 0
    else: return np.abs(difference)
def distanceCost(a, b, c):
    #np.seterr(all='warn')
    '''treats longer or shorter distances with equal disdain'''
    abDist = util.findDistance(a, b)
    bcDist = util.findDistance(b, c)
    if bcDist==0:
        return 200
    almostdone= np.abs(np.log((1/abDist)*bcDist))

    return almostdone
    


    
class Node:
    def __init__(self, state, parent, action, cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
#        if parent != -1:
#            self.cost = parent.cost + cost
    def getState(self):
        return self.state
    def getSuccessors(self, points):
        
        
        if self.parent == -1:
            out = []
            try: points.remove(self)
            except: pass
            for p in points:
                dist = util.findDistance(self.state.position, p.position)
                out.append(Node(p,self,p.id,dist))
            return out
        else:
#            print "parent is not -1"
            out = []
            try: points.remove(self)
            except: pass
            for p in points:
                if self.state.id != p.id: 
                    dCost = distanceCost(self.parent.state.position, self.state.position, p.position)
                    aCost = angleCost(self.parent.state.position, self.state.position, p.position)
                    
                    if aCost <= angle_limit and dCost <= distance_limit:
                        out.append(Node(p,self,p.id,angular_weight*aCost+distance_weight*dCost))
            return out

    def traceback(self):
        cost = 0
        solution = []
        node = self
        while node.parent != -1:
            solution.insert(0, node.action)
            cost += node.cost
            node = node.parent
        cardinality = len(solution)
        cost = cost/cardinality
        solution.append(cost)
        return solution


class PriorityQueue:
    '''stolen from ista 450 hw ;)'''

    def  __init__(self):  
        self.heap = []
    
    def push(self, item, priority):
        pair = (priority, item)
        heapq.heappush(self.heap, pair)
#        print "PQ now has ", len(self.heap), "members"


    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return item
  

    def isEmpty(self):
        return len(self.heap) == 0




if __name__ == '__main__': main()
