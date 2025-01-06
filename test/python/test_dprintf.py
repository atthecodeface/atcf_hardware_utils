#a Copyright
#  
#  This file 'test_dprintf.py' copyright Gavin J Stark 2017-2020
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
from queue import Queue
from regress.utils import t_dprintf_req_4, t_dprintf_byte, Dprintf
from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c DprintfTest_Base
class DprintfTest_Base(ThExecFile):
    th_name = "Utils dprintf test harness"
    # cfg_test_ctl = 0 for direct connection, 1 for sync fifo size 4, 2 for 2 async FIFOs size 8
    # This can be set at initialization time to reduce the number of explicit test cases
    cfg_test_ctl=0
    def __init__(self, test_ctl=None, **kwargs) -> None:
        if test_ctl is not None: self.cfg_test_ctl = test_ctl
        super(DprintfTest_Base,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(DprintfTest_Base,self).exec_init()
        pass
    #f drive_dprintf_req
    def drive_dprintf_req(self, address, data):
        self.dprintf_req__valid.drive(1)
        self.dprintf_req__address.drive(address)
        self.dprintf_req__data_0.drive(data[0])
        self.dprintf_req__data_1.drive(data[1])
        self.dprintf_req__data_2.drive(data[2])
        self.dprintf_req__data_3.drive(data[3])

        self.bfm_wait(1)
        self.dprintf_ack.wait_for_value(1)
        self.dprintf_req__valid.drive(0)
        self.bfm_wait(1)
        pass
            
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        self.bfm_wait(4)
        self.die_event.reset()
        self.test_ctl.drive(self.cfg_test_ctl)
        self.string_results = Queue()
        self.spawn(self.checker)
        self.bfm_wait(4)
        for (address, data, result) in self.data_to_test:
            og = Dprintf(address, bytes(), data).output
            assert(og == result.encode())
            self.verbose.warning("dprintf %04x: %08x %08x %08x %08x expect '%s'"%(address,data[0],data[1],data[2],data[3],result))
            self.string_results.put((address,result))
            self.drive_dprintf_req(address=address, data=data)
            pass
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f checker
    def checker(self):
        address = 0
        byte = 0
        completed = False
        expected_string = None
        while not self.die_event.fired():
            self.dprintf_byte__valid.wait_for_value(1,50)
            # self.verbose.message("Byte %d %d %d"%(self.dprintf_byte__valid.value(),self.dprintf_byte__last.value(),self.dprintf_byte__data.value()))
            if self.dprintf_byte__valid.value()!=1:
                continue
            if self.dprintf_byte__last.value():
                if expected_string is not None:
                    self.failtest("Not enough dprintf data received; still had '%s' at %04x"%(expected_string, expected_address))
                    completed = True
                    pass
                else:
                    if self.string_results.empty():
                        completed = True
                        pass
                    pass
                pass
            else:
                address = self.dprintf_byte__address.value()
                byte    = self.dprintf_byte__data.value()
                if expected_string is None:
                    if self.string_results.empty():
                        self.failtest("More dprintf data received than expected")
                        complete = True
                        pass
                    else:
                        (expected_address, expected_string) = self.string_results.get()
                        pass
                    pass
                if expected_string is not None:
                    self.compare_expected("Byte dprintfed at address %04x"%(expected_address),ord(expected_string[0]),byte)
                    self.compare_expected("Address dprintfed",expected_address,address)
                    expected_address = expected_address+1
                    expected_string=expected_string[1:]
                    if expected_string=="": expected_string=None
                    pass
                pass
            if completed: break
            self.bfm_wait(1)
            pass
        self.compare_expected("Completed checking",completed,True)
        # self.verbose.error("%d"%self.global_cycle())
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        # self.verbose.error("%d"%self.global_cycle())
        self.passtest("Test completed")
        pass
    pass

#c DprintfTest_0
class DprintfTest_0(DprintfTest_Base):
    data_to_test = [ (  0x0,  (0x6162636465666768, 0x696a6b6c6d6e6f70, 0x4142434445464748, 0x494a4b4c4d4e4f50 ), "abcdefghijklmnopABCDEFGHIJKLMNOP"),
    ]
    pass
#c DprintfTest_1
class DprintfTest_1(DprintfTest_Base):
    data_to_test = [ (  0x30, (0x85012345, 0xc11a85,0,0), "0123456789"),
                     ( 0x541, (0x85abcdef, 0x4700480049004a, 0x4b004c004d004e, 0x4f), "ABCDEFGHIJKLMNO"),
                     (0xff41, (0x41ff, 0,0,0), "A"),
    ]
    pass
#c DprintfTest_Hex
class DprintfTest_Hex(DprintfTest_Base):
    data_to_test = [ (  0x30, (0x80ff81ee82dddd83, 0xcccc84bbbbbb85aa, 0xaaaa869999999987,0x8888888800ff0000), "FEEDDDCCCCBBBBBAAAAAA999999988888888"),
                     (  0x30, (0x88, 0x0123456789000000, 0x89, 0x0123456789000000), "1234567890123456789"),
                     (  0x30, (0x8a, 0x0123456789AB0000, 0x8b, 0x0123456789AB0000), "123456789AB0123456789AB"),
                     (  0x30, (0x8c, 0x0123456789ABCD00, 0x8d, 0x0123456789ABCD00), "123456789ABCD0123456789ABCD"),
                     (  0x30, (0x8e, 0x0123456789ABCDEF, 0x8f, 0x0123456789ABCDEF), "123456789ABCDEF0123456789ABCDEF"),
                     (  0x30, (0x8e, 0, 0x8f, 0), "0000000000000000000000000000000"),
    ]
#c DprintfTest_Small
class DprintfTest_Small(DprintfTest_Base):
    data_to_test = [ (0x1, (0,0,0,0x41),"A") ] * 30
    pass
#c DprintfTest_DecimalUnpadded
class DprintfTest_DecimalUnpadded(DprintfTest_Base):
    data_to_test = [ (  0x000, (0xc000c001c00ac064, 0xc0ffff0000000000,0,0), "0110100255"),
                     (  0x040, (0xc10000c10002c100, 0x14c100c8c107d0c1, 0x4e20c1ffffff0000,0), "022020020002000065535"),
                     (  0x080, (0xc2000000c2000003, 0xc200001ec200012c, 0xc2000bb8c2007530, 0xc20493e0c22dc6c0), "03303003000300003000003000000"),
                     (  0x100, (0xc300000000000000, 0xc300000004,
                               0xc300000028, 0xc300000190,), "0440400"),
                     (  0x200, (0xc300000fa0, 0xc300009c40,
                               0xc300061a80, 0xc3003d0900,), "4000400004000004000000"),
                     (  0x300, (0xc302625a00, 0xc317d78400,
                               0xc3ee6b2800, 0xc3ffffffff,), "4000000040000000040000000004294967295"),
    ]
#c DprintfTest_DecimalPadded
class DprintfTest_DecimalPadded(DprintfTest_Base):
    data_to_test = [ (  0x000, (0xc400c401c40ac464, 0xc4ffff0000000000,0,0), " 0 110100255"),
                     (  0x040, (0xc90000c90002c900, 0x14c900c8c907d0c9, 0x4e20c9ffffff0000,0), "  0  2 2020020002000065535"),
                     (  0x080, (0xce000000ce000003, 0xce00001ece00012c, 0xce000bb8ce007530, 0xce0493e0ce2dc6c0), "   0   3  30 3003000300003000003000000"),
                     (  0x100, (0xd300000000000000, 0xd300000004,
                               0xd300000028, 0xd300000190,), "    0    4   40  400"),
                     (  0x200, (0xd700000fa0, 0xdb00009c40,
                                0xdf00061a80, 0xe3003d0900,), "  4000  40000  400000  4000000"),
                     (  0x300, (0xe302625a00, 0xe717d78400,
                                0xe7ee6b2800, 0xe7ffffffff,), " 40000000 40000000040000000004294967295"),
    ]

#a Hardware and test instantiation
#c DprintfHardware
class DprintfHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
                  ("clk_async",(0,17,10)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_dprintf"
    dut_inputs  = {"dprintf_req":t_dprintf_req_4,
                   "test_ctl":4,
    }
    dut_outputs = {"dprintf_ack":1,
                   "dprintf_byte":t_dprintf_byte,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestDprintf
class TestDprintf(TestCase):
    hw = DprintfHardware
    _tests = {"0_a": (DprintfTest_0, 1*1000,   {"th_args":{"test_ctl":0}}),
              "0_b": (DprintfTest_0, 1*1000,   {"th_args":{"test_ctl":1}}),
              "0_c": (DprintfTest_0, 1*1000,   {"th_args":{"test_ctl":2}}),
              "1_a": (DprintfTest_1, 1*1000,   {"th_args":{"test_ctl":0}}),
              "1_b": (DprintfTest_1, 1*1000,   {"th_args":{"test_ctl":1}}),
              "1_c": (DprintfTest_1, 1*2000,   {"th_args":{"test_ctl":2}}),
              "smoke": (DprintfTest_1, 1*2000,   {"th_args":{"test_ctl":2}}),
              "hex_0": (DprintfTest_Hex, 1*3000,   {"th_args":{"test_ctl":0}}),
              "hex_1": (DprintfTest_Hex, 1*3000,   {"th_args":{"test_ctl":1}}),
              "hex_2": (DprintfTest_Hex, 1*3000,   {"th_args":{"test_ctl":2}}),
              "decu_0": (DprintfTest_DecimalUnpadded, 1*4000,   {"th_args":{"test_ctl":0}}),
              "decu_1": (DprintfTest_DecimalUnpadded, 1*4000,   {"th_args":{"test_ctl":1}}),
              "decu_2": (DprintfTest_DecimalUnpadded, 1*4000,   {"th_args":{"test_ctl":2}}),
              "decp_0": (DprintfTest_DecimalPadded,   1*6000,   {"th_args":{"test_ctl":0}}),
              "decp_1": (DprintfTest_DecimalPadded,   1*6000,   {"th_args":{"test_ctl":1}}),
              "decp_2": (DprintfTest_DecimalPadded,   1*6000,   {"th_args":{"test_ctl":2}}),
              "small_0": (DprintfTest_Small, 1*5000,   {"th_args":{"test_ctl":0}}),
              "small_1": (DprintfTest_Small, 1*5000,   {"th_args":{"test_ctl":1}}),
              "small_2": (DprintfTest_Small, 1*5000,   {"th_args":{"test_ctl":2}}),
    }

