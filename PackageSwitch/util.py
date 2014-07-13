#!/usr/bin/python

import os
import glob

S_OP_NONE = 0
S_OP_SAVE = 1
S_OP_RESTORE = 2

def distro_loader(path):
    mod_files = []
    for root, subFolders, files in os.walk(path, topdown=False):
        for file in files:
            split = os.path.splitext(file)
            if len(split) == 2 and split[1] == ".py":
                mod_files.append(split[0])
    modules = map(__import__, mod_files)

    instances = []
    for mod in modules:
        instances.append(mod.module())
    return instances

def meta_loader(path, distro):
    mod_files = []
    for root, subFolders, files in os.walk(path, topdown=False):
        for file in files:
            split = os.path.splitext(file)
            if len(split) == 2 and split[1] == ".py":
                mod_files.append(split[0])
    modules = map(__import__, mod_files)

    instances = []
    for mod in modules:
        instances.append(mod.module(distro))
    return instances
