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

/*t t_dbg_master_request */
typedef struct {
    t_dbg_master_op op;
    bit[4] num_data_valid "Number of bytes valid, 0 to 6, in data; ignored if not an op data";
    bit[64] data;
} t_dbg_master_request;

/*t t_dbg_master_response
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

