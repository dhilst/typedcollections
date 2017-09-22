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

from abc import ABCMeta
from collections import UserDict, UserList
from functools import wraps

if __debug__:
    class TypedList(UserList):
        '''Check MultiTypedDict.'''
        type = type(None),

        def _check(self, a):
            if not issubclass(type(a), self.__class__.type):
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
            if not issubclass(type(v), self.__class__.type[i]):
                raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type[i], type(v)))

        def __init__(self, *args):
            super().__init__()
            for i, v in enumerate(args):
                self._check(i, v)
            self.data = list(args)

        def __setitem__(self, i, v):
            self._check(i, v)
            self.data[i] = v

    class MultiTypedDict(UserDict):
        '''
        Typed list and dictionary. The types are passed as class attributes. For
        TypedList the 'type' class attribute is used, for MultiTypedDict each attribute
        consists of an key. The keys types are not checked. Take a look at doctest
        for examples.

        >>> class FooList(TypedList):
        ...     type = int,
        ...
        >>> class FooMultiList(MultiTypedList):
        ...     type = int,str
        ...
        >>> class FooDict(MultiTypedDict):
        ...     foo = int,
        ...     bar = FooList,
        ...     tar = FooMultiList,
        ...     zar = str,type(None)
        ...
        >>> f = FooDict(foo=1, bar=FooList(1,2,3), tar=FooMultiList(1,'foo'), zar='hello')
        >>> # {'foo': 1, 'bar': [1, 2, 3], 'tar': [1, 'foo'], 'zar': 'hello'}
        >>>
        >>> f['foo'] = 'invalid' # Setting to invalid type raise exceptions.
        Traceback (most recent call last):
        ...
        TypeError: FooDict["foo"] expect one of (<class 'int'>,) but found <class 'str'>.
        >>>
        >>> f['bar'][0] = 'invalid' # Also true for TypedList.
        Traceback (most recent call last):
        ...
        TypeError: FooList expect (<class 'int'>,) type but found <class 'str'>.
        >>> 
        >>> f['tar'][0] = 2 # No problem
        >>> f['tar'][0] = 'invalid' # ops wrong value
        Traceback (most recent call last):
        ...
        TypeError: FooMultiList expect <class 'int'> type but found <class 'str'>.
        >>>
        >>> FooDict(foo='invalid') # Instantiation is protected too.
        Traceback (most recent call last):
        ...
        TypeError: FooDict["foo"] expect one of (<class 'int'>,) but found <class 'str'>.
        >>>
        >>> FooList('invalid') # Also true for lists.
        Traceback (most recent call last):
        ...
        TypeError: FooList expect (<class 'int'>,) type but found <class 'str'>.
        ''' 

        def _check(self, k, v):
            t = getattr(self.__class__, k)
            if not issubclass(type(v),t):
                raise TypeError('{}["{}"] expect one of {} but found {}.'.format(self.__class__.__name__, k, t, type(v)))

        def __init__(self, **kwargs):
            super().__init__()
            for k,v in kwargs.items():
                self._check(k,v)
            self.data = kwargs.copy()

        def __setitem__(self, k,v):
            self._check(k,v)
            self.data[k] = v
else:
    TypedList = UserList
    TypedDict = UserDict
    MultiTypedDict = UserDict
    MultiTypedList = UserList

def checkarguments(*t_args, **t_kwargs):
    '''Check arguments types with issubclass before calling the function.

    if __debug__ is false it just return the function, so no performance
    penality happend. __debug__ is false when running python in optimized
    mode.

    >>> @checkarguments(int, int, int)
    ... def foo(a,b,c):
    ...    return a + b + c
    ...
    >>> foo(1,2,3)
    6
    >>> foo('foo',2,3)
    Traceback (most recent call last):
    ...
    TypeError: foo positional argument 0 expects <class 'int'> but <class 'str'> found.
    >>>
    >>> @checkarguments(a=int, b=int, c=(int,type(None)))
    ... def bar(*args,a,b,c):
    ...     return a + b + (c if c is not None else 0)
    ...
    >>> bar(a=1,b=2,c=3)
    6
    >>> bar(a=1,b=2,c=None)
    3
    >>> bar(a='str',b=2,c=3)
    Traceback (most recent call last):
    ...
    TypeError: bar() keyword argument "a" expects <class 'int'> but <class 'str'> found.
    '''
    def decorator(func):
        if __debug__:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for i, (t, v) in enumerate(zip(t_args, args)):
                    if not issubclass(type(v), t if isinstance(t, tuple) else (t,)):
                        raise TypeError('{} positional argument {} expects {} but {} found.'\
                                        .format(func.__name__, i, t, type(v)))
                for (tk, tv), (ak, av) in (zip(t_kwargs.items(), kwargs.items())):
                    if not issubclass(type(av), tv if isinstance(tv, tuple) else (tv,)):
                        raise TypeError('{}() keyword argument "{}" expects {} but {} found.'\
                                .format(func.__name__, ak, tv, type(av)))
                return func(*args, **kwargs)
            return wrapper 
        else: # not __debug__
            return func
    return decorator

if __name__ == '__main__':
    import doctest
    doctest.testmod()


