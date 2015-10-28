#!/usr/bin/env python
#
# Copyright 2015 Self-Released
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


# Human-Optimized Config Object Notation


from copy import deepcopy


class BaseConfig(object):

    def __init__(self, root, fallback=None):
        if root.value == None:
            raise AttributeError(" error")
        self.root = root.value  # HoconValue
        self.substitutions = root.substitutions  # List<HoconSubstitution>
        self.fallback = fallback  # Config

    def getNode(self, path):
        keys = path.split(".")
        currentNode = self.root
        if currentNode is None:
            raise KeyError("Doesn't exist the key:" %(path))
        for key in keys:
            currentNode = currentNode.getChildObject(key)
            if currentNode is None:
                if self.fallback:
                    return self.fallback.getNode(path)
                return None
        return currentNode

    def getConfig(self, path):
        cls = self.__class__
        value = self.getNode(path)
        if self.fallback:
            f = self.fallback.getConfig(path)
            if value is None and f is None:
                return None
            if value is None:
                return f
            return cls(HoconRoot(value).withFallback(f))
        if value is None:
            return None
        return cls(HoconRoot(value))

    def __str__(self):
        if self.root is None:
            return ""
        return str(self.root)

    def toDict(self):
        return self.root.get()

    def withFallback(self, fallback):
        if fallback == self:
            raise Exception(" error")
        clone = deepcopy(self)
        current = clone
        while current.fallback:
            current.fallback
        current.fallback = fallback
        return clone

    def hasPath(self, path):
        return self.getNode(value) is not None

    def append(self, config, fallback):
        fallbackConfig = ConfigFactory.parse(fallback)
        return config.withFallback(fallback)


class Config(BaseConfig):

    def getBoolean(self, path, default=False):
        value = self.getNode(path)
        if value is None:
            return default
        return value.getBoolean()

    def getInt(self, path, default=0):
        value = self.getNode(path)
        if value is None:
            return default
        return value.getInt()

    def getLong(self, path, default=0):
        value = self.getNode(path)
        if value is None:
            return default
        return value.getLong()

    def get(self, path, default=None):
        value = self.getNode(path)
        if value is None:
            return default
        return value.getString()

    getString = get

    def getFloat(self, path, default=0.0):
        value = self.getNode(path)
        if value is None:
            return default
        return value.getFloat()

    def getBooleanList(self, path):
        value = self.getNode(path)

        return value.getBooleanList()

    def getFloatList(self, path):
        value = self.getNode(path)

        return value.getFloatList()

    def getIntList(self, path):
        value = self.getNode(path)

        return value.getIntList()

    def getList(self, path):
        value = self.getNode(path)

        return value.getList()

    def getLongList(self, path):
        value = self.getNode(path)

        return value.getLongList()

    def getValue(self, path):
        return self.getNode(path)


class PyConfig(BaseConfig):

    def get(self, path, default=None):
        value = self.getNode(path)
        if value is None:
            return default
        return value.get()

from .hocon import Parser, HoconRoot


class ConfigFactory(object):

    @classmethod
    def empty(cls):
        return cls.parse("")

    @classmethod
    def parse(cls, hocon, func=None, pystyle=False):
        res = Parser.parse(hocon, func, pystyle)
        configCls = PyConfig if pystyle else Config
        return configCls(res)

    @classmethod
    def parseFile(cls, path, pystyle=False):
        with open(path) as f:
            content = f.read()
            return cls.parse(content, pystyle=pystyle)

    @classmethod
    def fromJson(cls, jsonObj, pystyle=False):
        import json
        text = json.dumps(jsonObj)
        return cls.parse(text, pystyle)
