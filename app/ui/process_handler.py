from app.ui.process_base_handler import ProcessBaseHandler
from app.ui.data_process_handler import DataProcessHandler
from app.ui.lithology_handler import LithologyHandler
from app.ui.alteration_handler import AlterationHandler


class ProcessHandler(
    ProcessBaseHandler,
    DataProcessHandler,
    LithologyHandler,
    AlterationHandler
):
    def __init__(self, main_window):
        ProcessBaseHandler.__init__(self, main_window)
        DataProcessHandler.__init__(self, main_window)
        LithologyHandler.__init__(self, main_window)
        AlterationHandler.__init__(self, main_window)
