import unittest

from . import MultiTypedDict, MultiTypedList, TypedList, TypedDict


class MyMTD(MultiTypedDict):
    i = int,
    s = str,


class MyTD(TypedDict):
    value_type = int,


class MyMTL(MultiTypedList):
    type = int,int,int


class MyTL(TypedList):
    type = int,


class Test(unittest.TestCase):
    def test(self):
        mtd = MyMTD(i=1, s='hello')
        mtl = MyMTL(1,2,3)
        td  = MyTD(a=1,b=1,c=1)   
        tl  = MyTL(1,2)

        if __debug__:
            self.assertRaises(TypeError, MyMTD,1,2)
            self.assertRaises(TypeError, MyMTL,'str')
            self.assertRaises(TypeError, lambda: MyTD(a='str'))
            self.assertRaises(TypeError, MyTL,'str')
            def raiseTE(): mtd['i'] = 'not an int'
            self.assertRaises(TypeError, raiseTE)
            def raiseTE(): mtl[0] = 'str'
            self.assertRaises(TypeError, raiseTE)
            def raiseTE(): td['a'] = 'str'
            self.assertRaises(TypeError, raiseTE)
            def raiseTE(): tl[0] = 'str'
            self.assertRaises(TypeError, raiseTE)



            

        

