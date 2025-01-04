t_fifo_status  = {
    "pushed":1,
    "popped":1,
    "empty":1,
    "full":1,
    "overflowed":1,
    "underflowed":1,
    "entries_full":32,
    "spaces_available":32,
    }
class FifoStatus:
    def __init__(self, size, num, overflowed=False, underflowed=False):
        self.size = size
        self.entries_full = num
        self.overflowed = overflowed
        self.underflowed = underflowed
        self.derive()
        pass
    def derive(self):
        self.spaces_available = self.size - self.entries_full
        self.empty = self.entries_full == 0
        self.full = self.entries_full == self.size
        pass        
    def as_dbg_master_fifo_status(self) -> int:
        r = 0
        if self.empty: r += 1
        if self.full: r += 2
        if self.underflowed: r += 4
        if self.overflowed: r += 8
        if self.entries_full > 0x3fff:
            r += 0x3fff << 4
            pass
        else:
            r += (self.entries_full & 0x3fff) << 4
            pass
        if self.spaces_available > 0x3fff:
            r += 0x3fff << 18
            pass
        else:
            r += (self.spaces_available & 0x3fff) << 18
            pass
        return r
    def push(self):
        if self.full:
            self.overflowed = True
            return False
            pass
        self.entries_full += 1
        self.derive()
        return True
    def pop(self):
        if self.empty:
            self.underflowed = True
            return False
        self.entries_full -= 1
        self.derive()
        return True
    pass
        
