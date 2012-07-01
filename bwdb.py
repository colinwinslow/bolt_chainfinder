#!/usr/bin/env python

#### bwdb.py
#### The BlockWorld Database



from elixir import *



metadata.bind = 'sqlite:///blockworld.db'
metadata.bind.echo = False  



class Camera(Entity):
    using_options(tablename='cameras')
    near = Field(Float)
    far = Field(Float)
    fov = Field(Float)
    aspect = Field(Float)
    position_x = Field(Float)
    position_y = Field(Float)
    position_z = Field(Float)
    rotation_x = Field(Float)
    rotation_y = Field(Float)
    rotation_z = Field(Float)
    lookat_x = Field(Float)
    lookat_y = Field(Float)
    lookat_z = Field(Float)

class Scene(Entity):
    using_options(tablename='scenes')
    idx = Field(Integer)
    camera = ManyToOne('Camera')
    user_inputs = OneToMany('UserInput')
    objects = OneToMany('Object')

class Sequence(Entity):
    using_options(tablename='sequences')
    seq_idx = Field(Integer)
    scene_idx = Field(Integer)
    scene = ManyToOne('Scene')

class Object(Entity):
    using_options(tablename='objects')
    scene = ManyToOne('Scene')
    idx = Field(Integer)
    shape = Field(String)
    color_name = Field(String)
    color_r = Field(Float)
    color_g = Field(Float)
    color_b = Field(Float)
    position_x = Field(Float)
    position_y = Field(Float)
    position_z = Field(Float)
    quaternion_x = Field(Float)
    quaternion_y = Field(Float)
    quaternion_z = Field(Float)
    quaternion_w = Field(Float)
    bb_min_x = Field(Float)
    bb_min_y = Field(Float)
    bb_min_z = Field(Float)
    bb_max_x = Field(Float)
    bb_max_y = Field(Float)
    bb_max_z = Field(Float)
    aabb_min_x = Field(Float)
    aabb_min_y = Field(Float)
    aabb_min_z = Field(Float)
    aabb_max_x = Field(Float)
    aabb_max_y = Field(Float)
    aabb_max_z = Field(Float)

class SpatialRelation(Entity):
    using_options(tablename='spatial_relations')
    scene = ManyToOne('Scene')
    domain = Field(String) # this can be a plane 'xy' or an axis 'z'
    calculus = Field(String)
    relation = Field(String)
    arg1 = Field(String)
    arg2 = Field(String)
    reference = Field(String)

class UserInput(Entity):
    using_options(tablename='user_inputs')
    scene = ManyToOne('Scene')
    user = Field(String)
    text = Field(String)
    sentences = OneToMany('Sentence')

class Sentence(Entity):
    using_options(tablename='sentences')
    idx = Field(Integer)
    text = Field(String)
    parsetree = Field(String)
    user_input = ManyToOne('UserInput')
    tokens = OneToMany('Token')

class Token(Entity):
    using_options(tablename='tokens')
    sentence = ManyToOne('Sentence')
    idx = Field(Integer)
    word = Field(String)
    lemma = Field(String)
    pos = Field(String)
    ner = Field(String)
    nner = Field(String)
    off_begin = Field(Integer)
    off_end = Field(Integer)
    object_annotation = OneToOne('ObjectAnnotation')

class Dependency(Entity):
    using_options(tablename='dependencies')
    sentence = ManyToOne('Sentence')
    type = Field(String)
    governor = Field(String)
    dependent = Field(String)

class ObjectAnnotation(Entity):
    using_options(tablename='object_annotations')
    token = ManyToOne('Token')
    obj = ManyToOne('Object')



setup_all()
