include "fifo_sink.h"
extern module fifo_sink( clock clk,
                             input bit reset_n    "Active low reset",
                             input t_fifo_sink_ctrl fifo_sink_ctrl,
                             output t_fifo_sink_response fifo_resp,
                             input t_fifo_status fifo_status,
                             input bit data_valid "May occur in the same cycle as pop_fifo & pop_rdy OR later; can often be tied to !empty",
                             input bit[64] data0,
                             input bit[64] data1,
                             input bit[64] data2,
                             input bit[64] data3,
                             input bit[64] data4,
                             input bit pop_rdy "Must be independent of pop_fifo output, indicates a pop_fifo would be taken",
                             output bit pop_fifo "Must be deasserted if a pop is taken but data_valid is not asserted; can be reasserted once data_valid has become asserted"
    )
{
    timing to   rising clock clk fifo_sink_ctrl, fifo_status;
    timing to   rising clock clk data_valid, pop_rdy;
    timing to   rising clock clk data0, data1, data2, data3, data4;
    timing from rising clock clk fifo_resp;
    timing from rising clock clk pop_fifo;
}

extern module byte_fifo_multiaccess_24_8( clock clk                            "Clock for logic",
                                     input bit reset_n                    "Active low reset",

                                     input bit[64] data_in "64 bits of data valid in",
                                     input bit[4] data_in_bytes_valid "0 to 8 bytes valid in, for push",

                                     input bit[4] data_bytes_popped "Number of data_out bytes popped",
                                     output bit[64] data_out "Data out from the FIFO, byte 0 first",
                                     output bit[4] data_out_bytes_valid "Number of bytes valid in data_out, 0 to 8",

                                     output t_fifo_status fifo_status "Fifo status"
    )
{
    timing to   rising clock clk data_in, data_in_bytes_valid, data_bytes_popped;
    timing from rising clock clk data_out, data_out_bytes_valid;
    timing from rising clock clk fifo_status;
}
