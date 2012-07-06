'''
Created on Jun 22, 2012
quick description and documentation in attached readme file. 
@author: colinwinslow
'''
import util
import numpy as np
import heapq


global ignore_z
#ignores z axis data
ignore_z = False

global distance_limit 
# sets the allowed range for variance in spacing from one pair of objects in the line to the next.
# a value of 1 allows objects to range from half as distant to twice as distant, and a value of 2
# allows them to range from 1/4 as distant to 4 times as distant, etc.
distance_limit = 3


global angle_limit 
#the max angle, in radians, that an object is allowed to deviate from the existing line.
angle_limit = .9

global min_line_length
#minimum number of objects considered to be a line
min_line_length=3

global anglevar_weight,distvar_weight,dist_weight
#adjusts the weight of angle and distance variation in the cost function.

anglevar_weight = .05     # these two need to be small compared to dist_weight
distvar_weight = .1      
                       
dist_weight=1




def main():
    
    
    print "Sample run of line detecton on Blockworld: \n"
    np.seterr(all='raise')
    
    print "scene 14, step 8"
    


    for line in findChains(util.get_objects(14, 8)):
        print  "prior: ", np.round(line[0],4),"\t",util.lookup_objects(line[1])




def findChains(inputObjectSet):
    '''finds all the chains, then returns the ones that satisfy constraints, sorted from best to worst.'''

    
    bestlines = []
    explored = set()
    skipped = 0
    pairwise = util.find_pairs(inputObjectSet)
    list.sort
    pairwise.sort(key=lambda p: util.findDistance(p[0].position, p[1].position),reverse=True)
    for pair in pairwise:
        start,finish = pair[0],pair[1]
        if frozenset([start.id,finish.id]) not in explored:
            result = chainSearch(start, finish, inputObjectSet)
            if result != None: 
                bestlines.append(result)
                s = map(frozenset,util.find_pairs(result[0:len(result)-1]))
                map(explored.add,s)
        else: skipped += 1
               
    verybest = []
    costSum = 0
    for line in bestlines:
        if len(line)>min_line_length:
            verybest.append(line)
            line[len(line)-1] = 1-line[len(line)-1]
            costSum += line[len(line)-1]
    verybest.sort(key=lambda l: l[len(l)-1],reverse=True)
    costs = map(lambda l: l.pop()/costSum,verybest)
    return zip(costs,verybest)
            
def chainSearch(start, finish, points):
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
        #shouldn't ever occur, but prevents undefined data while debugging
        return 0
    return np.abs(np.log2((1/abDist)*bcDist))

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
        
        out = []
        if self.parent == -1: 
            for p in points:
                if self.state.id != p.id and finish.id!=p.id: 
                    aCost = angleCost(self.state.position,finish.position, self.state.position, p.position)
                    dCost =distCost(self.state.position,p.position,start.position,finish.position)
                    if aCost <= angle_limit and dCost < 1: # prevents it from choosing points that overshoot the target.
                        normA = anglevar_weight*(aCost/angle_limit)
                        normD = dist_weight*dCost
                        finalcost = (normA+normD)/(anglevar_weight+dist_weight)
                        out.append(Node(p,self,p.id, finalcost))
        else:
            out = []
            for p in points:
                if self.state.id != p.id: 
                    vCost = distVarCost(self.parent.state.position, self.state.position, p.position)       
                    aCost = angleCost(self.parent.state.position, self.state.position,self.state.position, p.position)
#                    aCost = oldAngleCost(self.parent.state.position,self.state.position,p.position)
                    dCost = distCost(self.state.position,p.position,start.position,finish.position)
                    if aCost <= angle_limit and dCost <= 1:
                        normV = distvar_weight*(vCost/distance_limit)
                        normA = anglevar_weight*(aCost/angle_limit)
                        finalCost = (normA+normV+dCost)/(distvar_weight+anglevar_weight+dist_weight)
                        out.append(Node(p,self,p.id,finalCost))
                        
        return out

    def traceback(self):
        solution = []
        node = self
        while node.parent != -1:
            solution.append(node.action)
            node = node.parent
        cardinality = len(solution)-1 #exclude the first node, which has cost 0
        cost = self.cost/cardinality
        solution.reverse()
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
