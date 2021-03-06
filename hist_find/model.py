from __future__ import absolute_import, print_function, unicode_literals
import itertools
import logging

from .utils import iter_unique, iter_matching_lines

logger = logging.getLogger(__name__)


class Model(object):

    class Action(object):
        EXECUTE = 'exec'
        FILL = 'fill'
        EDIT = 'edit'

    def __init__(self, lines, lines_capacity=0, search_string=''):
        self._lines = list(iter_unique(lines))
        self._search_chars = list(search_string)
        self._lines_capacity = lines_capacity
        self._action = None
        self._matching_lines = None
        self._clear_position()

    @property
    def search_string(self):
        return ''.join(self._search_chars)

    @property
    def matching_lines(self):
        if self._matching_lines is None:
            self._generate_matching_lines()
        return self._matching_lines

    @property
    def best_matching_line(self):
        position = self._position if self._position >= 0 else 0
        try:
            return self.matching_lines[position]
        except IndexError:
            return None

    @property
    def num_of_matching_lines(self):
        return len(self.matching_lines)

    def _generate_matching_lines(self):
        self._matching_lines = list(itertools.islice(
            iter_matching_lines(self._lines, self.search_string),
            self._lines_capacity,
        ))

    def _reset_matching_lines(self):
        self._matching_lines = None

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        if self._action is not None:
            raise ValueError('Action already set')
        self._action = action

    @property
    def lines_capacity(self):
        return self._lines_capacity

    @lines_capacity.setter
    def lines_capacity(self, lines_capacity):
        if self._lines_capacity == lines_capacity:
            return
        if self._position >= lines_capacity:
            self._clear_position()
        logger.debug('lines_capacity %s -> %s',
                     self._lines_capacity, lines_capacity)
        self._lines_capacity = lines_capacity
        self._reset_matching_lines()

    @property
    def position(self):
        return self._position

    def move_position_up(self):
        self._position += 1
        if self._position >= self.num_of_matching_lines:
            self._position = 0

    def move_position_down(self):
        self._position -= 1
        if self._position < 0:
            self._position = self.num_of_matching_lines - 1

    def remove_character(self):
        if self._search_chars:
            self._search_chars.pop()
        self._clear_position()
        self._reset_matching_lines()

    def append_character(self, c):
        self._search_chars.append(c)
        self._clear_position()
        self._reset_matching_lines()

    def _clear_position(self):
        self._position = -1
