from collections import namedtuple
from bwdb import *
import numpy as np

import math


def get_objects(sequence_index, frameIndex):
    '''returns list of objects in given sequence at any particular frame'''
    s = Sequence.query.filter_by(seq_idx=sequence_index)
    f = s.filter_by(scene_idx=frameIndex).first().scene_id
    return map(extract_data, Object.query.filter_by(scene_id=f).all())

def get_objects_by_scene(sceneIndex):
    '''returns list of objects in given scene id'''
    return map(extract_data, Object.query.filter_by(scene_id=sceneIndex).all())

def totuple(a):
    '''converts whatever nested iterables into (immutable) tuples'''
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a
    
def extract_data(o, n=3):
    '''extract position and size information for a given object in the db'''
    PhysicalObject = namedtuple('physicalObject', ['id', 'position', 'bbmin', 'bbmax'])
    return PhysicalObject(o.id,
             np.array([o.position_x, o.position_y, o.position_z]),
             np.array([o.bb_min_x, o.bb_min_y, o.bb_min_z]),
             np.array([o.bb_max_x, o.bb_max_y, o.bb_max_z])
                )
def lookup_objects(list):
    '''this is sloppy, but i'm new to SQL ;)'''
    descriptive_list = []
    for obj in list:
        allObjects = Object.query.all()
        for d in allObjects:
            if d.id==obj:
                descriptive_list.append(str(d.color_name)+str(d.shape)+str(d.id))
    return descriptive_list
    
    
def findDistance(vector1,vector2):
    '''euclidian distance between 2 points'''
    return np.round(math.sqrt(np.sum(np.square(vector2-vector1))),3) 

def findAngle(vector1, vector2):
    '''difference between two vectors, in radians'''
    preArc=np.dot(vector1, vector2) / np.linalg.norm(vector1) / np.linalg.norm(vector2)
    return np.arccos(np.round(preArc, 5))

def find_pairs(l):
    '''returns a list of all possible pairings of list elements'''
    pairs = []
    for i in range(len(l)):
        for j in range(len(l))[i + 1:]:
            pairs.append((l[i], l[j]))
    return pairs

