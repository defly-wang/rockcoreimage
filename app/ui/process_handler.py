from app.ui.process_base_handler import ProcessBaseHandler
from app.ui.data_process_handler import DataProcessHandler
from app.ui.lithology_handler import LithologyHandler


class ProcessHandler(
    ProcessBaseHandler,
    DataProcessHandler,
    LithologyHandler
):
    def __init__(self, main_window):
        ProcessBaseHandler.__init__(self, main_window)
        DataProcessHandler.__init__(self, main_window)
        LithologyHandler.__init__(self, main_window)
