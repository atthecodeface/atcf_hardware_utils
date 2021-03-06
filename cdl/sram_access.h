/** @copyright (C) 2016-20,  Gavin J Stark.  All rights reserved.
 *
 * @copyright
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *     http://www.apache.org/licenses/LICENSE-2.0.
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 *
 * @file   sram_access.h
 * @brief  Types for pipeline sram access
 *
 */
/*a Types */
/*t t_sram_access_req
 */
typedef struct {
    bit     valid;
    bit[8]  id;
    bit     read_not_write;
    bit[8]  byte_enable;
    bit[32] address;
    bit[64] write_data;
} t_sram_access_req;

/*t t_sram_access_resp
 */
typedef struct {
    bit     ack;
    bit     valid;
    bit[8]  id;
    bit[64] data;
} t_sram_access_resp;

/*a Modules
 */
extern module sram_access_mux_2( clock clk                            "Clock for logic",
                          input bit reset_n                    "Active low reset",
                          input  t_sram_access_req   req_a,
                          output t_sram_access_resp  resp_a,
                          input  t_sram_access_req   req_b,
                          output t_sram_access_resp  resp_b,

                          output t_sram_access_req   req       "id may be ignored if this goes straight to SRAM",
                          input  t_sram_access_resp  resp      "only data needs to be valid if this is straight to SRAM"
    )
{
    timing to    rising clock clk  req_a, req_b, resp;
    timing from  rising clock clk  resp_a, resp_b, req;

    timing comb input  req_a, req_b, resp;
    timing comb output resp_a, resp_b, req;
}
