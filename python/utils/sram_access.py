#s Structs
t_sram_access_req  = {"valid":1, "id":8, "read_not_write":1, "byte_enable":8, "address":32, "write_data":64}
t_sram_access_resp = {"valid":1, "id":8, "ack":1, "data":64}

#a Bus driver
class SramAccessBus:
    def __init__(self, obj, req_name:str, rsp_name:str):
        self.valid = getattr(obj, req_name+"__valid")
        self.req_id = getattr(obj, req_name+"__id")
        self.rnw = getattr(obj, req_name+"__read_not_write")
        self.address = getattr(obj, req_name+"__address")
        self.byte_enable = getattr(obj, req_name+"__byte_enable")
        self.write_data = getattr(obj, req_name+"__write_data")
        self.ack = getattr(obj, rsp_name+"__ack")
        self.rd_valid = getattr(obj, rsp_name+"__valid")
        self.rd_data = getattr(obj, rsp_name+"__data")
        self.rd_id = getattr(obj, rsp_name+"__id")
        pass
    def invalid(self):
        self.valid.drive(0)
        pass
    def drive(self, d):
        self.valid.drive(1)
        self.address.drive(d.address)
        self.req_id.drive(d.id)
        self.rnw.drive(d.read_not_write)
        self.address.drive(d.address)
        self.byte_enable.drive(d.byte_enable)
        self.write_data.drive(d.write_data)
        pass
    def is_acked(self) -> bool:
        return self.ack.value() == 1
    pass

#c SramAccess
class SramAccess:
    id: int
    address: int
    byte_enable: int
    write_data: bytes
    read_not_write : int
    def __init__(self, id:int, address:int, write_data:int, byte_enable:int, read_not_write:bool):
        self.address = address
        self.id = id
        self.write_data = write_data
        self.byte_enable = byte_enable
        self.read_not_write = read_not_write + 0
        pass
    pass

class SramAccessWrite(SramAccess):
    def __init__(self, id:int, address:int, write_data:int, byte_enable:int):
        super().__init__(id, address, write_data, byte_enable, read_not_write=False)
        pass
    pass

class SramAccessRead(SramAccess):
    def __init__(self, id:int, address:int):
        super().__init__(id, address, write_data=0, byte_enable=0, read_not_write=True)
        pass
    pass
