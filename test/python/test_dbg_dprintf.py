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
from regress.utils import t_dprintf_req_4, t_dprintf_byte, Dprintf, t_dbg_master_request, t_dbg_master_response, DprintfBus, DbgMaster, DbgMasterFifoScript, FifoStatus
from cdl.utils   import csr
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c DprintfTest_Base
class DprintfTest_Base(ThExecFile):
    th_name = "Utils dprintf test harness"
    # This can be set at initialization time to reduce the number of explicit test cases
    def __init__(self, **kwargs) -> None:
        super(DprintfTest_Base,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(DprintfTest_Base,self).exec_init()
        pass

    #f drive_dprintf_req
    def drive_dprintf_req(self, d):
        self.dprintf.drive(d)
        self.bfm_wait(1)
        while not self.dprintf.is_acked():
            self.bfm_wait(1)
            pass
        self.dprintf.invalid()
        pass
            
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(10)
        self.dprintf = DprintfBus(self, "dprintf_req", "dprintf_ack", n=4)
        self.dbg_master = DbgMaster(self, "dbg_master_req", "dbg_master_resp")
        pass
    #f run
    def run(self) -> None:
        self.bfm_wait(4)
        self.die_event.reset()
        self.dprintf.invalid()
        self.bfm_wait(4)
        script_num = 1
        for (data,script,exp_c,exp_d) in self.data_and_scripts_to_run:
            for d in data:
                self.drive_dprintf_req(d)
                pass
            (completion, res_data) = self.dbg_master.invoke_script_bytes(
                script.as_bytes(),
                self.bfm_wait,
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
       ([ Dprintf(0x0, b"abcdefghijklmnop"),
         ],
        DbgMasterFifoScript(["status"]),
        "ok",
        [FifoStatus(515,1).as_dbg_master_fifo_status(),
         ]
        ),
       ([Dprintf(0x0, b"abcdefghijklmnop"),
         ],
        DbgMasterFifoScript(["status","status","status","status"]),
        "ok",
        [FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         FifoStatus(515,2).as_dbg_master_fifo_status(),
         ]
        ),
       ([],
        DbgMasterFifoScript([("read",64,1), "status"]),
        "ok",
        [0x65666768, 0x61626364,
         FifoStatus(515,1).as_dbg_master_fifo_status(),
         ]
        ),
       ([],
        DbgMasterFifoScript([("read",64,2), "status"]),
        "ok",
        [0x65666768, 0x61626364,
         ]
        ),
       ([],
        DbgMasterFifoScript([("read",64,2), "status"]),
        "ok",
        [
         ]
        ),
       ([],
        DbgMasterFifoScript([("read_err",64,2), "status"]),
        "poll_failed",
        [
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
    }
    dut_outputs = {"dprintf_ack":1,
                   "dbg_master_resp":t_dbg_master_response,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestDbgDprintf
class TestDbgDprintf(TestCase):
    hw = DbgDprintfHardware
    _tests = {"0_a": (DprintfTest_0, 1*1000, {}),
              "smoke": (DprintfTest_0, 1*1000, {}),
    }

