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

import six
from functools import wraps
try:
    from collections import UserDict, UserList
except ImportError:
    from UserDict import UserDict
    from UserList import UserList


if __debug__:
    class TypedList(UserList):
        '''Check MultiTypedDict.'''
        type = type(None),

        def _check(self, a):
            if not issubclass(type(a), self.__class__.type):
                raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type, type(a)))
        
        def __init__(self, *args):
            super(TypedList, self).__init__()
            for a in args:
                self._check(a)
            self.data = list(args)

        def __setitem__(self, item, val):
            self._check(val)
            self.data[item] = val 

    class TypedDict(UserDict):
        key_type = str,
        value_type = type(None),

        def __setitem__(self, key, val):
            if not issubclass(type(key), self.__class__.key_type):
                raise TypeError('{} keys expect type {} but found {}.'.format(self.__class__.__name__, self.__class__.key_type, type(key)))
            if not issubclass(type(val), self.__class__.value_type):
                raise TypeError('{} keys expect type {} but found {}.'.format(self.__class__.__name__, self.__class__.value_type, type(value)))
            self.data[key] = val

    class MultiTypedList(UserList):
        type = type(None),

        def _check(self, i, v):
            if not issubclass(type(v), self.__class__.type[i]):
                raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type[i], type(v)))

        def __init__(self, *args):
            super(MultiTypedList, self).__init__()
            for i, v in enumerate(args):
                self._check(i, v)
            self.data = list(args)

        def __setitem__(self, i, v):
            self._check(i, v)
            self.data[i] = v

    class MultiTypedDict(UserDict):
        '''
        Multi typed dict.

        Types are defined using class attributes.

        >>> class FooMTD(MultiTypedDict):
        ...     foo = int,
        ...     bar = str,
        ...
        >>> f = FooMTD(foo=1, bar='str')
        >>> f == {'foo': 1, 'bar':'str'}
        True
        >>> f['foo'] = 'str' # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: FooMTD["foo"] expect (<... 'int'>,) but <... 'str'> found.
        >>>
        >>> FooMTD(foo=1,bar=2) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        TypeError: FooMTD["bar"] expect (<... 'str'>,) but <... 'int'> found.
        ''' 
        def __init__(self, **kwargs):
            UserDict.__init__(self)
            for k,v in six.iteritems(kwargs):
                self[k] = v

        def __setitem__(self, k, v):
            t = getattr(self.__class__, k)
            vt = type(v)
            if not issubclass(vt, t): 
                raise TypeError('{}["{}"] expect {} but {} found.'.format(
                        self.__class__.__name__, k, t, vt))
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
    >>> foo('foo',2,3) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: foo positional argument 0 expects <... 'int'> but <... 'str'> found.
    >>>
    >>> @checkarguments(a=int, b=int, c=(int,type(None)))
    ... def bar(a,b,c):
    ...     return a + b + (c if c is not None else 0)
    ...
    >>> bar(a=1,b=2,c=3)
    6
    >>> bar(a=1,b=2,c=None)
    3
    >>> bar(a='str',b=2,c=3) # doctest: +ELLIPSIS 
    Traceback (most recent call last):
    ...
    TypeError: bar() keyword argument "a" expects <... 'int'> but <... 'str'> found.
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


