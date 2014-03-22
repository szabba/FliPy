#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import sys
import random
import StringIO

from PyQt4 import QtGui, QtCore


class Board(QtCore.QObject):
    """The logical SwaPy board"""

    flipped = QtCore.pyqtSignal(int, int)
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

            self.flipped.emit(i, j)

    def swap_row(self, i):
        """B.swap_row(i)

        Swap the values in the i-th row.
        """

        for j in range(self.__size):

            self.__board[i][j] = not self.__board[i][j]

            self.flipped.emit(i, j)

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


class BoxWidget(QtGui.QWidget):
    """A single box widget."""

    ON_COLOR = QtGui.QColor(0, 255, 0)
    OFF_COLOR = QtGui.QColor(255, 0, 0)

    def __init__(self, board, pos, parent=None):

        super(BoxWidget, self).__init__()

        if parent is not None:

            self.setParent(parent)

        board.flipped.connect(self.onFlip)

        self.__board = board
        self.__pos = pos

    def draw(self):
        """BW.draw()

        Redisplays a single box.
        """

        qp = QtGui.QPainter()
        qp.begin(self)

        if self.__board.is_on(*self.__pos):

            color = BoxWidget.ON_COLOR

        else:

            color = BoxWidget.OFF_COLOR

        qp.setPen(color)
        qp.setBrush(color)

        qp.drawRect(0, 0, self.width(), self.height())

        qp.end()

    def paintEvent(self, e):
        """BW.paintEvent(e)

        Reacts to a Qt paint event.
        """

        self.draw()

    def onFlip(self, i, j):
        """Bw.onFlip(i, j)

        React to a board box being flipped.
        """

        if (i, j) == self.__pos:

            self.repaint()


class RowFlipper(QtGui.QPushButton):
    """A button that flips a board's row"""

    def __init__(self, board, row_no, parent=None):

        super(RowFlipper, self).__init__('Flip', parent)

        self.__board = board
        self.__row_no = row_no

        self.clicked.connect(self.flip)

    def flip(self):
        """RF.flip()

        Flips the appropriate row.
        """

        self.__board.swap_row(self.__row_no)


class ColumnFlipper(QtGui.QPushButton):
    """A button that flips a board's column"""

    def __init__(self, board, column_no, parent=None):

        super(ColumnFlipper, self).__init__('Flip', parent)

        self.__board = board
        self.__column_no = column_no

        self.clicked.connect(self.flip)

    def flip(self):
        """RF.flip()

        Flips the appropriate column.
        """

        self.__board.swap_column(self.__column_no)


class GameScreen(QtGui.QWidget):
    """A game screen"""

    def __init__(self, board_size, how_messy, parent=None):

        super(GameScreen, self).__init__()

        if parent is not None:

            self.setParent(parent)

        grid = QtGui.QGridLayout()

        board = Board(board_size, how_messy)

        for row in range(board_size):

            grid.addWidget(RowFlipper(board, row), row, 0)

            for column in range(board_size):

                grid.addWidget(BoxWidget(board, (row, column)), row, column + 1)

        for column in range(board_size):

            grid.addWidget(ColumnFlipper(board, column), board_size, column + 1)

        self.setLayout(grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    gs = GameScreen(5, 3)
    gs.show()

    sys.exit(app.exec_())
