# Copyright 2017 Daniel Hilst Selli <danielhilst@gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import UserDict, UserList

class TypedList(UserList):
    '''Check TypedDict.'''
    type = type(None),

    def _check(self, a):
        if not isinstance(a, self.__class__.type):
            raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type, type(a)))
    
    def __init__(self, *args):
        super().__init__()
        for a in args:
            self._check(a)
        self.data = list(args)

    def __setitem__(self, item, val):
        self._check(val)
        self.data[item] = val 

class MultiTypedList(UserList):
    type = type(None),

    def _check(self, i, v):
        if not isinstance(v, self.__class__.type[i]):
            raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type[i], type(v)))

    def __init__(self, *args):
        super().__init__()
        for i, v in enumerate(args):
            self._check(i, v)
        self.data = list(args)

    def __setitem__(self, i, v):
        self._check(i, v)
        self.data[i] = v

class TypedDict(UserDict):
    '''
    Typed list and dictionary. The types are passed as class attributes. For
    TypedList the 'type' class attribute is used, for TypedDict each attribute
    consists of an key. The keys types are not checked. Take a look at doctest
    for examples.

    >>> class FooList(TypedList):
    ...     type = int,
    ...
    >>> class FooMultiList(MultiTypedList):
    ...     type = int,str
    ...
    >>> class FooDict(TypedDict):
    ...     foo = int,
    ...     bar = FooList,
    ...     tar = FooMultiList,
    ...     zar = str,type(None)
    ...
    >>> f = FooDict(foo=1, bar=FooList(1,2,3), tar=FooMultiList(1,'foo'), zar='hello')
    >>> f
    {'foo': 1, 'bar': [1, 2, 3], 'tar': [1, 'foo'], 'zar': 'hello'}
    >>>
    >>> f['foo'] = 'invalid' # Setting to invalid type raise exceptions.
    Traceback (most recent call last):
    ...
    TypeError: FooDict["foo"] expect on of (<class 'int'>,) but found <class 'str'>.
    >>>
    >>> f['bar'][0] = 'invalid' # Also true for TypedList.
    Traceback (most recent call last):
    ...
    TypeError: FooList expect invalid type but found (<class 'int'>,).
    >>> f['tar'][0] = 2 # No problem
    >>> f['tar'][0] = 'invalid' # ops wrong value
    Traceback (most recent call last):
    ...
    TypeError: FooMultiList expect <class 'int'> type but found <class 'str'>.
    >>>
    >>> FooDict(foo='invalid') # Instantiation is protected too.
    Traceback (most recent call last):
    ...
    TypeError: FooDict["foo"] expect on of (<class 'int'>,) but found <class 'str'>.
    >>>
    >>> FooList('invalid') # Also true for lists.
    Traceback (most recent call last):
    ...
    TypeError: FooList expect invalid type but found (<class 'int'>,).
    ''' 

    def _check(self, k, v):
        t = getattr(self.__class__, k)
        if not isinstance(v,t):
            raise TypeError('{}["{}"] expect one of {} but found {}.'.format(self.__class__.__name__, k, t, type(v)))

    def __init__(self, **kwargs):
        super().__init__()
        for k,v in kwargs.items():
            self._check(k,v)
        self.data = kwargs.copy()

    def __setitem__(self, k,v):
        self._check(k,v)
        self.data[k] = v



