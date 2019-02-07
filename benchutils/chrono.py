import time

from benchutils.statstream import StatStream
from benchutils.report import print_table

from typing import List
from typing import Callable


def chrono(func: Callable):
    def chrono_decorator(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        t = time.time() - start
        print('{:>30} ran in {:10.4f} s'.format(func.__name__, t))
        return value
    return chrono_decorator


class MultiStageChrono:
    def __init__(self, stages: List[str], drop=10):
        self.names = stages
        self.stages = [StatStream(drop) for _ in stages]

        self.current_stage = 0
        self.start_time = 0
        self.end_time = 0
        self.total_s = 0
        self.total = StatStream(drop)

    def start(self, name=None):
        if self.start_time == 0:
            if name is not None:
                assert self.names[self.current_stage] == name

            self.start_time = time.time()
            self.total_s = self.start_time
        else:
            self.end_time = time.time()
            self.stages[self.current_stage] += (self.end_time - self.start_time)
            self.start_time = self.end_time
            self.current_stage += 1

            if name is not None:
                assert self.names[self.current_stage] == name

    def end(self):
        self.end_time = time.time()
        self.stages[self.current_stage] += (self.end_time - self.start_time)
        self.total += self.end_time - self.total_s
        self.current_stage = 0
        self.start_time = 0

    def make_table(self, common: List = None, transform=None):
        common = common or []
        table = []

        for i, stream in enumerate(self.stages):
            table.append([self.names[i]] + stream.to_array(transform) + common)

        table.append(['Total'] + self.total.to_array(transform) + common)
        return table

    def report(self, speed=False, size=1):
        header = ['Stage', 'Average', 'Deviation', 'Min', 'Max', 'count']
        table = self.make_table(None, lambda x: size / x) if speed else self.make_table()
        print_table(header, table)


if __name__ == '__main__':

    a = MultiStageChrono(['start', 'end'])

    a.start('start')

    a.start('end')

    a.end()
