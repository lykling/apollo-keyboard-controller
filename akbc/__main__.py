#!/usr/bin/env python
"""apollo keyboard controller
"""
import click
import signal
import traceback
from akbc import simple_vehicle
from cyber.python.cyber_py3 import cyber


@click.command()
@click.option('--enable_virtual_vehicle', is_flag=True, default=False)
@click.option('--dbc_file', default='./vehicle.dbc', type=str, help='dbc file')
@click.option('--device', default='can0', type=str, help='can device')
@click.option('--initial_x', default=587392.0, type=float, help='initial x')
@click.option('--initial_y', default=4140800.0, type=float, help='initial y')
def main(**kwargs):
    """main entry
    """
    cyber.init()

    vehicle = None
    if kwargs['enable_virtual_vehicle']:
        vehicle = simple_vehicle.SimpleVehicle(kwargs['dbc_file'],
                                               kwargs['device'],
                                               kwargs['initial_x'],
                                               kwargs['initial_y'])

    def _signal_handler(sig, frame):
        """signal_handler
        """
        print('exiting...')
        exit_signals = [signal.SIGINT, signal.SIGTERM]
        if sig in exit_signals:
            if vehicle:
                vehicle.shutdown()
            cyber.shutdown()
        else:
            # unhandled signal
            print(f'Unhandled signal: {sig}', traceback.print_stack(frame))

    # register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)

    if vehicle:
        vehicle.run()


if __name__ == '__main__':
    main()
