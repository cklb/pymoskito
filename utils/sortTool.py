#! /usr/bin/python2
# -*- coding: utf-8 -*-

def sortTree(dataList, sortKeyPath):
'''
helper method for data sorting
'''
    result = {}
    for elem in dataList:
        sortName = _getSubValue(elem, sortKeyPath)
        if not result.has_key(sortName):
            result.update({sortName: {}})
        
        while elem:
            val, keys = _removeDeepest(elem)
            if keys:
                _addSubVal(result[sortName], keys, val)

    return result

def _getSubValue(source, keyPath):
    subDict = source
    for key in keyPath:
        subDict = subDict[key]

    return subDict
      
def _removeDeepest(topDict, keys=None):
    '''
    iterates recursivly over dict and removes deepst entry.
    returnes entry and path to entry
    '''
    if not keys:
        keys = []

    for key in topDict.keys():
        val = topDict[key]
        print 'looking into:', key, val
        if isinstance(val, dict):
            if val:
                keys.append(key)
                return _removeDeepest(val, keys)
            else:
                del topDict[key]
                continue
        else:
            del topDict[key]
            keys.append(key)
            print 'leaving with:',keys
            return val, keys

    return None, None

def _addSubVal(topDict, keys, val):
    if len(keys) == 1:
        #we are here
        if keys[0] in topDict:
            topDict[keys[0]].append(val)
        else:
            topDict.update({keys[0]: [val]})
        return

    #keep iterating
    if keys[0] not in topDict:
        topDict.update({keys[0]: {}})
    
    _addSubVal(topDict[keys[0]], keys[1:], val)
    return

