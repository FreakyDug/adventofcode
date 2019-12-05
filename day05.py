import dataclasses
import operator
from typing import List

from aocd.models import Puzzle

from util import inspect


class Halt(Exception):
    pass


@dataclasses.dataclass()
class Computer:
    """
    >>> Computer([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50]).run().mem
    [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]
    >>> Computer([1, 0, 0, 0, 99]).run().mem
    [2, 0, 0, 0, 99]
    >>> Computer([2, 3, 0, 3, 99]).run().mem
    [2, 3, 0, 6, 99]
    >>> Computer([2, 4, 4, 5, 99, 0]).run().mem
    [2, 4, 4, 5, 99, 9801]
    >>> Computer([1, 1, 1, 4, 99, 5, 6, 0, 99]).run().mem
    [30, 1, 1, 4, 2, 5, 6, 0, 99]
    >>> Computer([3,0,4,0,99]).run().output
    1
    >>> Computer([3,9,8,9,10,9,4,9,99,-1,8]).run(inp=8).output
    1
    >>> Computer([3,9,8,9,10,9,4,9,99,-1,8]).run(inp=5).output
    0
    """
    mem: List[int]
    pc: int = 0

    def add(self, param1, param2, dest):
        self.write(self.read(*param1) + self.read(*param2), *dest)

    def mul(self, param1, param2, dest):
        self.write(self.read(*param1) * self.read(*param2), *dest)

    def store(self, dest):
        self.write(self._input, *dest)

    def out(self, param):
        self._output = self.read(*param)

    def jump_if_true(self, param1, param2):
        if self.read(*param1):
            self.pc = self.read(*param2)

    def jump_if_false(self, param1, param2):
        if not self.read(*param1):
            self.pc = self.read(*param2)

    def less_than(self, param1, param2, dest):
        self.write(1 if self.read(*param1) < self.read(*param2) else 0, *dest)

    def equals(self, param1, param2, dest):
        self.write(1 if self.read(*param1) == self.read(*param2) else 0, *dest)

    _input = 1
    _output = None

    _opcodes = {
        1: (add, 4),
        2: (mul, 4),
        3: (store, 2),
        4: (out, 2),
        5: (jump_if_true, 3),
        6: (jump_if_false, 3),
        7: (less_than, 4),
        8: (equals, 4),
    }

    def __post_init__(self):
        self.mem = self.mem.copy()

    @staticmethod
    def parse_op(opcode):
        """
        >>> Computer.parse_op(1002)
        (2, (0, 1, 0))
        """
        bits = str(opcode).rjust(5, '0')
        op = int(bits[-2:])
        return (op, tuple(int(mode) for mode in reversed(bits[0:3])))

    def write(self, value, param, mode):
        assert mode == 0
        self[param] = value

    def read(self, param, mode):
        if mode == 0:
            return self[param]
        elif mode == 1:
            return param
        else:
            raise Exception(f"Unknown mode: {mode}")

    def run(self, noun=None, verb=None, inp=None):
        if noun is not None:
            self[1] = noun
        if verb is not None:
            self[2] = verb
        if inp is not None:
            self._input = inp

        last_op = None

        while (opcode := self.mem[self.pc]) != 99:
            if self._output not in [0, None]:
                raise Exception(f"Test program failed on op: {last_op}")
            op, modes = self.parse_op(opcode)
            last_op = op
            try:
                op, param_num = self._opcodes[op]
            except KeyError:
                raise Exception(f"Unknown opcode {opcode} at pc {self.pc}")
            params = zip(self.mem[self.pc + 1:self.pc + param_num], modes)
            pc_before = self.pc
            op(self, *params)
            if pc_before == self.pc:
                self.pc += param_num
        return self

    def __getitem__(self, key):
        return self.mem[key]

    def __setitem__(self, key, value):
        self.mem[key] = value

    @property
    def output(self):
        if self._output is not None:
            return self._output
        return self[0]


def part1(program):
    return Computer(program).run().output


def part2(program):
    return Computer(program).run(inp=5).output


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    puzzle = Puzzle(year=2019, day=5)
    program = [int(val) for val in puzzle.input_data.split(',')]
    puzzle.answer_a = inspect(part1(program), prefix='Part 1: ')
    puzzle.answer_b = inspect(part2(program), prefix='Part 2: ')
