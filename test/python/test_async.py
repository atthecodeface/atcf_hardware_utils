#a Copyright
#  
#  This file 'test_clock_divider.py' copyright Gavin J Stark 2017-2020
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
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c AsyncReduceTest_Base
class AsyncReduceTest_Base(ThExecFile):
    th_name = "Async reduce test harness"
    test_data = [
        (100, 2),
        (200, 0),
        (100, 2),
        ]
    def __init__(self, fraction=None, measure_periods=100, **kwargs) -> None:
        if fraction is not None:
            if fraction<1.0: raise Exception("Bug - fraction cannot be <1 (as clock is a divider not a multiplier")
            (n,d) = find_closest_ratio(fraction, self.max_parameter )
            self.clock_test_data = [ (n-d, d, 1, measure_periods, fraction) ]
            pass
        super().__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super().exec_init()
        pass
    #f run__init
    def run__init(self) -> None:
        self.valid_in.drive(0)
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        self.verbose.warning(f"Run {self.__class__.__name__} with {self.hardware.__class__.__name__} ")
        n = 0
        e = n
        mask = (1<<self.in_width)-1
        ps = 0
        ps_in = 2*self.hardware.clock_desc[0][1][2]
        ps_out = 2*self.hardware.clock_desc[1][1][2]
        ps = self.global_cycle() % ps_out
        result_data = []
        for (number, gap) in self.test_data:
            self.verbose.warning(f"Run {number} entries with a gap of {gap} for in_width {self.in_width} out_width {self.out_width}")
            for i in range(number):
                self.valid_in.drive(1)
                self.data_in.drive(n & mask)
                self.bfm_wait(1)
                self.valid_in.drive(0)
                ps += ps_in
                if ps >= ps_out:
                    ps -= ps_out
                    if self.valid_out.value() == 1:
                        result_data.append(self.data_out.value())
                        pass
                    pass
                n += 1
                for j in range(gap):
                    self.valid_in.drive(0)
                    self.data_in.drive(0)
                    self.bfm_wait(1)
                    ps += ps_in
                    if ps >= ps_out:
                        ps -= ps_out
                        if self.valid_out.value() == 1:
                            result_data.append(self.data_out.value())
                            pass
                        pass
                    pass
                pass
            pass
        out_per_in = self.out_width // self.in_width
        first_shift = 0
        ds = self.in_width
        if self.left_to_right:
            first_shift = self.out_width - self.in_width
            ds = -ds
            pass
        for r in result_data:
            s = first_shift
            for i in range(out_per_in):
                v = (r >> s) & mask
                self.compare_expected(f"Data {e}", v, e&mask)
                s += ds
                e += 1
                pass
            pass
        if e < n - out_per_in*4:
            self.failtest(f"Expected more data (put in {n} got back {e}")
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        self.verbose.warning("Completed after %d cycles"%self.global_cycle())
        self.passtest("Test completed")
        pass
    pass

#c AsyncReduce_4_28_L_Test
class AsyncReduce_4_28_L_Test(AsyncReduceTest_Base):
    in_width = 4
    out_width = 28
    left_to_right = True
    pass

#c AsyncReduce_4_28_R_Test
class AsyncReduce_4_28_R_Test(AsyncReduce_4_28_L_Test):
    left_to_right = False
    pass

#c AsyncReduce_4_16_L_Test
class AsyncReduce_4_16_L_Test(AsyncReduceTest_Base):
    in_width = 4
    out_width = 16
    left_to_right = True
    pass

#c AsyncReduce_4_60_L_Test
class AsyncReduce_4_60_L_Test(AsyncReduceTest_Base):
    in_width = 4
    out_width = 60
    left_to_right = True
    pass

#a Hardware and test instantiation
#c AsyncReduce2_4_28_LHardware
class AsyncReduce2_4_28_LHardware(HardwareThDut):
    # Double shift register, so output clock > input clock * 3/2 * I/O
    #
    # Input clock freq of 31.25MHz means output clock > 6.696 MHz
    #
    # Hence output period < 149.33ps, so 148 here
    #
    # Make the slow occur just before the fast in sim for out test harness
    clock_desc = [("clk_in",(0,32,32)),
                  ("clk_out",(147,148,148)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "async_reduce2_4_28_l"
    dut_inputs  = {"valid_in":1,
                   "data_in":4,
    }
    dut_outputs = {"valid_out":1,
                   "data_out":28,
    }
    loggers = { }
    pass

#c AsyncReduce2_4_28_RHardware
class AsyncReduce2_4_28_RHardware(AsyncReduce2_4_28_LHardware):
    module_name = "async_reduce2_4_28_r"
    
#c AsyncReduce2_4_16_LHardware
class AsyncReduce2_4_16_LHardware(HardwareThDut):
    # Double shift register, so output clock > input clock * 3/2 * I/O
    #
    # Input clock freq of 31.25MHz means output clock > 11.71875 MHz
    #
    # Hence output period < 85.3ps, so 84 here
    #
    # Make the slow occur just before the fast in sim for out test harness
    clock_desc = [("clk_in",(0,32,32)),
                  ("clk_out",(83,84,84)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "async_reduce2_4_16_l"
    dut_inputs  = {"valid_in":1,
                   "data_in":4,
    }
    dut_outputs = {"valid_out":1,
                   "data_out":16,
    }
    loggers = { }
    pass

#c AsyncReduce_4_28_LHardware
class AsyncReduce_4_28_LHardware(HardwareThDut):
    # Single shift register, so output clock > input clock * 3 * I/O
    #
    # Input clock freq of 31.25MHz means output clock > 13.392 MHz
    #
    # Hence output period < 74.7ps, so 74 here
    #
    # Make the slow occur just before the fast in sim for out test harness
    clock_desc = [("clk_in",(0,32,32)),
                  ("clk_out",(147,74,74)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "async_reduce_4_28_l"
    dut_inputs  = {"valid_in":1,
                   "data_in":4,
    }
    dut_outputs = {"valid_out":1,
                   "data_out":28,
    }
    loggers = { }
    pass

#c AsyncReduce_4_28_RHardware
class AsyncReduce_4_28_RHardware(AsyncReduce_4_28_LHardware):
    module_name = "async_reduce_4_28_r"
    
#c AsyncReduce_4_16_LHardware
class AsyncReduce_4_16_LHardware(HardwareThDut):
    # Single shift register, so output clock > input clock * 3 * I/O
    #
    # Input clock freq of 31.25MHz means output clock > 23.4375 MHz
    #
    # Hence output period < 42.7, so 42 here
    clock_desc = [("clk_in",(0,32,32)),
                  ("clk_out",(83,42,42)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "async_reduce_4_16_l"
    dut_inputs  = {"valid_in":1,
                   "data_in":4,
    }
    dut_outputs = {"valid_out":1,
                   "data_out":16,
    }
    loggers = { }
    pass

#c AsyncReduce_4_60_LHardware
class AsyncReduce_4_60_LHardware(HardwareThDut):
    # Single shift register, so output clock > input clock * 3 * I/O
    #
    # Input clock freq of 31.25MHz means output clock > 6.25 MHz
    #
    # Hence output period < 160.0, so 160 here
    clock_desc = [("clk_in",(0,32,32)),
                  ("clk_out",(319, 160, 160)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "async_reduce_4_60_l"
    dut_inputs  = {"valid_in":1,
                   "data_in":4,
    }
    dut_outputs = {"valid_out":1,
                   "data_out":60,
    }
    loggers = { }
    pass

#c TestAsyncReduce2_4_28_L
class TestAsyncReduce2_4_28_L(TestCase):
    hw = AsyncReduce2_4_28_LHardware
    _tests = {"l2_4_28": (AsyncReduce_4_28_L_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce2_4_28_R
class TestAsyncReduce2_4_28_R(TestCase):
    hw = AsyncReduce2_4_28_RHardware
    _tests = {"r2_4_28": (AsyncReduce_4_28_R_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce2_4_16_L
class TestAsyncReduce2_4_16_L(TestCase):
    hw = AsyncReduce2_4_16_LHardware
    _tests = {"l2_4_16": (AsyncReduce_4_16_L_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce_4_28_L
class TestAsyncReduce_4_28_L(TestCase):
    hw = AsyncReduce_4_28_LHardware
    _tests = {"l_4_28": (AsyncReduce_4_28_L_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce_4_28_R
class TestAsyncReduce_4_28_R(TestCase):
    hw = AsyncReduce_4_28_RHardware
    _tests = {"r_4_28": (AsyncReduce_4_28_R_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce_4_16_L
class TestAsyncReduce_4_16_L(TestCase):
    hw = AsyncReduce_4_16_LHardware
    _tests = {"l_4_16": (AsyncReduce_4_16_L_Test, 60*1000,   {"th_args":{}}),
    }

#c TestAsyncReduce_4_60_L
class TestAsyncReduce_4_60_L(TestCase):
    hw = AsyncReduce_4_60_LHardware
    _tests = {"smoke": (AsyncReduce_4_60_L_Test, 60*1000,   {"th_args":{}}),
    }

