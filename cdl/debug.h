/*t t_dbg_master_op
  The protocol is:

  idle +
  (start | start_clear)
  { idle *
    data } *
  idle *
  (data_last)
  idle +
  
The state machine will error if data_last and the number of data valid
does not provide a complete operation; hence it can be aborted if
data_last and 0 data are valid.

    Start a script (go @a busy) when a start or start_clear op comes in.
    Start the script state machine (with optional clear).

    Then register data if provided, with a 'last' indication; provide this to
    the script state machine.
    Drive out the number of bytes consumed by the state machine, when used, and
    in the next tycle provide no data to the script state machine.

 */
typedef enum[3] {
    dbg_op_idle,
    dbg_op_start,
    dbg_op_start_clear,
    dbg_op_data,
    dbg_op_data_last,
} t_dbg_master_op;

/*t t_dbg_master_resp_type */
typedef enum[3] {
    dbg_resp_idle,
    dbg_resp_running,
    dbg_resp_completed,
    dbg_resp_poll_failed,
    dbg_resp_errored
} t_dbg_master_resp_type;

/*t t_dbg_master_request

Note that num_data_valid is reduced in the next cycle by the response's *bytes_consumed*.

Once the op is data_last, num_data_valid of 0 indicates full consumption of the data and the debug master should complete.

If the debug master sees data_last and a non-zero num_data_valid and
it cannot interpret the data for an operation then it must complete
with a response type of error; it need not consume the bytes.

Once a debug master has indicated it has completed the request wil be
idle until the next start; during this time the num_data_valid *may*
be nonzero as a data FIFO is consumed with a dbg_op of idle; 
  
 */
typedef struct {
    t_dbg_master_op op;
    bit[4] num_data_valid "Number of bytes valid, 0 to 6, in data; ignored if op is neither data or data_last";
    bit[64] data "Data bytes, valid from bit 0 upwards";
} t_dbg_master_request;

/*t t_dbg_master_response

This must be a wire-or structure, so driven to 0 when a debugger has
not been started.

bytes_valid must be 0 if the resp_type is idle

  The protocol is:

  idle +
  running +
  completing *
  (completed | poll_failed | errored)
  idle +
  
 */
typedef struct {
    t_dbg_master_resp_type resp_type;
    bit[4] bytes_consumed "If non-zero then remove the bottom bytes from the data request in the next cycle; data is never consumed in back-to-back cycles, and this will be zero for one cycle after it is nonzero";
    bit[3] bytes_valid; // 0 through 4
    bit[32] data;
} t_dbg_master_response;

