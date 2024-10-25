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
 * @file   fifo_status.h
 * @brief  Types for FIFO status reporting
 *
 */
/*a Types */
/*t t_fifo_status
 */
typedef struct {
    bit     pushed;
    bit     popped;
    bit     empty;
    bit     full;
    bit     overflowed;
    bit     underflowed;
    bit[32] entries_full;
    bit[32] spaces_available;
} t_fifo_status;
