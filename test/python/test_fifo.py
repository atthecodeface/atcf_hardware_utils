#a Copyright
#  
#  This file 'test_fifo.py' copyright Gavin J Stark 2017-2020
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
from random import Random
from regress.utils  import t_dprintf_req_2, t_dprintf_req_4
from regress.utils  import t_fifo_status
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c FifoData_Base
class FifoData_Base(object):
    data_mask = 0xffff
    def __init__(self, th):
        self.th         = th
    #f will_take_push
    def will_take_push(self) -> bool:
        return self.can_push.value()==1
    #f has_valid_data
    def has_valid_data(self) -> bool:
        return self.can_pop.value()==1
    #f validate_data
    def validate_data(self, data) -> None:
        a = self.pop_data.value()
        self.th.compare_expected("Data out of FIFO matches data in",a,data)
        pass
    #f generate_push
    def generate_push(self, do_push) -> int:
        self.push.drive(0)
        if not do_push: return None
        data = self.th.global_cycle()&self.data_mask
        self.push.drive(1)
        self.push_data.drive(data)
        return data
    #f generate_pop
    def generate_pop(self, do_pop) -> None:
        self.pop.drive(int(do_pop))
        pass
    pass
class FifoData_Dprintf(FifoData_Base):
    def __init__(self, th):
        super(FifoData_Dprintf,self).__init__(th)
        self.can_push   = th.ack_in
        self.can_pop    = th.req_out__valid
        self.push       = th.req_in__valid
        self.push_data  = th.req_in__address
        self.pop        = th.ack_out
        self.pop_data   = th.req_out__address
        pass
    pass
#c FifoTest_Base
class FifoTest_Base(ThExecFile):
    th_name = "Utils FIFO test harness"
    fifo_data = FifoData_Dprintf
    fifo_size = 4
    push_random_seed = "push_random_seed"
    pop_random_seed = "pop_random_seed"
    test_stages = [(10,  0.8, 0.1), # Fill it up
                       (300, 0.6, 0.6), # Consume stuff
                       (30,  0.1, 1.0), # Empty
                       ]
    def __init__(self, fifo_size=None, **kwargs) -> None:
        if fifo_size is not None: self.fifo_size=fifo_size
        super(FifoTest_Base,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        super(FifoTest_Base,self).exec_init()
        pass
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(10)
        pass
    #f fifo_accounting_tick
    def fifo_accounting_tick(self) -> None:
        self.will_push = 0
        self.will_pop = 0
        if self.data.will_take_push() and self.data_being_pushed is not None:
            self.queue.put(self.data_being_pushed)
            self.will_push = 1
            pass
        if self.data.has_valid_data() and self.data_being_popped:
            if self.queue.empty():
                self.failtest("Queue was empty when FIFO was presenting data")
                pass
            else:
                self.will_pop = 1
                self.data.validate_data(self.queue.get())
                pass
            pass
        self.compare_expected("Popped",self.fifo_status__popped.value(), self.last_data_being_popped)
        self.compare_expected("Pushed",self.fifo_status__pushed.value(), self.last_data_being_pushed)
        self.last_data_being_pushed = self.will_push
        self.last_data_being_popped = self.will_pop
        self.bfm_wait(1)
        self.compare_expected("Fifo entries",self.fifo_status__entries_full.value(), self.queue.qsize())
        self.compare_expected("Fifo space",self.fifo_status__spaces_available.value(), self.fifo_size-self.queue.qsize())
        self.compare_expected("Fifo full",self.fifo_status__full.value(), int(self.queue.qsize()==self.fifo_size))
        self.data_being_pushed = self.next_data_being_pushed
        self.data_being_popped = self.next_data_being_popped
        self.next_data_being_pushed = None
        self.next_data_being_popped = False
        pass
    #f generate_fifo_input
    def generate_fifo_input(self, push_chance, pop_chance) -> None:
        do_pop  = self.pop_random.random()<pop_chance
        do_push = self.push_random.random()<push_chance
        self.data.generate_pop(do_pop)
        self.next_data_being_pushed = self.data.generate_push(do_push)
        self.next_data_being_popped = do_pop
        pass
    #f run
    def run(self) -> None:
        self.queue = Queue()
        self.data = self.fifo_data(self)
        self.push_random = Random()
        self.pop_random = Random()
        self.push_random.seed(self.push_random_seed)
        self.pop_random.seed(self.pop_random_seed)
        self.last_data_being_pushed = 0
        self.last_data_being_popped = 0
        self.data_being_pushed = None
        self.data_being_popped = False
        self.next_data_being_pushed = None
        self.next_data_being_popped = False
        for (length, push_chance, pop_chance) in self.test_stages:
            for i in range(length):
                self.generate_fifo_input(push_chance,pop_chance)
                self.fifo_accounting_tick()
                pass
            pass
        self.bfm_wait(10)
        self.compare_expected("Fifo has not underflowed", self.fifo_status__underflowed.value(), 0)
        self.compare_expected("Fifo has not overflowed", self.fifo_status__overflowed.value(), 0)
        self.compare_expected("Queue empty at end of test", self.queue.empty(), True)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.verbose.error("%d"%self.global_cycle())
        self.passtest("Test completed")
        pass
    pass

#c FifoTest_0
class FifoTest_0(FifoTest_Base):
    """
    For 4-entry FIFOs this gets it full and empty a bit
    """
    push_random_seed = "push_random_seed"
    pop_random_seed = "pop_random_seed"
    test_stages = [(10,  0.8, 0.1), # Fill it up
                       (300, 0.6, 0.6), # Consume stuff
                       (30,  0.1, 1.0), # Empty
                       (30,  0, 1.0), # Empty
                       ]
    pass

#c FifoTest_1
class FifoTest_1(FifoTest_Base):
    """
    For 4-entry FIFOs this gets it full and empty a bit
    """
    push_random_seed = "a different push_random_seed"
    pop_random_seed = "a different pop_random_seed"
    test_stages = [(1000,  0.8, 0.1), # Fill it up
                   (2000, 0.6, 0.6), # Consume stuff
                   (1000,  0.1, 1.0), # Empty
                   (50,    0, 1.0), # Empty
    ]
    pass

#a Hardware and test instantiation
#c FifoHardware
class FifoHardware(HardwareThDut):
    clock_desc = [("clk",(0,1,1)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "dprintf_2_fifo_4"
    dut_inputs  = {"req_in":t_dprintf_req_2,
                   "ack_out":1,
    }
    dut_outputs = {"req_out":t_dprintf_req_2,
                   "ack_in":1,
                   "fifo_status":t_fifo_status
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    def __init__(self, module_name, fifo_data_type, **kwargs):
        self.module_name = module_name
        self.dut_inputs = dict(self.dut_inputs)
        self.dut_outputs = dict(self.dut_outputs)
        self.dut_inputs["req_in"]   = fifo_data_type
        self.dut_outputs["req_out"] = fifo_data_type
        super(FifoHardware,self).__init__(**kwargs)
        pass
    pass

#c TestFifo
class TestFifo(TestCase):
    hw = FifoHardware
    _tests = {"smoke": (FifoTest_0, 1*1000,   {"module_name":"dprintf_2_fifo_4",
                                               "fifo_data_type":t_dprintf_req_2,
              }),
              "fifo4_more": (FifoTest_1, 10*1000,   {"module_name":"dprintf_2_fifo_4",
                                                     "fifo_data_type":t_dprintf_req_2,
              }),
              "fifo512_deep": (FifoTest_1, 10*1000,   {"module_name":"dprintf_4_fifo_512",
                                                       "fifo_data_type":t_dprintf_req_4,
                                                       "th_args":{"fifo_size":515},
              }),
    }

