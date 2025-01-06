#a Copyright
#  
#  This file 'test_byte_fifo_multiaccess.py' copyright Gavin J Stark 2024
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
from regress.utils.fifo_status  import t_fifo_status
from cdl.sim     import ThExecFile
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional, Tuple

#c FifoData_Base
class FifoData_Base(object):
    data_mask = 0xffff
    def __init__(self, th):
        self.th         = th
    #f will_take_push
    def will_take_push(self, num:int) -> bool:
        return self.space_available >= num
    #f has_valid_data
    def has_valid_data(self) -> int:
        return self.can_pop.value()==1
    #f validate_data
    def validate_data(self, data) -> None:
        a = self.pop_data.value()
        self.th.compare_expected("Data out of FIFO matches data in",a,data)
        pass
#c FifoTest_Base
class FifoTest_Base(ThExecFile):
    th_name = "Utils FIFO test harness"
    fifo_size = 24
    bpa = 8
    push_random_seed = "push_random_seed"
    pop_random_seed = "pop_random_seed"
    rnd_none = lambda rand: 0
    rnd_few = lambda rand: rand.choice([0,0,0,0,0,0,0,0,1,2,3,5,8])
    rnd_some = lambda rand: rand.choice([0,1,2,3,4,5,6,7,8])
    rnd_many = lambda rand: rand.choice([0,0,2,4,4,5,5,6,6,7,7,8])
    rnd_all = lambda rand: 8
    test_stages = [("Base Reason Fill", 10,  rnd_many, rnd_few), # Fill it up
                   ("Base Reason Consume", 300, rnd_some, rnd_some), # Consume stuff
                   ("Base Reason Empty", 30,  rnd_few, rnd_all), # Empty
                   ("Base Reason Finish", 30,  rnd_none, rnd_all), # Empty
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
    #f generate_push
    def generate_push(self, num_push) -> None:
        """
        Push *up to* num_push data
        """
        if num_push > self.bpa: num_push = self.bpa
        if self.queue.qsize() + num_push > self.fifo_size:
            num_push = self.fifo_size - self.queue.qsize()
            pass
        self.data_in_bytes_valid.drive(num_push)
        data = self.global_cycle() * 0x149f
        data = data & 0xffffffffffffffff
        self.data_in.drive(int(data))
        for i in range(num_push):
            self.queue.put(data & 0xff)
            data = data >> 8
            pass
        self.will_push = num_push
        pass
    #f generate_pop
    def generate_pop(self, num_pop:int) -> Tuple[int,int]:
        if num_pop > self.bpa: num_pop = self.bpa
        if num_pop > self.queue.qsize():
            num_pop = self.queue.qsize()
            pass
        self.data_bytes_popped.drive(num_pop)
        self.will_pop = num_pop
        data = 0
        for i in range(num_pop):
            data |= self.queue.get()<<(i*8)
            pass
        return (num_pop, data)
    pass
    #f fifo_accounting_tick
    def fifo_accounting_tick(self, data_popped) -> None:
        self.bfm_wait(1)
        num_popped = data_popped[0]
        data_popped = data_popped[1]
        if num_popped > 0:
            if self.data_out_bytes_valid.value() < num_popped:
                self.failtest("Data out had fewer bytes valid than the amount popped")
                pass
            data_out = self.data_out.value() & ((1<<(8*num_popped))-1)
            self.compare_expected("Data popped",data_out, data_popped)
            pass
        self.compare_expected("Popped",self.fifo_status__popped.value(), self.last_data_being_popped)
        self.compare_expected("Pushed",self.fifo_status__pushed.value(), self.last_data_being_pushed)
        self.last_data_being_pushed = 0 + (self.will_push > 0)
        self.last_data_being_popped = 0 + (self.will_pop > 0)
        self.compare_expected("Fifo entries",self.fifo_status__entries_full.value(), self.last_queue_size)
        self.compare_expected("Fifo space",self.fifo_status__spaces_available.value(), self.fifo_size-self.last_queue_size)
        self.compare_expected("Fifo full",self.fifo_status__full.value(), int(self.last_queue_size==self.fifo_size))
        self.compare_expected("Fifo empty",self.fifo_status__empty.value(), int(self.last_queue_size==0))
        pass
    #f generate_fifo_input
    def generate_fifo_input(self, num_push, num_pop) -> Tuple[int, int]:
        self.last_queue_size = self.queue.qsize()
        qs = self.queue.qsize()
        if num_pop > qs: num_pop = qs
        self.generate_push(num_push)
        return self.generate_pop(num_pop)
    #f run
    def run(self) -> None:
        self.queue = Queue()
        # self.data = self.fifo_data(self)
        self.push_random = Random()
        self.pop_random = Random()
        self.push_random.seed(self.push_random_seed)
        self.pop_random.seed(self.pop_random_seed)
        self.last_data_being_pushed = 0
        self.last_data_being_popped = 0
        for (reason, length, push_rnd, pop_rnd) in self.test_stages:
            self.verbose.warning(reason)
            for i in range(length):
                data_popped = self.generate_fifo_input(push_rnd(self.push_random),pop_rnd(self.pop_random))
                self.fifo_accounting_tick(data_popped)
                pass
            pass
        self.bfm_wait(10)
        self.compare_expected("Fifo has not underflowed", self.fifo_status__underflowed.value(), 0)
        self.compare_expected("Fifo has not overflowed", self.fifo_status__overflowed.value(), 0)
        self.compare_expected("Queue empty at end of test", self.queue.empty(), True)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.verbose.warning("Completed after %d cycles"%self.global_cycle())
        self.passtest("Test completed")
        pass
    pass

#c FifoTest_24_8_long
class FifoTest_24_8_long(FifoTest_Base):
    push_random_seed = "push_random_seed"
    pop_random_seed = "pop_random_seed"
    rnd_none = lambda rand: 0
    rnd_few = lambda rand: rand.choice([0,0,0,0,0,0,0,0,1,2,3,5,8])
    rnd_some = lambda rand: rand.choice([0,1,2,3,4,5,6,7,8])
    rnd_many = lambda rand: rand.choice([0,0,2,4,4,5,5,6,6,7,7,8])
    rnd_all = lambda rand: 8
    test_stages = [("Fill 24_8_long by push many, pop few", 100,  rnd_many, rnd_few), # Fill it up
                   ("Push some, pop some", 3000, rnd_some, rnd_some), # Consume stuff
                   ("Empty with push few, pop all", 300,  rnd_few, rnd_all), # Empty
                   ("Empty finally with only pop", 300,  rnd_none, rnd_all), # Empty
                   ]
    pass

#c FifoTest_4_long
class FifoTest_4_long(FifoTest_Base):
    push_random_seed = "push_random_seed"
    pop_random_seed = "pop_random_seed"
    rnd_none = lambda rand: 0
    rnd_few = lambda rand: rand.choice([0,0,0,0,0,0,0,0,1,2,3])
    rnd_some = lambda rand: rand.choice([0,1,2,3,4])
    rnd_many = lambda rand: rand.choice([0,1,2,2,3,4,4,4,4])
    rnd_all = lambda rand: 4
    test_stages = [("Fill 4_long by push many, pop few", 100,  rnd_many, rnd_few), # Fill it up
                   ("Push some, pop some", 3000, rnd_some, rnd_some), # Consume stuff
                   ("Empty with push few, pop all", 300,  rnd_few, rnd_all), # Empty
                   ("Empty finally with only pop", 300,  rnd_none, rnd_all), # Empty
                   ]
    pass

#c FifoTest_12_4_long
class FifoTest_12_4_long(FifoTest_4_long):
    fifo_size = 12
    pass

#c FifoTest_16_4_long
class FifoTest_16_4_long(FifoTest_4_long):
    fifo_size = 16
    pass

#a Hardware and test instantiation
#c FifoHardware
class FifoHardware(HardwareThDut):
    clock_desc = [("clk",(0,1,1)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "byte_fifo_multiaccess"
    dut_inputs  = {"data_in":64,
                   "data_in_bytes_valid":4,
                   "data_bytes_popped":4,
    }
    dut_outputs = {"data_out":64,
                   "data_out_bytes_valid":4,
                   "fifo_status":t_fifo_status
    }
    loggers = { }
    def __init__(self, fifo_depth, bpa, **kwargs):
        module_name = "byte_fifo_multiaccess_%d_%d"%(fifo_depth, bpa)
        self.module_name = module_name
        self.dut_inputs = dict(self.dut_inputs)
        self.dut_outputs = dict(self.dut_outputs)
        self.dut_inputs["data_in"] = bpa*8
        self.dut_inputs["data_in_bytes_valid"] = bpa.bit_length()
        self.dut_inputs["data_bytes_popped"] = bpa.bit_length()
        self.dut_outputs["data_out"] = bpa*8
        self.dut_outputs["data_out_bytes_valid"] = bpa.bit_length()
        super(FifoHardware,self).__init__(**kwargs)
        pass
    pass

#c TestFifo
class TestFifo(TestCase):
    hw = FifoHardware
    _tests = {"smoke": (FifoTest_24_8_long, 10*1000,   {"fifo_depth":24, "bpa":8}),
              "t24_8": (FifoTest_24_8_long, 10*1000,   {"fifo_depth":24, "bpa":8}),
              "t12_4": (FifoTest_12_4_long, 10*1000,   {"fifo_depth":12, "bpa":4}),
              "t16_4": (FifoTest_16_4_long, 10*1000,   {"fifo_depth":16, "bpa":4}),
    }

