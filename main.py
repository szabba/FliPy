#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import sys
import random
import StringIO

from PyQt4 import QtGui, QtCore


class Board(QtCore.QObject):
    """The logical SwaPy board"""

    stateChanged = QtCore.pyqtSignal()
    solved = QtCore.pyqtSignal()

    def __init__(self, size, mess):

        super(Board, self).__init__()

        self.__size = size

        self.__board = [
                [True for i in range(size)]
                for i in range(size)]

        self.__signal_when_solved = False

        self.mess_up(mess)

        self.__signal_when_solved = True

    def mess_up(self, how_much):
        """B.mess_up(how_much)

        Randomly swaps columns and rows around.
        """

        for _ in range(how_much):

            column = random.choice([True, False])
            which = random.randint(0, self.__size - 1)

            if column:

                self.swap_column(which)

            else:

                self.swap_row(which)


    def swap_column(self, j):
        """B.swap_column(j)

        Swaps the values in the j-th column.
        """

        for i in range(self.__size):

            self.__board[i][j] = not self.__board[i][j]

        if self.__signal_when_solved:

            if all(map(all, self.__board)):

                self.solved.emit()

    def swap_row(self, i):
        """B.swap_row(i)

        Swap the values in the i-th row.
        """

        for j in range(self.__size):

            self.__board[i][j] = not self.__board[i][j]

        if self.__signal_when_solved:

            if all(map(all, self.__board)):

                self.solved.emit()

    def size(self):
        """B.size() -> board size

        Board are always square.
        """

        return self.__size

    def is_on(self, i, j):
        """B.is_on(i, j) -> bool

        Tells whether the (i, j)-th box on the board is on or off.
        """

        return self.__board[i][j]

    def __str__(self):

        out = StringIO.StringIO()

        for row in self.__board:
            for box in row:

                if box:
                    out.write('#')

                else:
                    out.write('_')

            out.write('\n')

        return out.getvalue()


class BoardWidget(QtGui.QWidget):
    """A Qt widget displaying a board."""

    ON_COLOR = QtGui.QColor(0, 255, 0)
    OFF_COLOR = QtGui.QColor(255, 0, 0)
    MIN_BOX_SIZE = 60

    def __init__(self, board, parent=None):

        super(BoardWidget, self).__init__()

        if parent is not None:

            self.setParent(parent)

        else:

            self.resize(
                    BoardWidget.MIN_BOX_SIZE * board.size(),
                    BoardWidget.MIN_BOX_SIZE * board.size())

        board.stateChanged.connect(self.draw)
        self.__board = board

    def draw(self):
        """BW.draw()

        Draws the board in a widget.
        """

        box_width = self.width() / self.__board.size()
        box_height = self.height() / self.__board.size()

        qp = QtGui.QPainter()
        qp.begin(self)

        for i in range(self.__board.size()):
            for j in range(self.__board.size()):

                if self.__board.is_on(i, j):

                    color = BoardWidget.ON_COLOR

                else:

                    color = BoardWidget.OFF_COLOR

                qp.setPen(color)
                qp.setBrush(color)

                qp.drawRect(
                        i * box_width,
                        j * box_height,
                        box_width,
                        box_height)

        qp.end()

    def paintEvent(self, e):
        """BW.paintEvent(e)

        Reacts to a Qt paint event.
        """

        self.draw()


if __name__ == '__main__':

    b = Board(5, 3)

    app = QtGui.QApplication(sys.argv)

    bw = BoardWidget(b)
    bw.show()

    sys.exit(app.exec_())
