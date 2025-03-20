/*a Types */
/*t t_fifo_sink_action
 *
 * Action that the FIFO ctrl is taking, based on the FSM state and the opcode etc
 */
typedef enum [2] {
    fifo_sink_action_idle,
    fifo_sink_action_get_status,
    fifo_sink_action_read_data
} t_fifo_sink_action;

/*t t_fifo_sink_ctrl
 *
 * Control of the Fifo sink
 */
typedef struct {
    t_fifo_sink_action action;
    bit set_counts;
    bit[6] byte_count;
    bit[16] word_count;
} t_fifo_sink_ctrl;

/*t t_fifo_sink_response
 *
 * Control of the Fifo sink
 */
typedef struct {
    bit valid;
    bit last_word;
    bit last_byte_of_word;
    bit empty;
    bit[3] bytes_valid;
    bit[32] data;
} t_fifo_sink_response;

