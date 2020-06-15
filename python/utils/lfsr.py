#a Copyright
#  
#  This file 'dprintf.py' copyright Gavin J Stark 2020
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#a Imports
from typing import Optional

#a Useful functions
def int_of_bits(bits):
    l = len(bits)
    m = 1<<(l-1)
    v = 0
    for b in bits:
        v = (v>>1) | (m*b)
        pass
    return v

def bits_of_n(nbits, n):
    bits = []
    for i in range(nbits):
        bits.append(n&1)
        n >>= 1
        pass
    return bits
def poly_of_list(l):
    v = 0
    for b in l:
        v += 1<<b
        pass
    return v

#a Lfsr base class
class Lfsr(object):
    init  : int = 0 # initial value
    poly  : int = 0x04C11DB7
    nbits : int = 32
    validated : bool = True
    def __init__(self, value:Optional[int]=None, nbits:Optional[int]=None, poly:Optional[int]=None):
        if nbits is not None:
            self.nbits = nbits
            pass
        if poly is not None:
            self.poly = poly
            pass
        assert self.poly is not None
        assert self.nbits is not None
        self.mask=(1<<self.nbits)-1
        assert (self.poly & self.mask)==self.poly
        self.poly = self.poly | (1<<self.nbits)
        if not self.validated:
            print("Validating",self.__class__.__name__)
            l=self.find_length()
            if (l+1)!=(1<<self.nbits): print("Not maximal",self.__class__.__name__)
            pass
        if value is not None:
            self.value = value
            pass
        else:
            self.value = self.init
            pass
        pass
    def set(self, v):
        self.value = v
    def get(self, mask=None):
        if mask is not None: return self.value & mask
        return self.value
    def clk_once(self):
        self.value = self.value<<1
        if (self.value>>self.nbits):
            self.value = self.value ^ self.poly
            pass
        pass
    def clk(self,n):
        for i in range(n):
            self.clk_once()
            pass
        pass
    def bit_reverse(self):
        x = bits_of_n(self.nbits, self.value)
        x.reverse()
        return int_of_bits(x)
    def find_length(self):
        remainders = {}
        remainders[0] = 0
        remainders[1] = self.poly & self.mask
        bits_per_tick = 14
        if (self.nbits<bits_per_tick): bits_per_tick=self.nbits-1
        p = self.poly
        for i in range(1<<bits_per_tick):
            if i in remainders:
                p = remainders[i]
                continue
            p = remainders[i // 2]<<1
            if (p>>self.nbits): p = p ^ self.poly
            if (i&1): p = (p ^ self.poly) & self.mask
            remainders[i] = p
            pass
        # for (k,v) in remainders.items():print(k,v,self.mask)
        p = 1
        n = 0
        for i in range(((1<<self.nbits)-bits_per_tick) // bits_per_tick):
            p = p<<bits_per_tick
            p = (p ^ remainders[p>>self.nbits]) & self.mask
            n += bits_per_tick
            pass
        self.value = p
        while self.value!=1:
            self.clk_once()
            n+=1
            if n>(1<<self.nbits): break
            pass
        return n
    def __str__(self, msb_first=True):
        r = ""
        br = range(0,self.nbits)
        if msb_first: br = range(self.nbits-1,-1,-1)
        for i in br:
            r+="%d"%((self.value>>i)&1)
            pass
        return r
    pass

#a Maximal length LFSRs
# Each is presented as max_lfsr_N
# There may be a max_lfsr_N_2 which is a 2-tap LFSR (top tap is N)
# There will be a max_lfsr_N_4 which is a 4-tap LFSR (top tap is N)
# max_lfsr_N will be max_lfsr_N_2 if it exists, else max_lfsr_N_4
# data taken from http://courses.cse.tamu.edu/csce680/walker/lfsr_table.pdf

#c Lfsr 2
class MaxLfsr_2(Lfsr):
    nbits = 2
    poly  = poly_of_list([1,0])
    pass

#c Lfsr 3
class MaxLfsr_3(Lfsr):
    nbits = 3
    poly  = poly_of_list([2,0])
    pass

#c Lfsr 4
class MaxLfsr_4(Lfsr):
    nbits = 4
    poly  = poly_of_list([3,0]) # 4,3
    pass

#c Lfsr 5
class MaxLfsr_5_2(Lfsr):
    nbits = 5
    poly  = poly_of_list([3,0]) # 5,3
    pass

class MaxLfsr_5_4(Lfsr):
    nbits = 5
    poly  = poly_of_list([4,3,2,0]) # 5,4,3,2
    pass
class MaxLfsr_5(MaxLfsr_5_2): pass

#c Lfsr 6
class MaxLfsr_6_2(Lfsr):
    nbits = 6
    poly  = poly_of_list([5,0])
    pass

class MaxLfsr_6_4(Lfsr):
    nbits = 6
    poly  = poly_of_list([5,3,2,0])
    pass
class MaxLfsr_6(MaxLfsr_6_2): pass

#c Lfsr 7
class MaxLfsr_7_2(Lfsr):
    nbits = 7
    poly  = poly_of_list([6,0])
    pass

class MaxLfsr_7_4(Lfsr):
    nbits = 7
    poly  = poly_of_list([6,5,4,0])
    pass
class MaxLfsr_7(MaxLfsr_7_2): pass

#c Lfsr 8
class MaxLfsr_8_4(Lfsr):
    nbits = 8
    poly  = poly_of_list([6,5,4,0])
    pass
class MaxLfsr_8(MaxLfsr_8_4): pass

#c Lfsr 9
class MaxLfsr_9_2(Lfsr):
    nbits = 9
    poly  = poly_of_list([5,0])
    pass

class MaxLfsr_9_4(Lfsr):
    nbits = 9
    poly  = poly_of_list([8,6,5,0])
    pass
class MaxLfsr_9(MaxLfsr_9_2): pass

#c Lfsr 10
class MaxLfsr_10_2(Lfsr):
    nbits = 10
    poly  = poly_of_list([7,0])
    pass

class MaxLfsr_10_4(Lfsr):
    nbits = 10
    poly  = poly_of_list([9,7,6,0])
    pass
class MaxLfsr_10(MaxLfsr_10_2): pass

#c Lfsr 11
class MaxLfsr_11_2(Lfsr):
    nbits = 11
    poly  = poly_of_list([9,0])
    pass

class MaxLfsr_11_4(Lfsr):
    nbits = 11
    poly  = poly_of_list([10,9,7,0])
    pass
class MaxLfsr_11(MaxLfsr_11_2): pass

#c Lfsr 12
class MaxLfsr_12_4(Lfsr):
    nbits = 12
    poly  = poly_of_list([11,8,6,0])
    pass
class MaxLfsr_12(MaxLfsr_12_4): pass

#c Lfsr 13
class MaxLfsr_13_4(Lfsr):
    nbits = 13
    poly  = poly_of_list([12,10,9,0])
    pass
class MaxLfsr_13(MaxLfsr_13_4): pass

#c Lfsr 14
class MaxLfsr_14_4(Lfsr):
    nbits = 14
    poly  = poly_of_list([13,11,9,0])
    pass
class MaxLfsr_14(MaxLfsr_14_4): pass

#c Lfsr 15
class MaxLfsr_15_2(Lfsr):
    nbits = 15
    poly  = poly_of_list([14,0])
    pass

class MaxLfsr_15_4(Lfsr):
    nbits = 15
    poly  = poly_of_list([14,13,11,0])
    pass
class MaxLfsr_15(MaxLfsr_15_2): pass

#c Lfsr 16
class MaxLfsr_16_4(Lfsr):
    nbits = 16
    poly  = poly_of_list([14,13,11,0])
    pass
class MaxLfsr_16(MaxLfsr_16_4): pass

#c Lfsr 17
class MaxLfsr_17_2(Lfsr):
    nbits = 17
    poly  = poly_of_list([14,0])
    pass

class MaxLfsr_17_4(Lfsr):
    nbits = 17
    poly  = poly_of_list([16,15,14,0])
    pass
class MaxLfsr_17(MaxLfsr_17_2): pass

#c Lfsr 18
class MaxLfsr_18_2(Lfsr):
    nbits = 18
    poly  = poly_of_list([11,0])
    pass

class MaxLfsr_18_4(Lfsr):
    nbits = 18
    poly  = poly_of_list([17,16,13,0])
    pass
class MaxLfsr_18(MaxLfsr_18_2): pass

#c Lfsr 19
class MaxLfsr_19_4(Lfsr):
    nbits = 19
    poly  = poly_of_list([18,17,14,0])
    pass
class MaxLfsr_19(MaxLfsr_19_4): pass

#c Lfsr 20
class MaxLfsr_20_2(Lfsr):
    nbits = 20
    poly  = poly_of_list([17,0])
    pass

class MaxLfsr_20_4(Lfsr):
    nbits = 20
    poly  = poly_of_list([19,16,14,0])
    pass
class MaxLfsr_20(MaxLfsr_20_2): pass

#c Lfsr 21
class MaxLfsr_21_2(Lfsr):
    nbits = 21
    poly  = poly_of_list([19,0])
    pass

class MaxLfsr_21_4(Lfsr):
    nbits = 21
    poly  = poly_of_list([20,19,16,0])
    pass
class MaxLfsr_21(MaxLfsr_21_2): pass

#c Lfsr 22
class MaxLfsr_22_2(Lfsr):
    nbits = 22
    poly  = poly_of_list([21,0])
    pass

class MaxLfsr_22_4(Lfsr):
    nbits = 22
    poly  = poly_of_list([19,18,17,0])
    pass
class MaxLfsr_22(MaxLfsr_22_2): pass

#c Lfsr 23
class MaxLfsr_23_2(Lfsr):
    nbits = 23
    poly  = poly_of_list([18,0])
    pass

class MaxLfsr_23_4(Lfsr):
    nbits = 23
    poly  = poly_of_list([22,20,18,0])
    pass
class MaxLfsr_23(MaxLfsr_23_2): pass

#c Lfsr 24
class MaxLfsr_24_4(Lfsr):
    nbits = 24
    poly  = poly_of_list([23,21,20,0])
    pass
class MaxLfsr_24(MaxLfsr_24_4): pass

#c Lfsr 25
class MaxLfsr_25_2(Lfsr):
    nbits = 25
    poly  = poly_of_list([22,0])
    pass

class MaxLfsr_25_4(Lfsr):
    nbits = 25
    poly  = poly_of_list([24,23,22,0])
    pass
class MaxLfsr_25(MaxLfsr_25_2): pass

#c Lfsr 26
class MaxLfsr_26_4(Lfsr):
    nbits = 26
    poly  = poly_of_list([25,24,20,0])
    pass
class MaxLfsr_26(MaxLfsr_26_4): pass

#c Lfsr 27
class MaxLfsr_27_4(Lfsr):
    nbits = 27
    poly  = poly_of_list([26,25,22,0])
    pass
class MaxLfsr_27(MaxLfsr_27_4): pass

#c Lfsr 28
class MaxLfsr_28_2(Lfsr):
    nbits = 28
    poly  = poly_of_list([25,0])
    pass

class MaxLfsr_28_4(Lfsr):
    nbits = 28
    poly  = poly_of_list([27,24,22,0])
    pass
class MaxLfsr_28(MaxLfsr_28_2): pass

#c Lfsr 29
class MaxLfsr_29_2(Lfsr):
    nbits = 29
    poly  = poly_of_list([27,0])
    pass

class MaxLfsr_29_4(Lfsr):
    nbits = 29
    poly  = poly_of_list([28,27,25,0])
    pass
class MaxLfsr_29(MaxLfsr_29_2): pass

#c Lfsr 30
class MaxLfsr_30_4(Lfsr):
    nbits = 30
    poly  = poly_of_list([29,26,24,0])
    pass
class MaxLfsr_30(MaxLfsr_30_4): pass

#c Lfsr 31
class MaxLfsr_31_2(Lfsr):
    nbits = 31
    poly  = poly_of_list([28,0])
    pass

class MaxLfsr_31_4(Lfsr):
    nbits = 31
    poly  = poly_of_list([30,29,28,0])
    pass
class MaxLfsr_31(MaxLfsr_31_2): pass

#c Lfsr 32
class MaxLfsr_32_4(Lfsr):
    nbits = 32
    poly  = poly_of_list([30,26,25,0])
    pass
class MaxLfsr_32(MaxLfsr_32_4): pass

#c Lfsr 33
class MaxLfsr_33_2(Lfsr):
    nbits = 33
    poly  = poly_of_list([20,0])
    pass

class MaxLfsr_33_4(Lfsr):
    nbits = 33
    poly  = poly_of_list([32,29,27,0])
    pass
class MaxLfsr_33(MaxLfsr_33_2): pass

#c Lfsr 34
class MaxLfsr_34_4(Lfsr):
    nbits = 34
    poly  = poly_of_list([31,30,26,0])
    pass
class MaxLfsr_34(MaxLfsr_34_4): pass

#c Lfsr 35
class MaxLfsr_35_2(Lfsr):
    nbits = 35
    poly  = poly_of_list([33,0])
    validated = False
    pass

class MaxLfsr_35_4(Lfsr):
    nbits = 35
    poly  = poly_of_list([34,28,27,0])
    validated = False
    pass
class MaxLfsr_35(MaxLfsr_35_2): pass

#c Lfsr 36
class MaxLfsr_36_2(Lfsr):
    nbits = 36
    poly  = poly_of_list([25,0])
    validated = False
    pass

class MaxLfsr_36_4(Lfsr):
    nbits = 36
    poly  = poly_of_list([35, 29,28,0])
    validated = False
    pass
class MaxLfsr_36(MaxLfsr_36_2): pass

#c Lfsr 37
class MaxLfsr_37_4(Lfsr):
    nbits = 37
    poly  = poly_of_list([36,33,31,0])
    validated = False
    pass
class MaxLfsr_37(MaxLfsr_37_4): pass

#a Test
do_validation = False
for c in Lfsr.__subclasses__():
    if do_validation:
        x=c()
    pass
