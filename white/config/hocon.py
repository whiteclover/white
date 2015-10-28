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


class HoconRoot(object):

    def __init__(self, value=None, substitutions=None):
        self.value = value or HoconValue()
        self.substitutions = substitutions or []


class MightBeAHoconObject:
    pass


class HoconValue(MightBeAHoconObject):

    def __init__(self, values=None):
        self.values = values or []

    def atKey(self, key):
        o = HoconObject()
        o.getOrCreate(key)
        o[key] = self
        r = HoconValue().appendValue(o)
        return Config(HoconRoot(r))

    def getObject(self):
        raw = self.values[0] if len(self.values) >= 1 else None

        if isinstance(raw, HoconObject):
            return raw

        if isinstance(raw, MightBeAHoconObject):
            if raw.isObject():
                return raw.getObject()
        return raw

    def isObject(self):
        return self.getObject() is not None

    def appendValue(self, value):
        # if isinstance(value, HoconElement):
        self.values.append(value)
        return self

    def clear(self):
        self.values[:] = []

    def newValue(self, value):
        self.clear()
        self.appendValue(value)

    def isString(self):
        return all([v.isString() for v in self.values])

    def getArray(self):
        x = []
        for arr in self.values:
            if arr.isArray():
                x.extend(arr.getArray())
        return x

    def getList(self):
        return [e.getString() for e in self.getArray()]

    def isArray(self):
        return self.getList() is not None

    def get(self):
        if len(self.values) == 1:
            return self.values[0].getObject()
        return [_.getObject() for _ in self.values]

    def contat(self):
        return "".join([_.getString() for _ in self.values])

    def getChildObject(self, key):
        return self.getObject().getKey(key)

    def getBoolean(self):
        v = self.getString()
        if v == 'on':
            return True
        if v == 'off':
            return False

        if v == 'true':
            return True
        if v == 'false':
            return False
        raise ValueError("Unknown boolean format: " + v)

    def getString(self):
        if self.isString():
            return self.contat()

        return None

    def _getByType(self, cast):
        v = self.getString()
        try:
            return cast(v)
        except:
            raise TypeError("Invalid %s format for: %s" % (str(cast), v))

    def getInt(self):
        return self._getByType(int)

    def getFloat(self):
        return self._getByType(float)

    def getLong(self):
        return self._getByType(long)

    def getIntList(self):
        return [e.getInt() for e in self.getArray()]

    def getLongList(self):
        return [e.getLong() for e in self.getArray()]

    def getFloatList(self):
        return [e.getFloat() for e in self.getArray()]

    def __str__(self):
        if self.isString():
            return self.getString()

        if len(self.values) > 1:
            return str.format("[{0}]", "|".join([e.getString() for e in self.getList()]))

        if self.isObject():
            return str(self.getObject())


class HoconElement(object):
    pass


class HoconArray(HoconElement, list):

    def isString(self):
        return False

    def getString(self):
        raise BaseException(" error")

    def isArray(self):
        return True

    def getObject(self):
        return [_.get() for _ in self]

    def getArray(self):
        return self


class HoconLiteral(HoconElement):

    def __init__(self, text=''):
        self.value = text

    def isString(self):
        return True

    def getString(self):
        return self.value

    def isArray(self):
        return False

    def isObject(self):
        return False

    def getObject(self):
        return self.value

    def getList(self):
        raise BaseException(" error")

    def __str__(self):
        return self.value


class HoconObject(HoconElement, dict):

    def isString(self):
        return False

    def getString(self):
        raise BaseException(" error")

    def isArray(self):
        return False

    def isObject(self):
        return True

    def getObject(self):
        return {k: v.get() for k, v in self.iteritems()}

    def getList(self):
        raise BaseException(" error")

    def getKey(self, key):
        return self.get(key)

    def getOrCreateKey(self, key):
        if key in self:
            return self.get(key)

        child = HoconValue()
        self[key] = child

        return child

    def merge(self, obj):
        for k, v in obj.iteritems():
            if k in self:
                thisItem = self[key]
                if item.isObject() and v.value.isObject():
                    thisItems.getObject.merge(v.value.getObject())
            else:
                self[k] = v.value


class HoconSubstitution(HoconElement, MightBeAHoconObject):

    def __init__(self, path=None):
        self.path = path
        self.resolvedValue = None

    def isString(self):
        return self.resolvedValue and self.resolvedValue.isString()

    def getString(self):
        return self.resolvedValue and self.resolvedValue.getString()

    def isArray(self):
        return self.resolvedValue.isArray()

    def getList(self):
        return self.resolvedValue.getList()

    def isObject(self):
        return self.resolvedValue and self.resolvedValue.isObject()

    def getObject(self):
        return self.resolvedValue.getObject()


class TokenType(object):

    Comment = 1
    Key = 2
    LiteralValue = 3
    Assign = 4
    ObjectStart = 5
    ObjectEnd = 6
    Dot = 7
    EoF = 8
    ArrayStart = 9
    ArrayEnd = 10
    Comma = 11
    Substitute = 12
    Include = 13


class Token(object):

    def __init__(self,  tokenType, soureIndex, length, value=None):
        self.soureIndex = soureIndex
        self.length = length
        self.value = value
        self.tokenType = tokenType

    @staticmethod
    def Key(key, sourceIndex, sourceLength):
        return Token(TokenType.Key, sourceIndex, sourceLength, key)

    @staticmethod
    def Substitution(path, sourceIndex, sourceLength):
        return Token(TokenType.Substitute, sourceIndex, sourceLength, path)

    @staticmethod
    def LiteralValue(value, sourceIndex, sourceLength):
        return Token(TokenType.LiteralValue, sourceIndex, sourceLength, value)

    @staticmethod
    def Include(path, sourceIndex, sourceLength):
        return Token(TokenType.Include, sourceIndex, sourceLength, path)


from .errors import HoconParserException, HoconTokenizerException
from ._config import Config


class Parser(object):

    def __init__(self):
        self._substitutions = []
        self._reader = None
        self._includeCallback = None
        self._diagnosticsStack = []
        self._root = None

    def pushDiagnostics(self, message):
        self._diagnosticsStack.append(message)

    def popDiagnostics(self):
        self._diagnosticsStack.pop()

    def getDiagnosticsStackTrace(self):
        currentPath = "".join(self._diagnosticsStack)
        return str.format("Current path: {0}", currentPath)

    @staticmethod
    def parse(text, includeCallback, pystyle=False):
        return Parser().parseText(text, includeCallback, pystyle)

    def parseText(self, text, includeCallback, pystyle):
        self._includeCallback = includeCallback
        self._root = HoconValue()
        self._reader = HoconTokenizer(text, pystyle)
        self._reader.pullWhitespaceAndComments()
        self.parseObject(self._root, True, "")
        c = Config(HoconRoot(self._root, []))

        for sub in self._substitutions:

            res = c.getValue(sub.path)

            if res is None:
                raise HoconParserException(
                    "Unresolved substitution:" + sub.path)
            sub.resolvedValue = res
        return HoconRoot(self._root, self._substitutions)

    def parseObject(self, current, root, currentPath):
        try:
            self.pushDiagnostics("{")
            if current.isObject():
                # Todo: blabla
                # the value of this object is already an dict
                pass
            else:
                current.newValue(HoconObject())
            currentObject = current.getObject()

            while not self._reader.eof:
                t = self._reader.pullNext()
                # to do add include context and config parse
                if t.tokenType == TokenType.Include:
                    included = self._includeCallback(t.value)
                    substitutions = included.substitutions
                    for substitution in substitutions:
                        substitution.path = currentPath + "." + substitution.path
                    self._substitutions.extend(substitutions)
                    otherObj = included.value.getObject()
                    current.getObject().merge(otherObj)

                elif t.tokenType == TokenType.EoF:
                    # not empty path
                    if currentPath:
                        raise HoconParserException(str.format(
                            "Expected end of object but found EoF {0}", self.getDiagnosticsStackTrace()))

                elif t.tokenType == TokenType.Key:
                    value_ = currentObject.getOrCreateKey(t.value)

                    value_.clear()
                    nextPath = t.value if currentPath == "" else currentPath + "." + t.value
                    self.parseKeyContent(value_, nextPath)
                    if not root:
                        return

                elif t.tokenType == TokenType.ObjectEnd:
                    return
        finally:
            self.popDiagnostics()

    def parseKeyContent(self, value, currentPath):
        try:

            last = currentPath.rsplit(".", 1)[-1]
            self.pushDiagnostics(str.format("{0} = ", last))
            while not self._reader.eof:
                t = self._reader.pullNext()
                if t.tokenType == TokenType.Dot:
                    self.parseObject(value, False, currentPath)
                    return

                elif t.tokenType == TokenType.Assign:

                    if not value.isObject():
                        value.clear()
                    self.parseValue(value, currentPath)
                    return

                elif t.tokenType == TokenType.ObjectStart:
                    self.parseObject(value, True, currentPath)
                    return

        finally:
            self.popDiagnostics()

    def parseValue(self, current, currentPath):

        if self._reader.eof:
            raise HoconParserException(
                "End of file reached while trying to read a value")

        self._reader.pullWhitespaceAndComments()
        start = self._reader.index

        try:
            while self._reader.isValue():
                t = self._reader.pullValue()
                if t.tokenType == TokenType.EoF:
                    pass

                elif t.tokenType == TokenType.LiteralValue:

                    if current.isObject():
                        # needed to allow for override objects
                        current.clear()
                    lit = HoconLiteral(t.value)
                    current.appendValue(lit)

                elif t.tokenType == TokenType.ObjectStart:
                    self.parseObject(current, True, currentPath)

                elif t.tokenType == TokenType.ArrayStart:
                    arr = self.parseArray(currentPath)
                    current.appendValue(arr)

                elif t.tokenType == TokenType.Substitute:
                    sub = self.parseSubstitution(t.value)
                    self._substitutions.append(sub)
                    current.appendValue(sub)

                elif self._reader.isSpaceOrTab():
                    self.parseTrailingWhitespace(current)

            self.ignoreComma()

        except Exception as e:
            raise HoconParserException(
                str.format("{0} {1}", str(e), self.getDiagnosticsStackTrace()))

        finally:
            # no value was found, tokenizer is still at the same position
            if self._reader.index == start:
                raise HoconParserException(str.format("Hocon syntax error: {0}\r{1}", self._reader.getHelpTextAtIndex(
                    start), self.getDiagnosticsStackTrace()))

    def parseTrailingWhitespace(self, current):
        ws = self._reader.pullSpaceOrTab()
        while len(ws.value) > 0:
            wsList = HoconLiteral(ws.value)
            current.appendValue(wsList)

    def parseSubstitution(self, value):
        return HoconSubstitution(value)

    def parseArray(self, currentPath):
        try:
            self.pushDiagnostics("|")
            arr = HoconArray()
            while (not self._reader.eof) and (not self._reader.isArrayEnd()):
                v = HoconValue()
                self.parseValue(v, currentPath)
                arr.append(v)
                self._reader.pullWhitespaceAndComments()
            self._reader.pullArrayEnd()
            return arr
        finally:
            self.popDiagnostics()

    def ignoreComma(self):
        if self._reader.isComma():
            self._reader.pullComma()


class Tokenizer(object):

    def __init__(self, text, pystyle=False):
        self._text = text
        self._index = 0
        self._indexStack = []
        self.pystyle = pystyle

    @property
    def length(self):
        return len(self._text)

    @property
    def index(self):
        return self._index

    def push(self):
        self._indexStack.append(self._index)

    def pop(self):
        self._indexStack.pop()

    @property
    def eof(self):
        return self._index >= len(self._text)

    def match(self, pattern):

        if (len(pattern) + self._index) > len(self._text):
            return False
        end = self._index + len(pattern)
        if self._text[self._index:end] == pattern:
            return True
        return False

    def matches(self, *patterns):
        for pattern in patterns:
            m = self.match(pattern)
            if m:
                return True
        return False

    def take(self, length):
        if(self._index + length) > len(self._text):
            return None
        end = self._index + length
        s = self._text[self._index:end]
        self._index += length
        return s

    def peek(self):
        if self.eof:
            return chr(0)

        return self._text[self._index]

    def takeOne(self):

        if self.eof:
            return chr(0)
        index = self._index
        self._index += 1
        return self._text[index]

    def pullWhitespace(self):
        while (not self.eof) and self.peek().isspace():
            self.takeOne()

    def getHelpTextAtIndex(self, index, length=0):
        if length == 0:
            length = self.length - index
        l = min(20, length)
        end = l + index
        snippet = self._text[index:end]
        if length > 1:
            return snippet + "..."
        snippet = snippet.replace("\r", "\\r").replace("\n", "\\n")
        return str.format("at index {0}: `{1}`", index, snippet)

import re


class HoconTokenizer(Tokenizer):

    NotInUnquotedKey = "$\"{}[]:=,#`^?!@*&\\."
    NotInUnquotedText = "$\"{}[]:=,#`^?!@*&\\"

    def pullWhitespaceAndComments(self):
        while True:
            self.pullWhitespace()
            while self.isStartOfComment():
                self.pullComment()
            if not self.isWhitespace():
                break

    def pullRestOfLine(self):
        sb = ""
        while not self.eof:
            c = self.takeOne()
            if c == '\n':
                break
            if c == '\r':
                continue
            sb += c
        return sb.strip()

    def pullNext(self):
        self.pullWhitespaceAndComments()
        start = self.index
        if self.isDot():
            return self.pullDot()
        if self.isObjectStart():
            return self.pullStartOfObject()
        if self.isObjectEnd():
            return self.pullObjectEnd()
        if self.isAssignment():
            return self.pullAssignment()

        if self.isInclude():
            return self.pullInclude()

        if self.isStartOfQuotedKey():
            return self.pullQuotedKey()

        if self.isUnquotedKeyStart():
            return self.pullUnquotedKey()

        if self.isArrayStart():
            return self.pullArrayStart()

        if self.isArrayEnd():
            return self.pullArrayEnd()

        if self.eof:
            return Token(TokenType.EoF, self.index, 0)

        raise HoconTokenizerException(str.format(
            "Unknown token: {0}", self.getHelpTextAtIndex(start)))

    def isStartOfQuotedKey(self):
        return self.match("\"")

    def pullArrayEnd(self):
        start = self.index
        if not self.isArrayEnd():
            raise HoconTokenizerException(str.format(
                "Expected end of array {0}", self.getHelpTextAtIndex(start)))
        self.takeOne()
        return Token(TokenType.ArrayEnd, start, self.index - start)

    def isArrayEnd(self):
        return self.match("]")

    def isArrayStart(self):
        return self.match("[")

    def pullArrayStart(self):
        start = self.index
        self.takeOne()
        return Token(TokenType.ArrayStart, self.index, self.index - start)

    def pullDot(self):
        start = self.index
        self.takeOne()
        return Token(TokenType.Dot, start, self.index - start)

    def pullComma(self):
        start = self.index
        self.takeOne()
        return Token(TokenType.Comma, start, self.index - start)

    def pullStartOfObject(self):
        start = self.index
        self.takeOne()
        return Token(TokenType.ObjectStart, start, self.index - start)

    def pullObjectEnd(self):
        start = self.index
        if not self.isObjectEnd():
            raise HoconTokenizerException(str.format(
                "Expected end of object {0}", self.getHelpTextAtIndex(self.index)))
        self.takeOne()
        return Token(TokenType.ObjectEnd, start, self.index - start)

    def pullAssignment(self):
        start = self.index
        self.takeOne()
        return Token(TokenType.Assign, start, self.index - start)

    def isComma(self):
        return self.match(",")

    def isDot(self):
        return self.match(".")

    def isObjectStart(self):
        return self.match("{")

    def isObjectEnd(self):
        return self.match("}")

    def isAssignment(self):
        return self.matches("=", ":")

    def isStartOfQuotedText(self):
        return self.match("\"")

    def isStartOfTripleQuotedText(self):
        return self.match("\"\"\"")

    def pullComment(self):
        start = self.index
        self.pullRestOfLine()
        return Token(TokenType.Comment, start, self.index - start)

    def pullUnquotedKey(self):
        start = self.index
        sb = ""
        while (not self.eof) and self.isUnquotedKey():
            sb += self.takeOne()
        return Token.Key(sb.strip(), start, self.index - start)

    def isUnquotedKey(self):
        return (not self.eof) and (not self.isStartOfComment()) and (self.peek() not in self.NotInUnquotedKey)

    def isUnquotedKeyStart(self):
        return (not self.eof) and (not self.isWhitespace()) and (not self.isStartOfComment()) and (self.peek() not in self.NotInUnquotedKey)

    def isWhitespace(self):
        return self.peek().isspace()

    def isWhitespaceOrComment(self):
        return self.isWhitespace() or self.isStartOfComment()

    def pullTripleQuotedText(self):
        start = self.index
        sb = ''
        self.take(3)
        while (not self.eof) and (not self.match("\"\"\"")):
            if self.match("\\"):
                sb += self.pullEscapeSequence()
            else:
                sb += self.takeOne()

        if self.match("\""):
            raise HoconTokenizerException(str.format(
                "Expected end of tripple quoted string {0}", self.getHelpTextAtIndex(self.index)))

        self.take(3)
        return Token.LiteralValue(sb, start, self.index - start)

    def pullQuotedText(self):
        start = self.index
        sb = ''
        self.takeOne()
        while (not self.eof) and not self.match("\""):
            if self.match("\\"):
                sb += self.pullEscapeSequence()
            else:
                sb += self.takeOne()

        self.takeOne()
        return Token.LiteralValue(sb, start, self.index - start)

    def pullQuotedKey(self):
        start = self.index
        sb = ''
        self.take(3)
        while (not self.eof) and (not self.match("\"")):
            if self.match("\\"):
                sb += self.pullEscapeSequence()
            else:
                sb += self.takeOne()

        self.takeOne()
        return Token.Key(sb, start, self.index - start)

    def pullInclude(self):
        start = self.index
        self.take(len("include"))
        self.pullWhitespaceAndComments()
        rest = self.pullQuotedText()
        unQuote = rest.value
        return Token.Include(unQuote, start, self.index - start)

    def pullEscapeSequence(self):
        start = self.index

        escaped = self.takeOne()
        if escaped == '"':
            return "\""
        if escaped == '\\':
            return "\\"
        if escaped == '/':
            return "/"
        if escaped == 'b':
            return "\b"
        if escaped == 'f':
            return "\f"
        if escaped == 'n':
            return "\n"
        if escaped == 'r':
            return "\r"
        if escaped == 't':
            return "\t"
        if escaped == 'u':
            hexStr = "0x" + self.take(4)
            j = hex(hexStr)
            return chr(j)
        raise HoconTokenizerException(str.format(
            "Unknown escape code `{0}` {1}", escaped, self.getHelpTextAtIndex(start)))

    def isStartOfComment(self):
        return self.matches("#", "//")

    def pullValue(self):
        start = self.index
        if self.isObjectStart():
            return self.pullStartOfObject()

        if self.isStartOfTripleQuotedText():
            return self.pullTripleQuotedText()

        if self.isStartOfQuotedText():
            return self.pullQuotedText()

        if self.isUnquotedText():
            return self.pullUnquotedText()
        if self.isArrayStart():
            return self.pullArrayStart()
        if self.isArrayEnd():
            return self.pullArrayEnd()
        if self.isSubstitutionStart():
            return self.pullSubstitution()

        raise HoconTokenizerException(str.format(
            "Expected value: Null literal, Array, Quoted Text, Unquoted Text, Triple quoted Text, Object or End of array {0}", self.getHelpTextAtIndex(start)))

    def isSubstitutionStart(self):
        return self.match("${")

    def isInclude(self):
        self.push()
        try:
            if self.match("include"):
                self.take(len("include"))

                if self.isWhitespaceOrComment():

                    self.pullWhitespaceAndComments()

                    if self.isStartOfQuotedText():
                        self.pullQuotedText()
                        return True
            return False

        finally:
            self.pop()

    def pullSubstitution(self):
        start = self.index
        sb = ''
        self.take(2)
        while ((not self.eof) and self.isUnquotedText()):
            sb += self.takeOne()

        self.takeOne()
        return Token.Substitution(sb.strip(), start, self.index - start)

    def isSpaceOrTab(self):
        return self.matches(" ", "\t", "\v")

    def isStartSimpleValue(self):
        if self.isSpaceOrTab():
            return True

        if self.isUnquotedText():
            return True

        return False

    def pullSpaceOrTab(self):
        start = self.index
        sb = ''
        while self.isSpaceOrTab():
            sb += self.takeOne()

        return Token.LiteralValue(sb, start, self.index - start)

    def pullUnquotedText(self):
        start = self.index
        value = ''
        while (not self.eof) and self.isUnquotedText():
            value += self.takeOne()

        if self.pystyle:
            value = self.convertToPyValue(value)

        return Token.LiteralValue(value, start, self.index - start)

    FLOAT_VAR = re.compile(r'^-?\d+\.\d+$')
    INT_VAR = re.compile(r'^-?\d+$')
    BOOL_VAR = {'true': True, 'false': False, 'on': True, 'off': False}

    def convertToPyValue(self, value):
        if value in self.BOOL_VAR:
            return self.BOOL_VAR[value]

        if self.INT_VAR.match(value):
            # it will auto cast to long if too large
            return int(value)

        if self.FLOAT_VAR.match(value):
            return float(value)

        return value

    def isUnquotedText(self):
        return (not self.eof) and (not self.isWhitespace()) and (not self.isStartOfComment()) and (self.peek() not in self.NotInUnquotedText)

    def pullSimpleValue(self):
        start = self.index

        if self.isSpaceOrTab():
            return self.pullSpaceOrTab()
        if self.isUnquotedText():
            return self.pullUnquotedText()

        raise HoconTokenizerException(str.format(
            "No simple value found {0}", self.getHelpTextAtIndex(start)))

    def isValue(self):

        if self.isArrayStart():
            return True
        if self.isObjectStart():
            return True
        if self.isStartOfTripleQuotedText():
            return True
        if self.isSubstitutionStart():
            return True
        if self.isStartOfQuotedText():
            return True
        if self.isUnquotedText():
            return True

        return False
