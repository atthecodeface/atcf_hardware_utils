/*a Includes */
include "debug.h"

/*a Modules */
/*m dprintf */
extern
module dbg_master_fifo_sink( clock clk,
                             input bit reset_n    "Active low reset",
                             input t_dbg_master_request    dbg_master_req  "Request from the client to execute from an address in the ROM",
                             output t_dbg_master_response  dbg_master_resp "Response to the client acknowledging a request",
                             input t_fifo_status fifo_status,
                             input bit[64] data0,
                             input bit[64] data1,
                             input bit[64] data2,
                             input bit[64] data3,
                             output bit pop_fifo
    )
{
    timing to   rising clock clk dbg_master_req;
    timing from rising clock clk dbg_master_resp;
    timing to   rising clock clk fifo_status, data0, data1, data2, data3;
    timing from rising clock clk pop_fifo;
}
