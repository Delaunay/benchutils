import time
import json

from benchutils.statstream import StatStream
from benchutils.report import print_table

from math import sqrt
from math import log10
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
        return self.stream

    def __exit__(self, exception_type, exc_val, traceback):
        # Sync before ending timer to make sure all the work is accounted for
        self.sync()
        self.end = time.time()

        if exception_type is None:
            self.stream.update(self.end - self.start)

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
        if sync is None:
            self.sync = lambda: None

    def time(self, name, skip_obs=None):
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

        return _ChronoContext(val, self.sync)

    def make_table(self, common: List = None, transform=None):
        common = common or []
        table = []

        for i, (name, stream) in enumerate(self.chronos.items()):
            table.append([name] + stream.to_array(transform) + common)

        return table

    def report(self, *args, format='csv', **kwargs):
        if format == 'csv':
            return self.report_csv(*args, **kwargs)
        print(self.to_json(*args, **kwargs))

    def report_csv(self, speed=False, size=1, file_name=None, common: Dict[str, str] = None, skip_header=False):
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
        if 'indent' not in kwargs:
            kwargs['indent'] = '  '
        return json.dumps(self.to_dict(base), *args, **kwargs)


def estimated_time_to_arrival(i, n, timer):
    # return ETA and +/- offset
    avg = timer.avg
    if avg == 0:
        avg = timer.val

    eta = (n - i - 1) * avg
    return eta, 2.95 * timer.sd * sqrt((n - i - 1))


def get_div_fmt(val):
    div, fmt = 60, 'min'
    if val < div:
        div = 1
        fmt = 's'
    return div, fmt


def show_eta(i, n, timer, end='\n'):
    eta, offset = estimated_time_to_arrival(i, n, timer)
    size = int(log10(n) + 1)

    div, fmt = get_div_fmt(eta)

    eta = f'{eta / div:6.2f} {fmt}'

    div, fmt = get_div_fmt(offset)
    conf = f'{offset / sqrt(div):6.2f} {fmt}'

    print(f'[{i:{size}d}/{n:{size}d}] {eta} +/- {conf}', end=end)


if __name__ == '__main__':

    chrono = MultiStageChrono(0, disabled=False)

    for i in range(0, 10):

        with chrono.time('forward_back') as timer:
            with chrono.time('forward'):
                time.sleep(1)

                if i % 2 == 0:
                    time.sleep(0.25)

            with chrono.time('backward', skip_obs=3):
                time.sleep(1)

                if i % 2 == 0:
                    time.sleep(0.25)

        show_eta(i, 10, timer)

    print()
    chrono.report()
    print(chrono.to_json(base={'main': 1}, indent='   '))
    print()
    chrono.report(format='json')

