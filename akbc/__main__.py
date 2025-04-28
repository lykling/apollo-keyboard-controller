#!/usr/bin/env python
"""apollo keyboard controller
"""
import click
import curses
import signal
import traceback
import threading
from akbc import simple_vehicle
from akbc import keyboard_controller
from akbc import screen
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
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    scr = screen.Screen(stdscr)

    cyber.init()

    controller = keyboard_controller.KeyboardController(
        scr, kwargs['dbc_file'], kwargs['device'])
    vehicle = None
    if kwargs['enable_virtual_vehicle']:
        vehicle = simple_vehicle.SimpleVehicle(scr, kwargs['dbc_file'],
                                               kwargs['device'],
                                               kwargs['initial_x'],
                                               kwargs['initial_y'])

    threads = []
    screen_thread = threading.Thread(target=scr.run, name='screen')
    threads.append(screen_thread)
    controller_thread = threading.Thread(target=controller.run,
                                         name='controller')
    threads.append(controller_thread)
    if vehicle:
        vehicle_thread = threading.Thread(target=vehicle.run, name='vehicle')
        threads.append(vehicle_thread)

    def _exit_screen(_):
        """_exit_curses
        """
        scr.shutdown()
        controller.shutdown()
        if vehicle:
            vehicle.shutdown()
        cyber.shutdown()

    scr.on(ord('q'), _exit_screen)

    def _signal_handler(sig, frame):
        """signal_handler
        """
        print('exiting...', sig)
        exit_signals = [signal.SIGINT, signal.SIGTERM]
        if sig in exit_signals:
            scr.shutdown()
            controller.shutdown()
            if vehicle:
                vehicle.shutdown()
            cyber.shutdown()
        else:
            # unhandled signal
            print(f'Unhandled signal: {sig}', traceback.print_stack(frame))

    # register signal handlers
    signal.signal(signal.SIGINT, _signal_handler)

    for thread in threads:
        thread.start()

    # for thread in threads:
    #     thread.join()
    screen_thread.join()


if __name__ == '__main__':
    main()
