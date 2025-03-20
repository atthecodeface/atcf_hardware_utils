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
from random import Random
from queue import Queue
from regress.utils import t_dprintf_req_4, t_dprintf_byte, Dprintf, t_dbg_master_request, t_dbg_master_response, DprintfBus, SramAccessBus, SramAccessRead, SramAccessWrite, DbgMaster, DbgMasterMuxScript, DbgMasterSramScript, DbgMasterFifoScript, FifoStatus, t_sram_access_req, t_sram_access_resp
from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c FifoScript
class FifoScript(DbgMasterMuxScript):
    select = 1
    def __init__(self, *args, **kwargs):
        subscript = DbgMasterFifoScript(*args, **kwargs)
        super().__init__(select=self.select, clear=False, subscript=subscript)
        pass
    pass

#c SramScript
class SramScript(DbgMasterMuxScript):
    select = 2
    def __init__(self, *args, **kwargs):
        subscript = DbgMasterSramScript(*args, **kwargs)
        super().__init__(select=self.select, clear=False, subscript=subscript)
        pass
    pass

#c DprintfTest_Base
class DprintfTest_Base(ThExecFile):
    th_name = "Utils dprintf test harness"
    sram_inter_delay = 0
    random_seed = "bananas"
    pop_rdy_pct = 30
    dv_pct = 30
    # This can be set at initialization time to reduce the number of explicit test cases
    def __init__(self, **kwargs) -> None:
        super(DprintfTest_Base,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(DprintfTest_Base,self).exec_init()
        pass

    #f bfm_wait_toggling_rdy_dv
    def bfm_wait_toggling_rdy_dv(self, n):
        for i in range(n):
            
            pop_rdy = int(self.random_holdoffs.randrange(100) <= self.pop_rdy_pct)
            dv = int(self.random_holdoffs.randrange(100) <= self.dv_pct)
            self.dbg_pop_rdy.drive(pop_rdy)
            self.dprintf_fifo_out_data_valid.drive(dv)
            self.bfm_wait(1)
            pass
        pass

    #f drive_dprintf_req
    def drive_dprintf_req(self, d):
        self.dprintf.drive(d)
        self.bfm_wait_toggling_rdy_dv(1)
        while not self.dprintf.is_acked():
            self.bfm_wait_toggling_rdy_dv(1)
            pass
        self.dprintf.invalid()
        pass

    #f perform_sram_req
    def perform_sram_req(self, s):
        self.sram_access.drive(s)
        self.bfm_wait_toggling_rdy_dv(1)
        while not self.sram_access.is_acked():
            self.bfm_wait_toggling_rdy_dv(1)
            pass
        self.sram_access.invalid()
        if self.sram_inter_delay>0:
            self.bfm_wait_toggling_rdy_dv(self.sram_inter_delay)
            pass
        pass
            
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(1)
        self.random_holdoffs = Random()
        self.random_holdoffs.seed(self.random_seed)

        self.verbose.set_level(self.verbose.level_info)
        self.verbose.message(f"Test {self.__class__.__name__}")

        self.dbg_pop_rdy.drive(1)
        self.dprintf_fifo_out_data_valid.drive(1)
        self.bfm_wait(10)
        self.dprintf = DprintfBus(self, "dprintf_req", "dprintf_ack", n=4)
        self.dbg_master = DbgMaster(self, "dbg_master_req", "dbg_master_resp")
        self.sram_access = SramAccessBus(self, "sram_access_req", "sram_access_resp")
        pass
    #f run
    def run(self) -> None:
        self.bfm_wait(4)
        self.die_event.reset()
        self.dprintf.invalid()
        self.bfm_wait(4)
        script_num = 1
        for (reason,srams,data,script,exp_c,exp_d) in self.data_and_scripts_to_run:
            self.verbose.warning(reason)
            for s in srams:
                self.perform_sram_req(s)
                pass
            for d in data:
                self.drive_dprintf_req(d)
                pass
            (completion, res_data) = self.dbg_master.invoke_script_bytes(
                script.as_bytes(),
                self.bfm_wait_toggling_rdy_dv,
                lambda :0,
                1000)
            self.compare_expected(f"Completion of script {script_num}", exp_c, completion)
            self.compare_expected_list(f"Data of script {script_num}", exp_d, res_data)
            self.bfm_wait(4)
            script_num += 1
            pass
        self.bfm_wait_until_test_done(100)
        self.die_event.fire()
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.passtest("Test completed")
        pass
    pass

#c DprintfTest_0
class DprintfTest_0(DprintfTest_Base):
    data_and_scripts_to_run = [
       ("Dprintf 16 characters, read FIFO status and check it has 515 slots with 1 full",
        [],
        [ Dprintf(0x0, b"abcdefghijklmnop"),
         ],
        FifoScript(["status"]),
        "ok",
        [FifoStatus(515,1).as_dbg_master_fifo_status(),
         ]
        ),
       ("Dprintf 16 characters, read FIFO status (four times) and check it has 515 slots with 2 full",
        [],
        [Dprintf(0x0, b"abcdefghijklmnop"),
         ],
        FifoScript(["status","status","status","status"]),
        "ok",
        [FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         ]
        ),
       ("Read one entry of 64 bits of FIFO data (abcdefgh) and then check status has 515 slots with 1 full",
        [],
        [],
        FifoScript([("read",64,1), "status"]),
        "ok",
        [0x65666768, 0x61626364,
         FifoStatus(515,1).as_dbg_master_fifo_status(),
         ]
        ),
       ("Read two entries of 64 bits of FIFO data (abcdefgh), only one of which is present",
        [],
        [],
        FifoScript([("read",64,2), "status"]),
        "ok",
        [0x65666768, 0x61626364,
         ]
        ),
       ("Read two entries of 64 bits of FIFO data (abcdefgh), none of which are present",
        [],
        [],
        FifoScript([("read",64,2), "status"]),
        "ok",
        [
         ]
        ),
       ("Read with error if not ready two entries of 64 bits of FIFO data (abcdefgh), none of which are present",
        [],
        [],
        FifoScript([("read_err",64,2), "status"]),
        "poll_failed",
        [
         ]
        ),
        ]
    pass

#c DprintfTest_1
class DprintfTest_1(DprintfTest_Base):
    random_seed = "toaa1231sdst"
    data_and_scripts_to_run = [
       ("Dprintf 10 times then read FIFO status of 515 slots and 10 full",
        [],
        [ Dprintf(0x0, b"abcdefg1andmore"),
          Dprintf(0x0, b"abcdefg2andmore"),
          Dprintf(0x0, b"abcde3g3andmore"),
          Dprintf(0x0, b"abcde4g4andmore"),
          Dprintf(0x0, b"abc5efg5andmore"),
          Dprintf(0x0, b"abc6efg6andmore"),
          Dprintf(0x0, b"a7cdefg7andmore"),
          Dprintf(0x0, b"a8cdefg8andmore"),
          Dprintf(0x0, b"abcdefg9andmore"),
          Dprintf(0x0, b"abcdefg0andmore"),
         ],
        FifoScript(["status"]),
        "ok",
        [FifoStatus(515,10).as_dbg_master_fifo_status(),
         ]
        ),
       ("Read FIFO data 1 byte, 2 bytes, 3 bytes, then 4 bytes, then status of 515 slots and 6 full",
        [],
        [],
        FifoScript([("read",8,1),
                             ("read",16,1),
                             ("read",24,1),
                             ("read",32,1),
                             "status"]),
        "ok",
        [0x31, 0x6732, 0x336733, 0x65346734,
         FifoStatus(515,6).as_dbg_master_fifo_status(),
         ]
        ),
       ("Read FIFO data 5 bytes, 6 bytes, 7 bytes, then 8 bytes, then status of 515 slots and 2 full",
        [],
        [],
        FifoScript([("read",40,1),
                             ("read",48,1),
                             ("read",56,1),
                             ("read",64,1),
                             "status"]),
        "ok",
        [0x65666735, 0x35,
         0x65666736, 0x6336,
         0x65666737, 0x376364,
         0x65666738, 0x61386364,
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         ]
        ),
        ]
    pass

#c SramTest_0
class SramTest_0(DprintfTest_Base):
    # Provide a delay between SRAM writes to allow dprintf's to occur
    sram_inter_delay = 2
    data_and_scripts_to_run = [
       ("Write SRAM[0] with 0x12345678, then read SRAM 1 entry, four times, one as 32-bit, then 24-bit, then 16-bit, then 8-bit",
        [SramAccessWrite(0,0,0x12345678,0xffff)],
        [],
        SramScript([("read",32,0,1),
                    ("read",24,0,1),
                    ("read",16,0,1),
                    ("read",8,0,1),
                    ]),
        "ok",
        [0x12345678, 0x345678, 0x5678, 0x78
         ]
        ),
       ("Write SRAM[1-8] with 16-bits of known data, then read 9 SRAM entries, four times, first as 32-bit, then 24-bit, then 16-bit, then 8-bit",
        [SramAccessWrite(0,d,d*0x01020201,0xffff) for d in [1,2,3,4,5,6,7,8]],
        [],
        SramScript([("read",32,0,9),
                    ("read",24,0,9),
                    ("read",16,0,9),
                    ("read",8,0,9),
                    ]),
        "ok",
        [0x12345678, 0x1020201, 0x2040402, 0x3060603, 0x4080804, 0x50a0a05, 0x60c0c06, 0x70e0e07, 0x8101008,
         0x345678,  0x020201, 0x040402, 0x060603, 0x080804, 0x0a0a05, 0x0c0c06, 0x0e0e07, 0x101008,
         0x5678,  0x0201, 0x0402, 0x0603, 0x0804, 0x0a05, 0x0c06, 0x0e07, 0x1008,
         0x78, 1,2,3,4,5,6,7,8,
         ]
        ),
       ("Read FIFO status of 515 slots with 5+8+9*4 entries as each SRAM access does a 'dprintf' which goes into the dprintf FIFO",
        [],
        [],
        FifoScript(["status"]),
        "ok",
        [FifoStatus(515,5+8+9*4).as_dbg_master_fifo_status(),
         ]
        ),
        ]
    pass

#a Hardware and test instantiation
#c DbgDprintfHardware
class DbgDprintfHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "tb_dbg_dprintf_fifo"
    dut_inputs  = {"dprintf_req":t_dprintf_req_4,
                   "dbg_master_req":t_dbg_master_request,
                   "sram_access_req":t_sram_access_req,
                   "dbg_pop_rdy":1,
                   "dprintf_fifo_out_data_valid":1,
    }
    dut_outputs = {"dprintf_ack":1,
                   "dbg_master_resp":t_dbg_master_response,
                   "sram_access_resp":t_sram_access_resp,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestDbgDprintf
class TestDbgDprintf(TestCase):
    hw = DbgDprintfHardware
    _tests = {"0": (DprintfTest_0, 2*1000, {}),
              "1": (DprintfTest_1, 2*1000, {}),
              "smoke": (DprintfTest_0, 2*1000, {}),
    }

