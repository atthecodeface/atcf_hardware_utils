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

#a Structs
#t t_dprintf_byte
t_dprintf_byte = {"address":16,
                "data":8,
                "last":1,
                "valid":1,
}

#t t_dprintf_req_4
t_dprintf_req_4 = {
    "valid":1,
    "address":16,
    "data_0":64,
    "data_1":64,
    "data_2":64,
    "data_3":64,
    }

#t t_dprintf_req_2
t_dprintf_req_2 = {
    "valid":1,
    "address":16,
    "data_0":64,
    "data_1":64,
    }



#a Bus driver
class DprintfBus:
    def __init__(self, obj, req_name:str, ack_name:str, n=4):
        self.n = n
        self.valid = getattr(obj, req_name+"__valid")
        self.address = getattr(obj, req_name+"__address")
        self.data_0 = getattr(obj, req_name+"__data_0")
        self.data_1 = getattr(obj, req_name+"__data_1")
        if n>2:
            self.data_2 = getattr(obj, req_name+"__data_2")
            self.data_3 = getattr(obj, req_name+"__data_3")
            pass
        self.ack = getattr(obj, ack_name)
        pass
    def invalid(self):
        self.valid.drive(0)
        pass
    def drive(self, d):
        self.valid.drive(1)
        self.address.drive(d.address)
        n = len(d.data_list)
        if n > self.n: n = self.n
        if n > 0:
            self.data_0.drive(d.data_list[0])
            pass
        if n > 1:
            self.data_1.drive(d.data_list[1])
            pass
        if n > 2:
            self.data_2.drive(d.data_list[2])
            pass
        if n > 3:
            self.data_3.drive(d.data_list[3])
            pass
        pass
    def is_acked(self) -> bool:
        return self.ack.value() == 1
    pass

#a Constructor/Dprintf to byte
#c DprintfByte
class DprintfByte:
    address: int
    data: int
    last: bool
    valid : bool
    def __init__(self, address:int=0, data:int=0, last:bool=False, valid:bool=True):
        self.address = address
        self.data = data
        self.last = last
        self.valid = valid
        pass
    @classmethod
    def invalid(cls):
        return cls(valid=False)
    @classmethod
    def last(cls):
        return cls(last=True)
    pass

#c Dprintf
class Dprintf:
    address: int
    data: bytes
    output: bytes
    data_list: list[int]
    def __init__(self, address:int, data:bytes, data_ints:list[int]=[]):
        self.address = address
        self.data = bytearray(data)
        if len(data_ints)!=0:
            for d in data_ints:
                for i in range(8):
                    v = (d>>(56-8*i)) & 0xff
                    self.data.append(v)
                    pass
                pass
            pass
        self.data = bytes(self.data)
        self.generate_output()
        self.generate_list()
        pass
    def generate_list(self):
        self.data_list = []
        value = 0
        shift = 56
        for d in self.data:
            value |= d << shift
            if shift == 0:
                self.data_list.append(value)
                shift = 56
                pass
            else:
                shift = shift - 8
                pass
            pass
        while len(self.data_list)<4:
            self.data_list.append(value)
            value = 0
            pass
        pass
    def as_dprintf_bytes(self) -> list[DprintfByte]:
        result = []
        addr = self.address
        for b in output:
            result.append(DprintfByte(address, b))
            address += 1
            pass
        result.append(DprintfByte.last())
        return result
    def generate_output(self):
        hex = b"0123456789ABCDEF"
        self.output = bytearray()
        data_len = len(self.data)
        n = 0
        while n < data_len:
            c = self.data[n]
            if c==0:
                n += 1
                pass
            elif c<128:
                self.output.append(c)
                n += 1
                pass
            elif c<0x90:
                nybbles = (c & 0xf)+1
                num_data_bytes = (nybbles + 1) // 2
                # assert(n+1+num_data_bytes < data_len)
                for i in range(num_data_bytes):
                    if n+1+i < data_len:
                        v = self.data[n+1+i]
                        pass
                    else:
                        v = 255
                        pass
                    if i>0 or (nybbles%2)==0:
                        self.output.append(hex[(v >> 4) & 0xf])
                        pass
                    self.output.append(hex[v & 0xf])
                    pass
                n += 1+num_data_bytes
                pass
            elif c<255:
                num_data_bytes = ((c&3)+ 1)
                pad_to = (c>>2) & 15
                # assert(n+1+num_data_bytes < data_len)
                assert(pad_to<10)
                value = 0
                for i in range(num_data_bytes):
                    if n+1+i < data_len:
                        v = self.data[n+1+i]
                        pass
                    else:
                        v = 255
                        pass
                    value = value*256 + v
                    pass
                s = str(value)
                if pad_to >= 1:
                    for i in range(pad_to+1-len(s)):
                        self.output.append(32)
                        pass
                    pass
                self.output += s.encode()
                n += 1+num_data_bytes
                pass
            else:
                break
            pass
        pass
    pass
