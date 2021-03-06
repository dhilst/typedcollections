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

'''
Overview
--------

Each class at this library represents a typed data structure. The types
are enforced at intialization and when setting a value too. The user
must subclass the desired type and parametrize using class attributes.

Each class attribute is a tuple of possible values. The types are checked
using issubclass builting function. Check the docstring of each class for
examples.

There is a decorator for checking function parameters too.

When running in optimized mode the classes are noped and no parameter checking
happens. So no performance penality should be noticed.
'''

import six
from abc import ABCMeta
from functools import wraps
try:
    from collections import UserDict, UserList
except ImportError:
    from UserDict import UserDict
    from UserList import UserList

if __debug__:
    class TypedList(UserList):
        '''
        Single type list. Values type are defined by type class
        attribute, which is a tuple of possible types.

        >>> class FooTL(TypedList):
        ...     type = int,
        ...

        Initialize as list constructor
        >>> foo = FooTL(1,2,3,4)
        >>> foo == [1,2,3,4]
        True
    
        >>> foo[0] = 10
        '''
        type = type(None),

        def _check(self, a):
            if not issubclass(type(a), self.__class__.type):
                raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type, type(a)))
        
        def __init__(self, *args):
            UserList.__init__(self)
            for a in args:
                self._check(a)
            self.data = list(args)

        def __setitem__(self, item, val):
            self._check(val)
            self.data[item] = val 

    class TypedDict(UserDict):
        '''
        Single type dict. Key type is defined by 
        key_type class attribute (default is str). Value type is defined
        by value_type class attribute (default is type(None), which is useless).

        >>> class FooTD(TypedDict):
        ...    value_type = int, # Types must be a tuple.
        ...

        Construct as dict constructor.
        >>> foo = FooTD(foo=1,bar=2)
        >>> foo == {'foo': 1, 'bar': 2}
        True

        Setting values is protected against wrong types. Both keys
        and values.
        >>> foo[1] = 10 # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: FooTD keys expect type (<... 'str'>,) but found <... 'int'>.

        Initialization is protected against wrong types.
        >>> FooTD(foo='str',bar=2) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: FooTD values expect type (<... 'int'>,) but found <... 'str'>.
        '''

        key_type = str,
        value_type = type(None),

        def __init__(self, **kwargs):
            UserDict.__init__(self)
            for k, v in six.iteritems(kwargs):
                self[k] = v

        def __setitem__(self, key, val):
            if not issubclass(type(key), self.__class__.key_type):
                raise TypeError('{} keys expect type {} but found {}.'.format(self.__class__.__name__, self.__class__.key_type, type(key)))
            if not issubclass(type(val), self.__class__.value_type):
                raise TypeError('{} values expect type {} but found {}.'.format(self.__class__.__name__, self.__class__.value_type, type(val)))
            self.data[key] = val

    class MultiTypedList(UserList):
        '''
        Multi typed list.
        
        Types are positionally defined by assigning a tuple of types to list.
        
        >>> class FooMTL(MultiTypedList):
        ...     type = int,int,str
        ...
        >>> f = FooMTL(1,1,'hello')
        >>> f == [1,1,'hello']
        True
        >>> f[0] = 2
        >>> f == [2,1,'hello']
        True
        '''
        type = type(None),

        def _check(self, i, v):
            if not issubclass(type(v), self.__class__.type[i]):
                raise TypeError('{} expect {} type but found {}.'.format(self.__class__.__name__, self.__class__.type[i], type(v)))

        def __init__(self, *args):
            UserList.__init__(self)
            for i, v in enumerate(args):
                self._check(i, v)
            self.data = list(args)

        def __setitem__(self, i, v):
            self._check(i, v)
            self.data[i] = v

    class _MultiDictTypedMeta(ABCMeta):
        def __init__(cls, name, bases, attrs):
            super(_MultiDictTypedMeta, cls).__init__(name, bases, attrs)
            cls._keys = list(k for k in attrs.keys() if not k.startswith('__'))

    class MultiTypedDict(six.with_metaclass(_MultiDictTypedMeta, UserDict, object)):
        '''
        Multi typed dict.

        Types are defined using class attributes.

        >>> class FooMTD(MultiTypedDict):
        ...     foo = int, # Types must be a tuple
        ...     bar = str,
        ...

        Create instances with a dict like signature.
        >>> f = FooMTD(foo=1, bar='str')
        >>> f == {'foo': 1, 'bar':'str'}
        True
        
        Common dictionary operations are supported since this inherit from
        UserDict.
        >>> list(f.items()) == [('foo', 1), ('bar', 'str')]
        True

        Setting items trigger type assertion. If type is wrong TypeError
        is raised. The key is specified in the error message.

        >>> f['foo'] = 2 # Okay
        >>> f['foo'] = 'str' # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: FooMTD["foo"] expect (<... 'int'>,) but <... 'str'> found.

        Also initializing triggers type assertion.
        >>> FooMTD(foo=1,bar=2) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: FooMTD["bar"] expect (<... 'str'>,) but <... 'int'> found.

        All the field are required. Initializing with missing values raises
        ValueError.
        >>> FooMTD(foo=1) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: FooMTD missing values for the keys ['bar']

        Deleting is prohibited too.
        >>> del f['foo']
        Traceback (most recent call last):
        ...
        RuntimeError: You can't delete values from FooMTD.

        All this properties garantees that the dictionary state is valid, always.
        ''' 
        data = {}

        def __init__(self, **kwargs):
            clskeys = set(self.__class__._keys)
            kwkeys  = set(kwargs.keys())
            if kwkeys != clskeys:
                raise ValueError('{} missing values for the keys {}'.format(
                    self.__class__.__name__, list(clskeys - kwkeys)))
            for k,v in six.iteritems(kwargs):
                self[k] = v

        def __setitem__(self, k, v):
            t = getattr(self.__class__, k)
            vt = type(v)
            if not issubclass(vt, t): 
                raise TypeError('{}["{}"] expect {} but {} found.'.format(
                        self.__class__.__name__, k, t, vt))
            self.data[k] = v

        def __delitem__(self, k):
            raise RuntimeError('You can\'t delete values from {}.'.format(
                self.__class__.__name__))

        
else:
    class BaseDict(UserDict):
        def __init__(self, **kwargs):
            UserDict.__init__(self, kwargs)

    class BaseList(UserList):
        def __init__(self, *args):
            UserList.__init__(self, args)

    class MultiTypedDict(BaseDict): pass
    class MultiTypedList(BaseList): pass
    class TypedDict(BaseDict): pass
    class TypedList(BaseList): pass

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


