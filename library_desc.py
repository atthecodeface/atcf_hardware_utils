import cdl_desc
from cdl_desc import CdlModule, CModel

class Library(cdl_desc.Library):
    name="utils"
    pass

class DprintfModules(cdl_desc.Modules):
    name = "dprintf"
    c_src_dir   = "cmodel"
    src_dir     = "cdl"
    tb_src_dir  = "cdl_tb"
    include_dir = "cdl"
    libraries = {"std":True}
    export_dirs = [ src_dir, include_dir ]
    modules = []
    modules += [ CdlModule("async_reduce2_4_28_l",constants={"input_width":4,"output_width":28, "shift_right":0, "double_sr":1}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]
    modules += [ CdlModule("async_reduce2_4_28_r",constants={"input_width":4,"output_width":28, "shift_right":1, "double_sr":1}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]
    modules += [ CdlModule("async_reduce_4_28_l", constants={"input_width":4,"output_width":28, "shift_right":0, "double_sr":0}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]
    modules += [ CdlModule("async_reduce_4_28_r", constants={"input_width":4,"output_width":28, "shift_right":1, "double_sr":0}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]
    modules += [ CdlModule("async_reduce_4_60_l", constants={"input_width":4,"output_width":60, "shift_right":0, "double_sr":0}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]
    modules += [ CdlModule("async_reduce_4_60_r", constants={"input_width":4,"output_width":60, "shift_right":1, "double_sr":0}, cdl_filename="generic_async_reduce", cdl_module_name="generic_async_reduce") ]

    modules += [ CdlModule("dprintf") ]
    modules += [ CdlModule("hysteresis_switch") ]
    modules += [ CdlModule("clock_divider") ]
    modules += [ CdlModule("tech_sync_flop") ]
    modules += [ CdlModule("tech_sync_bit") ]

    modules += [ CdlModule("dprintf_2_mux",      force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_2"}, cdl_filename="generic_valid_ack_mux", cdl_module_name="generic_valid_ack_mux") ]
    modules += [ CdlModule("dprintf_4_mux",      force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_4"}, cdl_filename="generic_valid_ack_mux", cdl_module_name="generic_valid_ack_mux") ]
    modules += [ CdlModule("dprintf_2_fifo_4",   force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_2"}, constants={"fifo_depth":3}, cdl_filename="generic_valid_ack_fifo", cdl_module_name="generic_valid_ack_fifo") ]
    modules += [ CdlModule("dprintf_4_fifo_4",   force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_4"}, constants={"fifo_depth":3}, cdl_filename="generic_valid_ack_fifo", cdl_module_name="generic_valid_ack_fifo") ]
    modules += [ CdlModule("dprintf_4_async",    force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_4"}, cdl_filename="generic_valid_ack_async_slow", cdl_module_name="generic_valid_ack_async_slow") ]
    modules += [ CdlModule("dprintf_4_fifo_512", force_includes=["dprintf.h"], types={"gt_generic_valid_req":"t_dprintf_req_4"}, constants={"fifo_depth":512}, instance_types={"generic_valid_ack_dpsram":"dprintf_4_dp_sram_512"}, cdl_filename="generic_valid_ack_sram_fifo", cdl_module_name="generic_valid_ack_sram_fifo") ]

    modules += [ CdlModule("tb_dprintf", src_dir=tb_src_dir) ]
    modules += [ CdlModule("tb_dprintf_mux", src_dir=tb_src_dir) ]
    modules += [ CdlModule("tb_hysteresis_switch", src_dir=tb_src_dir) ]

    pass
