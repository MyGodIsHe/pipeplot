#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import collections
import curses
import fcntl
import itertools
import locale
import os
import sys
import time


__version__ = '0.1.4'


class CursesContext:
    def __init__(self):
        self.stdscr = None

    def __enter__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)
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
            self.stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self.stdscr = None


class PlotWidget:
    STATS_FLOAT_FORMAT = r'{:6.2f}'
    STATS_INT_FORMAT = r'{:6d}'

    def __init__(self, stdscr, color, symbol, border):
        self.stdscr = stdscr
        self._queue = collections.deque(maxlen=1000)
        self.color = curses.color_pair(color)
        self.symbol = symbol
        self.border = border
        self.min_value = None
        self.max_value = None
        self.is_natural = True

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

        if self.border == 'window':
            min_value, max_value = min(values), max(values)
        else:
            min_value, max_value = self.min_value, self.max_value

        if max_value == min_value:
            # draw middle value
            height_k = height
            values[0] += 0.5
        else:
            height_k = height / (max_value - min_value)

        self.add_plot(values, height, height_k, min_value)
        self.add_stats(width, height, min_value, current_value, max_value)

        self.stdscr.refresh()

    def add_plot(self, values, height, height_k, min_value):
        for x, value in enumerate(values):
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
            self.stdscr.addstr(y, x, ' ')
        except curses.error:
            pass

    def add_str(self, x, y, char, color):
        try:
            self.stdscr.addstr(y, x, char, color)
        except curses.error:
            pass


def perfect_symbol(char):
    code = locale.getpreferredencoding()
    try:
        decoded_char = char.decode(code)
    except AttributeError:
        decoded_char = char
    if len(decoded_char) != 1:
        raise argparse.ArgumentTypeError('only one')
    return char


def parse_args():
    parser = argparse.ArgumentParser(
        description='Displays a graph based on data from the pipe.'
    )
    parser.add_argument('--color', default=2, type=int)
    parser.add_argument('--symbol', default='█', type=perfect_symbol)
    parser.add_argument('--border', default='all', choices=['all', 'window'])
    return parser.parse_args()


def main(args):
    # init non-blocking stdin
    fd = sys.stdin.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    with CursesContext() as curses_context:
        plot = PlotWidget(
            curses_context.stdscr, args.color, args.symbol, args.border,
        )

        while True:
            try:
                line = sys.stdin.readline()
            except IOError as exc:
                if exc.errno == 11:
                    time.sleep(0.1)
                    continue
                raise
            if not line:
                time.sleep(0.1)
                continue
            value = float(line)
            plot.append(value)
            max_y, max_x = curses_context.stdscr.getmaxyx()
            plot.draw(max_x, max_y)
            time.sleep(0.1)


def run():
    locale.setlocale(locale.LC_ALL, '')
    try:
        args = parse_args()
        main(args)
    except KeyboardInterrupt:
        pass
    except ValueError as exc:
        print('Stdin error: {}'.format(exc))
