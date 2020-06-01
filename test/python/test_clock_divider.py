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
from regress.utils.clock_divider import t_clock_divider_control, t_clock_divider_output
from regress.utils.clock_divider import find_closest_ratio
from cdl.sim     import ThExecFile, LogEventParser
from cdl.sim     import HardwareThDut
from cdl.sim     import TestCase
from typing import Optional

#c ClockDividerTest_Base
class ClockDividerTest_Base(ThExecFile):
    th_name = "Utils clock divider test harness"
    enable_fractional = 0
    def __init__(self, fraction=None, measure_periods=100, **kwargs) -> None:
        if fraction is not None:
            if fraction<1.0: raise Exception("Bug - fraction cannot be <1 (as clock is a divider not a multiplier")
            (n,d) = find_closest_ratio(fraction, self.max_parameter )
            self.clock_test_data = [ (n-d, d, 1, measure_periods, fraction) ]
            pass
        super(ClockDividerTest_Base,self).__init__(**kwargs)
        pass
    #f exec_init
    def exec_init(self) -> None:
        self.die_event         = self.sim_event()
        super(ClockDividerTest_Base,self).exec_init()
        pass
    #f write_config_data
    def write_config_data(self, adder, subtractor, fractional_mode=0):
        data = (subtractor<<16) + (adder<<0)
        if fractional_mode: data = data | (1<<31)
        self.divider_control__write_config.drive(1)
        self.divider_control__write_data.drive(data)
        self.divider_control__disable_fractional.drive(1^self.enable_fractional)
        self.bfm_wait(1)
        self.divider_control__write_config.drive(0)
        self.bfm_wait(1)
        self.compare_expected("config written",self.divider_output__config_data.value(),data)
        pass
    #f start
    def start(self):
        self.compare_expected("divider running",self.divider_output__running.value(),0)
        self.divider_control__start.drive(1)
        self.bfm_wait(2)
        self.divider_control__start.drive(0)
        self.compare_expected("divider running",self.divider_output__running.value(),1)
        self.bfm_wait(1)
        pass
    #f stop
    def stop(self):
        self.compare_expected("divider running",self.divider_output__running.value(),1)
        self.divider_control__stop.drive(1)
        self.bfm_wait(2)
        self.divider_control__stop.drive(0)
        self.compare_expected("divider running",self.divider_output__running.value(),0)
        self.bfm_wait(1)
        pass
            
    #f measure
    def measure(self, num_periods:int) -> float:
        self.divider_output__clock_enable.wait_for_value(1)
        start_cycle = self.bfm_cycle()
        for i in range(num_periods):
            self.bfm_wait(1)
            self.divider_output__clock_enable.wait_for_value(1)
            pass
        end_cycle = self.bfm_cycle()
        period = (end_cycle-start_cycle)/num_periods
        # self.verbose.error("Divider clock period %f"%period)
        return period
            
    #f run__init
    def run__init(self) -> None:
        self.bfm_wait(10)
        pass
    #f run
    def run(self) -> None:
        for (adder, subtractor, fractional_mode, measure_periods, divider_clock_period) in self.clock_test_data:
            if fractional_mode==0 or not self.enable_fractional:
                if subtractor!=0: raise Exception("Bug - subtractor must be 0 if not fractional")
                pass
            self.write_config_data(adder=adder,subtractor=subtractor,fractional_mode=fractional_mode)
            self.start()
            period = self.measure(measure_periods)
            err = abs(period-divider_clock_period)/divider_clock_period
            if err>0.01:
                self.failtest("Clock rate for %d/%d/%d exceeded 1%% error rate (got %f, expected %f)"%
                              (adder, subtractor, fractional_mode, period, divider_clock_period))
                pass
            self.stop()
            pass
        self.bfm_wait(10)
        pass
    #f run__finalize
    def run__finalize(self) -> None:
        # self.verbose.error("%d"%self.global_cycle())
        self.passtest("Test completed")
        pass
    pass

#c ClockDividerTest_0
class ClockDividerTest_0(ClockDividerTest_Base):
    clock_test_data = [
        (100,0,0,10,101.0),
        (1,0,0,10,2.0),
        (2,0,0,10,3.0),
        (64,0,0,10,65.0),
        ]
    pass

#c ClockDividerTest_Fractional_1
class ClockDividerTest_Fractional_1(ClockDividerTest_Base):
    enable_fractional = 1
    clock_test_data = [
        (1,0,0,10,2.0),
        (1,1,1,10,2.0),
        (1,7,1,100,8/7),
        (7,1,1,10,8/1),
        (2,3,1,100,5/3),
        ]
    pass

#c ClockDividerTest_Fractional_Runtime
class ClockDividerTest_Fractional_Runtime(ClockDividerTest_Base):
    enable_fractional = 1
    max_parameter = 200
    pass

#a Hardware and test instantiation
#c ClockDividerHardware
class ClockDividerHardware(HardwareThDut):
    clock_desc = [("clk",(0,2,2)),
    ]
    reset_desc = {"name":"reset_n", "init_value":0, "wait":5}
    module_name = "clock_divider"
    dut_inputs  = {"divider_control":t_clock_divider_control,
    }
    dut_outputs = {"divider_output":t_clock_divider_output,
    }
    loggers = { # "dprintf": {"modules":"dut.dut", "verbose":1}
                }
    pass

#c TestClockDivider
class TestClockDivider(TestCase):
    hw = ClockDividerHardware
    _tests = {"0": (ClockDividerTest_0, 30*1000,   {"th_args":{}}),
              "fractional_smoke": (ClockDividerTest_Fractional_1, 5*1000,   {"th_args":{}}),
              "fractional_rt_0": (ClockDividerTest_Fractional_Runtime, 2*1000, {"th_args":{"fraction":1.54}}),
              "fractional_rt_1": (ClockDividerTest_Fractional_Runtime, 2*1000, {"th_args":{"fraction":4.58}}),
    }

