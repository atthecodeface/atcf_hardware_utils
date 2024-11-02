
#t t_dbg_master_op
t_dbg_master_op = {
    "dbg_op_idle":0,
    "dbg_op_start":1,
    "dbg_op_start_clear":2,
    "dbg_op_data":3,
    "dbg_op_data_last":4,
} 

# t_dbg_master_resp_type
t_dbg_master_resp_type = {
    "dbg_resp_idle":0,
    "dbg_resp_running":1,
    "dbg_resp_completed":2,
    "dbg_resp_poll_failed":3,
    "dbg_resp_errored":4,
}

# t_dbg_master_request
t_dbg_master_request = {
    "op": 3, # t_dbg_master_op
    "num_data_valid": 4, # Number of bytes valid, 0 to 6, in data; ignored if not an op data
    "data":64,
} 

# t_dbg_master_response
t_dbg_master_response  = {
    "resp_type":3,
    "bytes_consumed":4, # If non-zero then remove the bottom bytes from the data request in the next cycle; data is never consumed in back-to-back cycles, and this will be zero for one cycle after it is nonzero";
    "bytes_valid":3, # // 1, 2, or 3 for 32-bit; 0 for no valid data
    "data":32,
}

#a Bus driver
class DbgMasterFifoScript:
    def __init__(self, ops):
        self.ops = ops
        pass
    def as_bytes(self) -> bytes:
        r = bytearray()
        for op in self.ops:
            if op == "status": # Read fifo status
                r.append(0)
                pass
            elif op[0] == "read":
                r.append(64 + (op[1]//8-1))
                r.append((op[2]-1) &0xff)
                r.append(((op[2]-1)>>8) &0xff)
                pass
            elif op[0] == "read_err":
                r.append(128 + (op[1]//8-1))
                r.append((op[2]-1) &0xff)
                r.append(((op[2]-1)>>8) &0xff)
                pass
            pass
        return r
    pass
#a Bus driver
class DbgMaster:
    def __init__(self, obj, req_name:str, resp_name:str):
        self.resp_type = getattr(obj, resp_name+"__resp_type")
        self.resp_data = getattr(obj, resp_name+"__data")
        self.resp_bytes_valid = getattr(obj, resp_name+"__bytes_valid")
        self.resp_bytes_consumed = getattr(obj, resp_name+"__bytes_consumed")
        self.req_op = getattr(obj, req_name+"__op")
        self.req_num_data_valid = getattr(obj, req_name+"__num_data_valid")
        self.req_data = getattr(obj, req_name+"__data")
        pass
    #f invoke_script_bytes
    def invoke_script_bytes(self, bytes_to_run:bytes, bfm_wait, inter_data_idle, cycles_to_run:int=1000):
        bytes_to_run = bytearray(bytes_to_run)
        if (self.resp_type.value() != t_dbg_master_resp_type["dbg_resp_idle"]):
            return ("Not idle", [])

        self.req_num_data_valid.drive(0)
        self.req_op.drive(t_dbg_master_op["dbg_op_start_clear"] )
        bfm_wait(1)
        self.req_op.drive(t_dbg_master_op["dbg_op_idle"] )
        bfm_wait(1)
        completion = "ok"
        data_returned = []
        do_idle_cnt = inter_data_idle()
        while cycles_to_run > 0:
            bv = self.resp_bytes_valid.value()
            data = self.resp_data.value()
            if bv == 1: data_returned.append(data&0xff)
            if bv == 2: data_returned.append(data&0xffff)
            if bv == 3: data_returned.append(data&0xffffff)
            if bv == 4: data_returned.append(data&0xffffffff)
            if self.resp_type.value() != t_dbg_master_resp_type["dbg_resp_running"]:
                break
            bytes_consumed = self.resp_bytes_consumed.value()
            for i in range(bytes_consumed):
                if len(bytes_to_run)>0:
                    bytes_to_run.pop(0)
                    pass
                do_idle_cnt = inter_data_idle()
                pass

            if do_idle_cnt > 0:
                self.req_op.drive(t_dbg_master_op["dbg_op_idle"] )
                self.req_data.drive(0xdeadbeef)
                self.req_num_data_valid.drive(do_idle_cnt&7)
                bfm_wait(1)
                do_idle_cnt -= 1
                continue
                pass

            n = len(bytes_to_run)
            self.req_op.drive(t_dbg_master_op["dbg_op_data"] )
            if n<=6:
                self.req_op.drive(t_dbg_master_op["dbg_op_data_last"] )
                pass
            else:
                n = 6
                pass
            data = 0
            for i in range(n):
                data = data | (bytes_to_run[i] << (8*i))
                pass
            self.req_data.drive(data)
            self.req_num_data_valid.drive(n)
            bfm_wait(1)
            cycles_to_run -= 1
            pass
        self.req_num_data_valid.drive(0)
        self.req_op.drive(t_dbg_master_op["dbg_op_idle"] )
        completion = "unexpected"
        if self.resp_type.value() == t_dbg_master_resp_type["dbg_resp_completed"]:
            completion = "ok"
            pass
        if self.resp_type.value() == t_dbg_master_resp_type["dbg_resp_errored"]:
            completion = "errored"
            pass
        if self.resp_type.value() == t_dbg_master_resp_type["dbg_resp_poll_failed"]:
            completion = "poll_failed"
            pass
        return (completion, data_returned)
