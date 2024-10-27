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
