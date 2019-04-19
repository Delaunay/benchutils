import time
import json

from benchutils.statstream import StatStream
from benchutils.report import print_table

from typing import List, Dict
from typing import Callable


def chrono(func: Callable):
    def chrono_decorator(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        t = time.time() - start
        print('{:>30} ran in {:10.4f} s'.format(func.__name__, t))
        return value
    return chrono_decorator


class _DummyContext:
    def __init__(self, **args):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ChronoContext:
    """
        sync is a function that can be set to make the timer wait before ending.
        This is useful when timing async calls like cuda calls
    """
    def __init__(self, name, stream: StatStream, sync: Callable, parent, verbose=False, endline='\n'):
        self.name = name
        self.stream = stream
        self.start = 0
        self.sync = sync
        self.parent = parent
        self.verbose = verbose
        self.newline = endline

    def __enter__(self):
        # Sync before starting timer to make sure previous work is not timed as well
        self.depth = self.parent.depth
        self.parent.depth += 1
        self.sync()

        if self.verbose:
            print(f'{" " * self.depth * 2} [{self.depth:3d}] >  {self.name}')

        self.start = time.time()
        return self.stream

    def __exit__(self, exception_type, exc_val, traceback):
        # Sync before ending timer to make sure all the work is accounted for
        self.sync()
        self.end = time.time()

        self.parent.depth -= 1
        if exception_type is None:
            self.stream.update(self.end - self.start)

        if self.verbose:
            print(
                f'{" " * self.depth * 2} [{self.depth:3d}] <  {self.name}: (obs: {self.stream.val:8.4f} s, '
                f'avg: {self.stream.avg:8.4f})',
                end=self.newline
            )


    @property
    def count(self):
        return self.stream.current_count


class MultiStageChrono:
    def __init__(self, skip_obs=10, sync=None, disabled=False, name=None):
        self.chronos = {}
        self.skip_obs = skip_obs
        self.sync = sync
        self.name = name
        self.disabled = disabled
        self.depth = 0
        if sync is None:
            self.sync = lambda: None

    def time(self, name, *args, skip_obs=None, **kwargs):
        if self.disabled:
            return _DummyContext()

        # if self.name is not None:
        #    name = '{}.{}'.format(self.name, name)

        val = self.chronos.get(name)

        if val is None:
            val = StatStream(self.skip_obs)
            if skip_obs is not None:
                val = StatStream(skip_obs)
            self.chronos[name] = val

        return ChronoContext(name, val, self.sync, self, *args, **kwargs)

    def make_table(self, common: List = None, transform=None):
        common = common or []
        table = []

        for i, (name, stream) in enumerate(self.chronos.items()):
            table.append([name] + stream.to_array(transform) + common)

        return table

    def report(self, speed=False, size=1, file_name=None, common: Dict[str, str] = None, skip_header=False):
        if self.disabled:
            return

        common = common or {}

        # split map in two
        items = list(common.items())

        common_header = list(map(lambda item: item[0], items))
        common = list(map(lambda item: item[1], items))

        header = ['Stage', 'Average', 'Deviation', 'Min', 'Max', 'count']
        header.extend(common_header)

        table = self.make_table(common, lambda x: size / x) if speed else self.make_table(common)
        print_table(header, table, file_name, skip_header)

    def to_dict(self, base=None):
        items = base
        if items is None:
            items = {}

        if self.name is not None:
            items['name'] = self.name

        for key, stream in self.chronos.items():
            items[key] = stream.to_dict()

        return items

    def to_json(self, base=None, *args, **kwargs):
        return json.dumps(self.to_dict(base), *args, **kwargs)


if __name__ == '__main__':

    chrono = MultiStageChrono(0, disabled=False)

    with chrono.time('all', verbose=True):
        for i in range(0, 10):

            with chrono.time('forward_back', verbose=True):
                with chrono.time('forward', verbose=True):
                    time.sleep(1)

                with chrono.time('backward', skip_obs=3, verbose=True) as t:
                    time.sleep(1)


    chrono.report()
    print(chrono.to_json(base={'main': 1}, indent='   '))


