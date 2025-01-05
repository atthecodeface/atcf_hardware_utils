# ATCF Utilities 

## Generic modules

### generic_async_reduce

The *generic_async_reduce* module takes a validated bus with one clock, and presents a validated bus of a multiple of the input width on a second clock.

It uses a shift register to combine a number of valid input data, as either least-significant first or most-significant first, into an output data. A full toggle synchronizer is used between the two clock domains. There is no reverse synchronizer; the output must is assumed to take the data. The synchronization takes three output clock ticks. The synchronized data rate (and hence input data rate) is therefore no faster than the output clock times shift register width divided by 3.

With the shift register set to be the size of the output data, the output data rate will be no more than three times the output width; There is an option to have a double-output-width length shift register. This permits a smaller output data bus width, as two valid output data are provided for every three output clock periods.

A simple example: at an input clock of 10ns (100MHz) and an output clock of 18ns (55MHz) and an input data with of 8 bits, the output data without double shift register is one output data valid every 54ns, rounded up to 60ns (in input clock periods); hence the output data width must be 48bits wide. If a double shift register were used then the output data bus need only be 24 bits wide

The design thus permits a 4-bit input at 312.5MHz (3.2ns period) to transfer to a 125MHz domain (8ns period)
(clk_out/clk_in periods of 2.5) with a shift register width of 4*3*ceil(8/3.2) or 32 bits; the output data can be 16 bits wide if a double shift register is used.

## Generic valid ack modules

The standard approach of having data that is passed when it is valid and the receiver is ready is supported with this set of modules. Most are fully syncrhonous.

### generic_async_valid_ack_slow

This is a very simple valid/ack synchronized data buffer using a toggle for going between the two clock domains.

The transfer rate is one data item per three to four clock ticks each of both sides.

### generic_valid_ack_double_buffer

A synchronous double-register buffer, effectively a 2-entry FIFO

This has slightly simplified logic compared to an N-entry register FIFO with N=2.

As a fifo, it has a fifo_status output.

### generic_valid_ack_fifo

Very simple synchronous generic register FIFO for a valid/ack system

If the output will be empty then the input data is stored in the output register
If not empty then the input data is stored in register[write_ptr];

If not empty and output register will be empty move register[read_ptr] to output register

### generic_valid_ack_insertion_buffer

A synchronous generic insertion buffer, with 8 outputs of the current buffer contents (including valids)

This is a FIFO whose contents are fully visible; the FIFO is implemented by inserting new data directly after the last valid entry, so that the valid contents are presented from output entry 0 upwards.


### generic_valid_ack_mux

This is a multiplexer for two identical requesters (with a valid signal
each), to arbitrate for an output request, with a response with an
‘ack’ signal.

This module may be used with a different type (using type remapping)
to generate a specific multiplexer for two validated requests, which
have just an ack in response (e.g. the teletext dprintf requests).

The module registers its output request; it remembers which requester
it consumed from last, and will preferentially consume from the other
port next - hence supplying some degree of fairness.

When its output is not valid, or is being acknowledged, it may take a
new request from one of the two requesting masters, using the desired
priority. It will also then acknowledge that requester.

If its output is valid and is not acknowledged, then it will not
consumer another request.

### generic_valid_ack_sram_fifo

A deep valid/ack FIFO using a synchronous dual-port SRAM and read/write pointers.
The module can keep up with a data in per cycle and a data out per cycle.

The SRAM has a read-to-data delay of a cycle, and so two output registers
must be kept; these are denoted @a req_out and @a pending_req_out.

If both are valid then the SRAM *must not* be reading (not should it
start a read) as there is nowhere for the data to go.  In this case if
req_out is being acked, then req_out will come from pending_req_out
which will become empty. If req_out is not being acked, then both
registers hold their values. (i.e. hold/hold or pending/empty)

If only one is valid then the SRAM *can* be reading *or* can start a read.
In particular, if req_out is valid and pending_req_out is not, then:
  if req_out is acked then it is either from SRAM or empty; else hold/SRAM, or hold/empty
If req_out is not valid but pending_req_out is, then:
  req_out comes from pending_req_out; pending_req_out is either empty or SRAM

If neither is valid then an SRAM read can certainly start.

There is a single data register on input to capture the @a req_in.
This *must* be transfered if valid to the SRAM or one of the output registers,
unless the SRAM buffer is full.

This permits an @a ack_in unless the @a req_in is valid and the SRAM buffer is full.

## Hysteresis

* CDL implementation of a module that takes an input signal and
 * notionally keeps a count of cycles that the input is low, and
 * cycles that the input is high; using these counters it makes a
 * decision on the real value of the output, using hysteresis.
 *
 * Since infinite history is not sensible and the counters cannot run
 * indefinitely without overflow anyway, the counters divide by 2 on a
 * configurable divider (effectively filtering the input stream).
 *
 * The two notional counters are @a cycles_low and @a cycles_high.
 *
 * To switch to a ‘high’ output from a current ‘low’ output requires
 * the @a cycles_high - @a cycles_low to be greater than half of the
 * filter period.
 *
 * To switch to a ‘low’ output from a current ‘high’ output requires
 * the @a cycles_high - @a cycles_low to be less than minus half of the
 * filter period.
 *
 * Hence a n+1 bit difference would need to be maintained for
 * @a cycles_high and @a cycles_low. This difference would increase by 1
 * if the input is high, and decrease by 1 if the input is low.
 *
 * Hence an actual implementation can maintain an up/down counter
 * @a cycles_diff, which is divided by 2 every filter period, and which
 * is incremented on input of 1, and decremented on input of 0.
 *
 * When the output is low and the @a cycles_diff is > half the filter
 * period the output shifts to high.
 *
 * When the output is high and the @a cycles_diff is < -half the filter
 * period the output shifts to low.

