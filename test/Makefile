smoke:
	${SIM} smoke.csm

smoke_mifs: smoke_rom.py
	PYTHONPATH=.:${PYTHONPATH} apb_processor_rom.py --src smoke_rom --mif smoke_rom.mif
