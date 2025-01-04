/*a Includes */
include "debug.h"
include "sram_access.h"

/*a Modules */
/*m dbg_master_mux */
extern
module dbg_master_mux( clock clk,
                       input bit reset_n    "Active low reset",
                       input t_dbg_master_request    dbg_master_req  "Request from the client to execute from an address in the ROM",
                       output t_dbg_master_response  dbg_master_resp "Response to the client acknowledging a request",
                       output t_dbg_master_request   req0,
                       input t_dbg_master_response  resp0,
                       output t_dbg_master_request   req1,
                       input t_dbg_master_response  resp1,
                       output t_dbg_master_request   req2,
                       input t_dbg_master_response  resp2,
                       output t_dbg_master_request   req3,
                       input t_dbg_master_response  resp3
    )
{
    timing to   rising clock clk dbg_master_req;
    timing from rising clock clk dbg_master_resp;

    timing from rising clock clk req0, req1, req2, req3;
    timing to   rising clock clk resp0, resp1, resp2, resp3;
}

/*m dbg_master_fifo_sink */
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

/*m dbg_master_sram_access */
extern
module dbg_master_sram_access( clock clk,
                               input bit reset_n    "Active low reset",
                               input t_dbg_master_request    dbg_master_req  "Request from the client to execute from an address in the ROM",
                               output t_dbg_master_response  dbg_master_resp "Response to the client acknowledging a request",
                               output t_sram_access_req sram_access_req,
                               input t_sram_access_resp sram_access_resp
    )
{
    timing to   rising clock clk dbg_master_req;
    timing from rising clock clk dbg_master_resp;
    timing to   rising clock clk sram_access_resp;
    timing from rising clock clk sram_access_req;
}
