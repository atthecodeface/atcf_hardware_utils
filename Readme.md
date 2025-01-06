# ATCF Utilities

This is a library of utilities. It includes basic SRAM access, FIFOs,
valid-ack buffers/multiplexers, and debug modules including the
`dprintf` and `dbg_master` request/response system:

* SRAM access; providing a standard SRAM read/write mechanism to allow
  for abstracted access for any SRAM.

* FIFO modules; register-based or SRAM-backed, with standard status
  reporting.

* Valid-ack multiplexers (arbiters) and clock-domain crossing modules;
  these use types that include a `valid` signal, and a transfer occurs
  when `valid` is asserted and a reverse direction `ack` is asserted.

* Clock divider; a simple clock gate generator that is run-time
  configured to provide an enable at a fixed frequency that can be any
  rational fraction.

* Dprintf modules; this is a hardware *printf* system that formats
  output for display to a character-based frame buffer, to a UART, or
  to a byte-debug FIFO.

* Debug master request/response and endpoints; this defines a protocol
  for byte streams of requests to endpoints, and byte streams of
  result data - such an endpoint might be an SRAM read port, or a FIFO
  data/status access.

## Clock divider

A clock divider utility module is provided, which generates either a
simple divide-by-N (31-bit value) or a fractional divider.

The module takes a `t_clock_divider_control` input, which allows for
writing the configuration of the divider, and controlling its
operation (with start and stop). The config 32 bits of write data; if
the top bit is clear then the remaining 31-bits provide the value for
a divide-by-N counter. If the top bit is asserted (and
disable_fractional is deasserted) then a digital differential
accumulator (DDA) is used.

The DDA has an accumulator value which is treated as a signed 16-bit
value; the configuration has a 15-bit **add** value, and a 15-bit
**subtract** value. If the accumulator is positive or zero then the
**subtract** value is subtracted from it, and if the accumulator is
negative then it has the **add** value added to it. The output clock is
enabled in every tick following one in which the accumulator is
negative. The result of this is that the output clock enable is
asserted for **add** cycles out of every **add** plus **subtract** cycles.

To start the clock divider, the **start** signal should be
asserted. Its value is ignored when the divider is running.

To stop a running clock divider, the **stop** signal should be
asserted. Its value is ignored while the divider is not running.

## FIFO modules

Numerous synchronous FIFO modules are provided; they use a standard
FIFO status indication, which is the `t_fifo_status` type.

Small FIFO implementations can use registers for the contents; larger
FIFOs use SRAMs.

For more details, see the generic valid ack modules - the FIFOs
indicate push with a valid input when ready, and pop when the output
data is valid and the client is asserting the output ready signal.

An additional modules is provided, `byte_fifo_multiaccess`. This has a
push interface of a variable number of bytes, and a pop interface of a
variable number of bytes. It is designed for systems that parse byte
streams (such as the debug script system).

### FIFO status

The common FIFO status type `t_fifo_status` contains

```
bit     pushed;
bit     popped;
bit     empty;
bit     full;
bit     overflowed;
bit     underflowed;
bit[32] entries_full;
bit[32] spaces_available;
```

Pushed and popped are registered indications that the FIFO was pushed
or popped; they can be used, for example, to invoke dprintf debug
requests to display the fullness of the FIFO.

Empty and full indicate the current state of the FIFO, as do
`entries_full and spaces_available`. Overflowed and underflowed are
*sticky* values - they indicate a hardware failure, and if they become
set a hardware assertion should be raised.

## SRAM access modules

A standard SRAM control bus is provided, so that SRAMs can conform to
a simple standard interface. This does not handle ECC (in the sense of
supplying ECC syndromes with the request or the ability to poison the
SRAM - the SRAM may itself support ECC by generating syndromes for
write data and checking them on read data).

It has valid, 8-bit id, `read_not_write`, 32-bit address, 64-bit write
data, and 8-bit byte emables.

An SRAM access multiplexer module, `sram_access_mux_2`, provides a
simple arbiter between two SRAM access requesters into an SRAM.  To
distinguish between the read data for the two masters, the **id** fields
of the requests (which should appear in SRAM read data responses) can
be used.

## Async bus reduction modules

A generic valid-and-data bus reduction module supports taking
validated data on one clock and presenting it as valid data on another
clock domain.

Instances of this module are named along the line of
`async_reduce_4_28_r`; this takes a 4-bit validated input bus and
produces a 28-bit validated output bus on a different clock, with the
oldest 4-bit data appearing in the bottom bits (right). The naming
scheme is `async_reduce_I_O_[lr]`, for a module that uses the
`generic_async_reduce` module with a single width shift register, an
input data bus of width I bits, and an output data bus with a width of
O bits. The output clock period must be no more than 3*O/I times the
valid input data period (i.e. output clock > input clock * 3I/O.

For uses of the generic module with a double shift register the name
would be `async_reduce2_I_O_[lr]`. This has the constraint that output
clock > input clock * 3/2 * I/O

Thus `async_reduce2_4_16` with an input clock of 312.5MHz (such as
required for GMII) has an output clock requirement (taking 16-bit
validated data) of at least 312.5 * 3/8 or about 116MHz (i.e. 125MHz
is ideal).

### `generic_async_reduce` module

The `generic_async_reduce` module takes a validated bus with one
clock, and presents a validated bus of a multiple of the input width
on a second clock.

It uses a shift register to combine a number of valid input data, as
either least-significant first or most-significant first, into an
output data. A full toggle synchronizer is used between the two clock
domains. There is no reverse synchronizer; the output must is assumed
to take the data. The synchronization takes three output clock
ticks. The synchronized data rate (and hence input data rate) is
therefore no faster than the output clock times shift register width
divided by 3.

With the shift register set to be the size of the output data, the
output data rate will be no more than three times the output width;
There is an option to have a double-output-width length shift
register. This permits a smaller output data bus width, as two valid
output data are provided for every three output clock periods.

## Generic valid ack modules

The standard approach of having data that is passed when it is valid
and the receiver is ready is supported with this set of modules. Most
are fully syncrhonous.

### `generic_async_valid_ack_slow` module

This is a very simple valid/ack synchronized data buffer using a
toggle for going between the two clock domains.

The transfer rate is one data item per three to four clock ticks each
of both sides (i.e. if the clock periods are 20ns and 70ns, then the
data is transferred one transaction every 270ns.

### `generic_valid_ack_double_buffer` module

A synchronous double-register buffer, effectively a 2-entry FIFO

This has slightly simplified logic compared to an N-entry register
FIFO with N=2.

As a fifo, it has a `t_fifo_status` output.

### `generic_valid_ack_fifo` module

Very simple synchronous generic register FIFO for a valid/ack
system. It is implemented with a circular buffer of registered entries
and read and write pointers; plus there is an output data register.

On a push, if the FIFO will be empty then the input data is stored in
the output register; if the FIFO will not be empty then the input data
is stored in `register[write_ptr]`.

If the FIFO is not empty and output register will be empty then the
contents of register[read_ptr] is copied to thenoutput register

### `generic_valid_ack_insertion_buffer` module

This is a synchronous generic insertion buffer, with 8 outputs of the
current buffer contents (including valids)

This is a FIFO whose contents are fully visible; the FIFO is
implemented by inserting new data directly after the last valid entry,
so that the valid contents are presented from output entry 0
upwards. When the data is read the contents shift down by one entry.

### `generic_valid_ack_mux` module

This is a multiplexer for two identical requesters (with a valid
signal each), to arbitrate for an output request, with a response with
an **ack** signal.

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

### `generic_valid_ack_sram_fifo` module

A deep valid/ack FIFO using a synchronous dual-port SRAM and
read/write pointers.  The module can keep up with a data in per cycle
and a data out per cycle.

The SRAM must have a read-to-data delay of a cycle.

## Hysteresis

This module takes an input signal and notionally keeps a count of
cycles that the input is low, and cycles that the input is high; using
these counters it makes a decision on the real value of the output,
using hysteresis.

Since infinite history is not sensible and the counters cannot run
indefinitely without overflow anyway, the counters divide by 2 on a
configurable divider (effectively filtering the input stream).

The two notional counters are `cycles_low` and `cycles_high`.

To switch to a **high** output from a current **low** output requires
the `cycles_high - cycles_low` to be greater than half of the filter
period.

To switch to a **low** output from a current **high** output requires
the `cycles_low - cycles_high` to be greater than half of the filter
period.

Hence a n+1 bit difference would need to be maintained for
`cycles_high` and `cycles_low`. This difference would increase by 1 if
the input is high, and decrease by 1 if the input is low.

Hence an actual implementation can maintain an up/down counter
`cycles_diff`, which is divided by 2 every filter period, and which is
incremented on input of 1, and decremented on input of 0.

When the output is low and the `cycles_diff` is greater than half the
filter period the output shifts to high.

When the output is high and the `cycles_diff` is less than minus half
the filter period the output shifts to low.

## DPrintf modules

The dprintf system provides a means to generate strings of bytes with
associated addresses from a **printf**-like input. The purpose is to
allow hardware to write a debug message such as `Addr 0x400 data
0x1234` onto a textual video buffer, or to a UART.

The core module is the dprintf module itself. This takes a `t_dprintf`
input, which is a validated type with up to 32 bytes of data with a
corresponding address. It interprets the bytes one by one, and
produces an output byte stream (valid, address, byte, and a **last**
byte indicator).

The input byte stream consists of ASCII characters plus potentially
*video control* characters - all in the range 1 to 127, plus control
codes of 0 or 128 to 255.

The code 0 is just skipped; it allows for simple alignment of data in
the dprintf request.

Byte values from 1 to 127 are passed through unchanged.

A code of 128 to 191 is a zero-padded hex format field. The encoding
is 8h10xxssss; x is unused, and the size ss is 0-f, indicating 1 to 16
following nybbles are data (msb first). The data follows in the
succeeding bytes.

A code of 192 to 254 is a space-padded decimal format field. The
encoding is 8h11ppppss; the size is 0-3 for 1 to 4 bytes of data, in
the succeeding bytes. The padding (pppp) is zero for no padding; 1
forces the string to be at least 2 characters long (prepadded with
space if required); 2 is pad to 3 characters, and so on. The maximum
padding is to a ten character output (pppp of 9).

A code of 255 terminates the string.

As the dprintf request is a valid-ack interface, the numerous generic
FIFO and arbiter modules can be used to buffer and select from
multiple masters; the sources of the dprintf requests tend to be very
simple logic such as:

```
if (dp_req_1.valid && dp_req_1_ack) {
  dp_req_1.valid <- 0;
}
if (event_fired) {
  dp_req_1.valid <= 1;
  dp_req_1.address <= 64;
  dp_req_1.data_0 <= 64h_48656c6c6f2083;
  dp_req_1.data_1 <= bundle(event_addr[0; 16], 8hff, 40b0);
}
```

This will produce an output byte stream of “Hello ABCD” if the
`event_addr` is 0xABCD.

The `dprintf_4_mux` module multiplexes two input requests (round
robin) onto an output.

The `dprintf_4_fifo_4` is a 4-deep `t_dprintf4` synchronous FIFO; this
can help smooth bursts of debug messages should they occur at the same
time. The `dprintf_4_fifo_512` is an SRAM FIFO that provides even more
buffering of messages.

The `dprintf_4_async` module allows a dprintf request to cross from
one clock domain to another (at the rate of one transfer every 3 input
and output clock periods. This should be used to cross asynchronous
clock boundaries.

## Debug master bus

The library provides a pair of buses that allow some form of debug
master to access, through a simple byte script, an endpoint such as an
APB bus master, a FIFO, or an SRAM. The library really provides the
buses and defines the protocol; it also includes two debug endpoints
(one for FIFO data and status reading, and one for SRAM reading).

The debug master bus provides a byte stream to the debug endpoint, and
the endpoint returns streams of bytes or an error code. The endpoint
parses the request byte stream and consumes up to eight bytes in one
cycle, and delivers up to eight bytes as a result (with error code) in
one cycle.

### Debug SRAM access endpoint

The `dbg_master_sram_access` module takes a debug master request and
interprets a byte stream as an opcode byte followed by two bytes
encoding an SRAM address, and two bytes encoding a number of
**entities** to read. The opcode indicates the size of an **entity** -
i.e. the number of bytes of read data from the SRAM should be returned
to the debug master as a single **entity**.

The opcode byte should be 0 to read N single bytes from successive
addresses; it should bef 1 to read N 16-bit values each from
successive addresses, and so om up to a value of 7 to read N 64-bit
values each from successive addresses.

### Debug FIFO data/status endpoint

The `dbg_master_fifo_sink` module takes a debug master request and
interprets a byte stream as an opcode byte followed by two bytes
encoding an SRAM address, and two bytes encoding a number of
**entities** to read. The opcode indicates the size of an **entity** -
i.e. the number of bytes of read data from the SRAM should be returned
to the debug master as a single **entity**.

The opcode byte should be 0 to read N single bytes from successive
addresses; it should bef 1 to read N 16-bit values each from
successive addresses, and so om up to a value of 7 to read N 64-bit
values each from successive addresses.


### Debug master demultiplexer/multiplexer

The `dbg_master_mux` module takes a debug master request and interprets
a *single* byte at the start of each stream as an endpoint select
value. It then has four debug master interface to four different
endpoints.

# Commonmark notes

Heading: #; subheading ##; subsubheading ###.

*Italics*, **Bold**, and `inline code`. Or _italics_, __bold__.

> Block quotes

* Item list

1. Numeric list

2. Numeric list

```
Code block
```

[link](http://stuff "Title for link")

![Image description](http://a.jpg "Image title")


