from PySide6.QtWidgets import QSpinBox
from simulation.config import load_config


def setup_elevator_table(table, num_elevators: int):
    table.setRowCount(num_elevators)
    for row in range(num_elevators):
        spin_max = QSpinBox()
        spin_max.setRange(1, 20)
        spin_max.setValue(5)
        table.setCellWidget(row, 0, spin_max)

        spin_speed = QSpinBox()
        spin_speed.setRange(1, 30)
        spin_speed.setValue(5)
        table.setCellWidget(row, 1, spin_speed)

        spin_starting = QSpinBox()
        spin_starting.setRange(0, load_config().floors)
        spin_starting.setValue(0)
        table.setCellWidget(row, 2, spin_starting)
