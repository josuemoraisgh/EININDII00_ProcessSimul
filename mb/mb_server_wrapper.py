
from __future__ import annotations

class ModbusHartController:
    """Liga/desliga HART junto com seu servidor Modbus."""
    def __init__(self, server, hart_link):
        self.server = server
        self.hart = hart_link

    @property
    def running(self) -> bool:
        srun = getattr(self.server, "running", False)
        hrun = getattr(self.hart, "running", False)
        return bool(srun and hrun)

    def start(self, modbus_port=None, hart_port=None, **kwargs):
        started = False
        try:
            self.server.start(port=modbus_port, **kwargs)
            started = True
        except TypeError:
            self.server.start(modbus_port=modbus_port, **kwargs)
            started = True
        self.hart.open(hart_port)
        return started and self.hart.running

    def stop(self):
        try:
            self.server.stop()
        finally:
            self.hart.close()
