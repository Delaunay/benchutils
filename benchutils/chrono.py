import time

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


class _ChronoContext:
    """
        sync is a function that can be set to make the timer wait before ending.
        This is useful when timing async calls like cuda calls
    """
    def __init__(self, stream: StatStream, sync: Callable):
        self.stream = stream
        self.start = 0
        self.sync = sync

    def __enter__(self):
        # Sync before starting timer to make sure previous work is not timed as well
        self.sync()
        self.start = time.time()

    def __exit__(self, exception_type, exc_val, traceback):
        # Sync before ending timer to make sure all the work is accounted for
        self.sync()
        self.end = time.time()

        if exception_type is None:
            self.stream.update(self.end - self.start)


class MultiStageChrono:
    def __init__(self, skip_obs=10, sync=None, disabled=False, name=None):
        self.chronos = {}
        self.skip_obs = skip_obs
        self.sync = sync
        self.name = name
        self.disabled = disabled
        if sync is None:
            self.sync = lambda: None

    def time(self, name, skip_obs=None):
        if self.disabled:
            return _DummyContext()

        if self.name is not None:
            name = '{}.{}'.format(self.name, name)

        val = self.chronos.get(name)

        if val is None:
            val = StatStream(self.skip_obs)
            if skip_obs is not None:
                val = StatStream(skip_obs)
            self.chronos[name] = val

        return _ChronoContext(val, self.sync)

    def make_table(self, common: List = None, transform=None):
        common = common or []
        table = []

        for i, (name, stream) in enumerate(self.chronos.items()):
            table.append([name] + stream.to_array(transform) + common)

        return table

    def report(self, speed=False, size=1, file_name=None, common: Dict[str, str] = None):
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
        print_table(header, table, file_name)


if __name__ == '__main__':

    chrono = MultiStageChrono(2, disabled=False)

    for i in range(0, 10):

        with chrono.time('forward_back'):
            with chrono.time('forward'):
                time.sleep(1)

            with chrono.time('backward', skip_obs=3):
                time.sleep(1)

    chrono.report()
