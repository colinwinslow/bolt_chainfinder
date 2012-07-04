'''
Created on Jun 22, 2012
quick description and documentation in attached readme file. 
@author: colinwinslow
'''
import util
import numpy as np
import heapq
from collections import namedtuple
global distance_limit 
# sets the allowed range for variance in spacing from one pair of objects in the line to the next.
# a value of 1 allows objects to range from half as distant to twice as distant, and a value of 2
# allows them to range from 1/4 as distant to 4 times as distant, etc.
distance_limit = 105


global angle_limit 
#the max angle, in radians, that an object is allowed to deviate from the existing line.
angle_limit = .7

global min_line_length
#minimum number of objects considered to be a line
min_line_length=3

global anglevar_weight,distvar_weight,dist_weight
#adjusts the weight of angle and distance variation in the cost function.
anglevar_weight = 0
distvar_weight = 0
dist_weight=1

def main():
    
    print "Sample run of line detecton on Blockworld: \n"
    np.seterr(all='raise')
    
    print "scene 14, step 8"
    findChains(util.get_objects(14, 8))
    print""
    print "scene 4, step 5"
    findChains(util.get_objects(4, 5))
    
    PhysicalObject = namedtuple('physicalObject', ['id', 'position', 'bbmin', 'bbmax'])
#    
#    a = PhysicalObject(1,np.array([1,0]),1,1)
#    b = PhysicalObject(2,np.array([2,0]),1,1)
#    c = PhysicalObject(3,np.array([3,0]),1,1)
#    d = PhysicalObject(4,np.array([4,0]),1,1)
#    e = PhysicalObject(5,np.array([5,0]),1,1)
#    
#    f = PhysicalObject(6,np.array([1,1]),1,1)
#    g = PhysicalObject(7,np.array([2,2]),1,1)
#    h = PhysicalObject(8,np.array([3,3]),1,1)
#    i = PhysicalObject(9,np.array([4,4]),1,1)
#    j = PhysicalObject(10,np.array([5,5]),1,1)
#    k = PhysicalObject(11,np.array([6,6]),1,1)
#
#    
#    print"test problem"
#    findChains([a,b,c,d,e,f,g,h,i,j,k])
    
    
    
    
    

def findChains(inputObjectSet):
    '''finds all the chains, then returns the ones that satisfy constraints, sorted from best to worst.'''
    startingPairs = util.find_pairs(inputObjectSet)
    
    bestlines = []
    for pair in startingPairs:
        result = chainSearch(pair[0], pair[1], inputObjectSet, trace)
        if result != None: bestlines.append(result)
    print "bestlines: ",bestlines
    print "best lines:"
    verybest = []
    for line in bestlines:
        if len(line)>min_line_length:
            verybest.append(line)
    verybest.sort(key=lambda l: l[len(l)-1])
    
    for line in verybest:
        print  "cost: ", line[len(line)-1],"\t",util.lookup_objects(line)
    return verybest

        
            
def chainSearch(start, finish, points, trace=False):
    node = Node(start, -1, [], 0)
    frontier = PriorityQueue()
    frontier.push(node, 0)
    explored = set()
    while frontier.isEmpty() == False:
        node = frontier.pop()
        if node.getState().id == finish.id:
            path = node.traceback()
            path.insert(0, start.id)
            return path
        explored.add(node.state.id)
        successors = node.getSuccessors(points,start,finish)
        for child in successors:
            if child.state.id not in explored and frontier.contains(child.state.id)==False:
                frontier.push(child, child.cost)
            elif frontier.contains(child.state.id) and frontier.pathCost(child.state.id) > child.cost:
                frontier.push(child,child.cost)

                
            
        


    


            
        
        
#cost functions
def oldAngleCost(a, b, c):
    '''angle cost of going to c given we came from ab'''
    abDir = b - a
    bcDir = c - b
    difference = util.findAngle(abDir, bcDir)
    if np.isnan(difference): return 0
    else: return np.abs(difference)
def angleCost(a, b, c, d):
    '''prefers straighter lines'''
    abDir = b - a
    cdDir = d - c
    difference = util.findAngle(abDir, cdDir)
    if np.isnan(difference): return 0
    else: return np.abs(difference)
def distVarCost(a, b, c):
    #np.seterr(all='warn')
    '''prefers lines with less variance in their spacing'''
    abDist = util.findDistance(a, b)
    bcDist = util.findDistance(b, c)
    if bcDist==0:
        return 200
    almostdone= np.abs(np.log2((1/abDist)*bcDist))
    return almostdone
def distCost(current,step,start,goal):
    '''prefers dense lines to sparse ones'''
    stepdist = util.findDistance(current, step)
    totaldist= util.findDistance(start, goal)
    return stepdist**2/totaldist**2
    
    


    
class Node:
    def __init__(self, state, parent, action, cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.icost = cost
        if parent != -1:
            self.cost = parent.cost + cost
        else: self.cost=cost
    def getState(self):
        return self.state
    
    def getSuccessors(self, points,start,finish):
        
        
        if self.parent == -1:
            out = []
            for p in points:
                if self.state.id != p.id and finish.id!=p.id: 
                    
                    aCost = angleCost(self.state.position,finish.position, self.state.position, p.position)
                    if aCost <= angle_limit:
                        dCost =distCost(self.state.position,p.position,start.position,finish.position)
                        if dCost < 1: # prevents it from choosing points that overshoot the target.
                            normA = anglevar_weight*(aCost/angle_limit)
                            normD = dist_weight*dCost
                            finalcost = (normA+normD)/(anglevar_weight+dist_weight)
                            out.append(Node(p,self,p.id, finalcost))
            return out
        else:
#            print "parent is not -1"
            out = []
            
            for p in points:
                if self.state.id != p.id: 
                    vCost = distVarCost(self.parent.state.position, self.state.position, p.position)
                    #aCost = angleCost(self.parent.state.position, self.state.position,self.state.position, p.position)
                    aCost = oldAngleCost(self.parent.state.position,self.state.position,p.position)
                    dCost = distCost(self.state.position,p.position,start.position,finish.position)
                    if aCost <= angle_limit and dCost <= 1:
                        normV = distvar_weight*(vCost/distance_limit)
                        normA = anglevar_weight*(aCost/angle_limit)
                        finalCost = (normA+normV+dCost)/(distvar_weight+anglevar_weight+dist_weight)
                        out.append(Node(p,self,p.id,finalCost))
                        
            return out

    def traceback(self):
#         cost = 0
        solution = []
        node = self
        while node.parent != -1:
            solution.insert(0, node.action)
            node = node.parent
        cardinality = len(solution)-1 #exclude the first node, which has cost 0
        cost = self.cost/cardinality
        solution.append(cost)
        return solution


class PriorityQueue:
    '''stolen from ista 450 hw ;)'''

    def  __init__(self):  
        self.heap = []
        self.dict = dict()
    
    def push(self, item, priority):
        pair = (priority, item)
        heapq.heappush(self.heap, pair)
        self.dict[item.state.id]=priority
    
    def contains(self,item):
        return self.dict.has_key(item)
    
    def pathCost(self,item):
        return self.dict.get(item)


    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return item
        
  

    def isEmpty(self):
        return len(self.heap) == 0




if __name__ == '__main__': main()
