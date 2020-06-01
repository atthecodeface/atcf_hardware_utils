extern module fifo_status( clock clk                            "Clock for logic",
                    input bit reset_n                    "Active low reset",
                    input bit push,
                    input bit pop,
                    input bit[32] max_entries "Should be hardwired in parent",
                    output t_fifo_status fifo_status
    )
{
    timing to   rising clock clk push, pop, max_entries;
    timing from rising clock clk fifo_status;
}
