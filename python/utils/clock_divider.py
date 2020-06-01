#a Copyright
#  
#  This file 'clock_divider.py' copyright Gavin J Stark 2020
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

# t_clock_divider_control */
t_clock_divider_control = {
    "write_config":1,
    # "Asserted if clock divider configuration should be written";
    "write_data":32,
    # "Data to be used if write_config is asserted";
    "start":1,
    # "Assert to start the clock divider - deassert if running";
    "stop":1,
    # "Assert to stop the clock divider - only used if running";
    "disable_fractional":1,
    # "Assert to disable fractional mode";
}

# t_clock_divider_output */
t_clock_divider_output = {
    "config_data":32, # "Current configuration, as last written (defaults to 0)";
    "running":1, # "Asserted if the clock divider has been started";
    "clock_enable":1, # "Output from the clock divider";
}

#a Useful functions
#f dda_of_ratio
def dda_of_ratio(r):
    """
    Get adder+subtractor values to achieve ratio r = (n,d)
    """
    if r is None: return (0,0)
    (n,d) = r
    dda_add = n-1
    dda_sub = d-2-dda_add
    return (dda_add, dda_sub)
    
#f find_closest_ratio
def find_closest_ratio(f:float, max:int):
    """
    Find closest ratio to frequency f where components have a max value
    """
    def ratio_compare(f:float, r) -> int:
        (n,d) = r
        diff = f*d - n
        if abs(diff)<1.0/max/3: return 0
        if diff<0: return -1
        return 1
    must_be_above = (0, 1)
    must_be_below = (1, 0)
    while True:
        ratio_to_test = (must_be_below[0] + must_be_above[0],
                         must_be_below[1] + must_be_above[1])
        (dda_add, dda_sub) = dda_of_ratio(ratio_to_test)
        if (dda_add>=max) or (dda_sub>=max):
            break
        c = ratio_compare(f,ratio_to_test)
        if (c==0): return ratio_to_test
        if (c==1):
            must_be_above = ratio_to_test
            pass
        else:
            must_be_below = ratio_to_test
            pass
        pass
    if must_be_above[0]==0: return None
    return must_be_above
