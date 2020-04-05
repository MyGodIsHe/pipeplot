#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import collections
import curses
import errno
import fcntl
import itertools
import locale
import os
import sys
import time


__version__ = '0.3.3'


class CursesContext:
    def __init__(self):
        self.stdscr = None

    def __enter__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        self.stdscr.leaveok(False)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self.stdscr = None

    def get_symbol_size(self, symbol):
        curses.curs_set(2)
        curses.setsyx(0, 0)
        self.stdscr.addstr(symbol)
        self.stdscr.refresh()
        curses.curs_set(0)
        return curses.getsyx()[1]


class PlotWidget:
    STATS_FLOAT_FORMAT = r'{:6.2f}'
    STATS_INT_FORMAT = r'{:6d}'

    def __init__(
            self,
            stdscr,
            color,
            symbol,
            symbol_size,
            scale,
            fixed_min,
            fixed_max,
            direction,
    ):
        self.stdscr = stdscr
        self._queue = collections.deque(maxlen=1000)
        self.color = curses.color_pair(color)
        self.symbol = symbol
        self.symbol_size = symbol_size
        self.scale = scale
        self.min_value = None
        self.max_value = None
        self.fixed_min = fixed_min
        self.fixed_max = fixed_max
        self.is_natural = True
        self.direction = direction

    def append(self, value):
        if self.is_natural:
            self.is_natural = value % 1 == 0.0
        if self.min_value is None:
            self.min_value = self.max_value = value
        else:
            if self.min_value > value:
                self.min_value = value
            elif self.max_value < value:
                self.max_value = value
        self._queue.appendleft(value)

    def draw(self, width, height):
        if not width or not height:
            return
        values = list(itertools.islice(self._queue, 0, width))
        if not values:
            return
        current_value = values[0]

        if self.scale == 'window':
            min_value, max_value = min(values), max(values)
        else:
            min_value, max_value = self.min_value, self.max_value

        self.add_plot(values, width, height, min_value, max_value)
        self.add_stats(width, height, min_value, current_value, max_value)
        self.stdscr.refresh()

    def add_plot(self, values, width, height, min_value, max_value):
        if self.fixed_min is not None:
            min_value = self.fixed_min
        if self.fixed_max is not None:
            max_value = self.fixed_max

        if max_value == min_value:
            # draw middle value
            height_k = height
            values = [0.5] * len(values)
        else:
            height_k = height / (max_value - min_value)

        for x, value in enumerate(values):
            x *= self.symbol_size
            if self.direction == 'left':
                x = width - x
            value = int((value - min_value) * height_k)
            value = height - value
            for y in range(0, value):
                self.clear_char(x, y)
            for y in range(value, height + 1):
                self.add_str(x, y, self.symbol, self.color)

    def add_stats(self, width, height, min_value, current_value, max_value):
        if self.is_natural:
            stats_format = self.STATS_INT_FORMAT
            max_value = int(max_value)
            current_value = int(current_value)
            min_value = int(min_value)
        else:
            stats_format = self.STATS_FLOAT_FORMAT
        stats_box = [
            ('Max: ' + stats_format).format(max_value),
            ('Cur: ' + stats_format).format(current_value),
            ('Min: ' + stats_format).format(min_value),
        ]
        offset_x = int((width - max(len(line) for line in stats_box)) / 2)
        offset_y = int((height - len(stats_box)) / 2)
        for y, line in enumerate(stats_box):
            self.add_str(offset_x, offset_y + y, line, curses.color_pair(0))

    def clear_char(self, x, y):
        try:
            self.stdscr.addstr(y, x, ' ' * self.symbol_size)
        except curses.error:
            pass

    def add_str(self, x, y, char, color):
        try:
            self.stdscr.addstr(y, x, char, color)
        except curses.error:
            pass


def perfect_symbol(char):
    if not char:
        raise argparse.ArgumentTypeError('not empty')
    return char


def parse_args():
    parser = argparse.ArgumentParser(
        description='Displays a graph based on data from the pipe.'
    )
    parser.add_argument('--color', default=2, type=int)
    parser.add_argument('--symbol', default='█', type=perfect_symbol)
    parser.add_argument('--scale', default='all', choices=['all', 'window'])
    parser.add_argument(
        '--direction', default='right', choices=['left', 'right'],
    )
    parser.add_argument('--min', type=float)
    parser.add_argument('--max', type=float)
    return parser.parse_args()


def stdin_iter_py2():
    while True:
        try:
            line = sys.stdin.readline().strip()
        except IOError as exc:
            if exc.errno == errno.EAGAIN:
                time.sleep(0.1)
                continue
            raise
        if not line:
            break
        value = float(line)
        yield value
        time.sleep(0.1)


def stdin_iter_py3():
    while True:
        line = sys.stdin.readline().strip()
        if line:
            value = float(line)
            yield value
        time.sleep(0.1)


def main(args):
    # init non-blocking stdin
    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    with CursesContext() as curses_context:
        symbol_size = curses_context.get_symbol_size(args.symbol)
        plot = PlotWidget(
            curses_context.stdscr,
            args.color,
            args.symbol,
            symbol_size,
            args.scale,
            args.min,
            args.max,
            args.direction,
        )

        if sys.version_info.major == 2:
            std_iter = stdin_iter_py2
        else:
            std_iter = stdin_iter_py3

        for value in std_iter():
            plot.append(value)
            max_y, max_x = curses_context.stdscr.getmaxyx()
            plot.draw(max_x, max_y)


def run():
    locale.setlocale(locale.LC_ALL, '')
    try:
        args = parse_args()
        main(args)
    except KeyboardInterrupt:
        pass
    except ValueError as exc:
        print('Stdin error: {}'.format(exc))
