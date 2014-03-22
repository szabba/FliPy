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

    def __init__(self, size):

        super(Board, self).__init__()

        self.__size = size

        self.__board = [
                [True for i in range(size)]
                for i in range(size)]

        self.mess_up()

    def mess_up(self):
        """B.mess_up()

        Randomly swaps columns and rows around.
        """

        for row in range(self.size()):

            if random.choice([True, False]):

                self.swap_row(row)

            if random.choice([True, False]):

                self.swap_diagonal()

        for column in range(self.size()):

            if random.choice([True, False]):

                self.swap_column(column)

            if random.choice([True, False]):

                self.swap_diagonal()


    def swap_column(self, j):
        """B.swap_column(j)

        Swaps the values in the j-th column.
        """

        for i in range(self.__size):

            self.__board[i][j] = not self.__board[i][j]

            self.flipped.emit(i, j)

        self.signal_if_solved()

    def swap_row(self, i):
        """B.swap_row(i)

        Swap the values in the i-th row.
        """

        for j in range(self.__size):

            self.__board[i][j] = not self.__board[i][j]

            self.flipped.emit(i, j)

        self.signal_if_solved()

    def swap_diagonal(self):
        """B.swap_diagonal()

        Swap the values on the rising diagonal
        """

        for i in range (self.__size):
            j = self.__size - i - 1

            self.__board[i][j] = not self.__board[i][j]

            self.flipped.emit(i, j)

        self.signal_if_solved()

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

    def signal_if_solved(self):
        """B.signal_if_solved()

        Signal if the board has been solved.
        """

        if all(map(all, self.__board)):

            self.solved.emit()

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


class DiagonalFlipper(QtGui.QPushButton):
    """A button that flips the board's rising diagonal"""

    def __init__(self, board, parent=None):

        super(DiagonalFlipper, self).__init__('Flip', parent)

        self.__board = board

        self.clicked.connect(self.flip)

    def flip(self):
        """RF.flip()

        Flips the appropriate column.
        """

        self.__board.swap_diagonal()


class GameScreen(QtGui.QWidget):
    """A game screen"""

    def __init__(self, board_size, anchor):

        super(GameScreen, self).__init__()

        grid = QtGui.QGridLayout()

        board = self.__board = Board(board_size)
        self.__board.solved.connect(self.onSolved)

        for row in range(board_size):

            grid.addWidget(RowFlipper(board, row), row, 0)

            for column in range(board_size):

                grid.addWidget(BoxWidget(board, (row, column)), row, column + 1)

        grid.addWidget(DiagonalFlipper(board), board_size, 0)

        for column in range(board_size):

            grid.addWidget(ColumnFlipper(board, column), board_size, column + 1)

        self.__anchor = anchor
        anchor.anchor(self)

        self.setLayout(grid)
        self.show()

    def onSolved(self):
        """GS.onSolved()

        React to the board being solved.
        """

        NewGame(self.__anchor, self.__board.size())

        self.destroy()


class NewGame(QtGui.QWidget):
    """A new game screen"""

    MIN_SIZE = 3
    MAX_SIZE = 7

    def __init__(self, anchor, init_size=MIN_SIZE):

        super(NewGame, self).__init__()

        box = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)

        box.addWidget(QtGui.QLabel('What size should the board be?'))

        slider = self.__slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setValue(init_size)
        slider.setRange(NewGame.MIN_SIZE, NewGame.MAX_SIZE)

        box.addWidget(slider)

        button = QtGui.QPushButton('Start!')
        button.clicked.connect(self.start)

        box.addWidget(button)

        self.__anchor = anchor
        anchor.anchor(self)

        self.setLayout(box)
        self.show()

    def start(self):
        """NG.start()

        Starts a new game.
        """

        GameScreen(
                self.__slider.value(),
                self.__anchor)

        self.destroy()


class Anchor(object):
    """Keeps a reference to the current window, so it doesn't get garbage
    collected. This helps prevent a segfault.

    PyQt memory managment is complicated.
    """

    def anchor(self, v):
        """A.anchor(v)

        Change the value being anchored.
        """

        self.__v = v


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    anchor = Anchor()
    NewGame(anchor)

    sys.exit(app.exec_())
