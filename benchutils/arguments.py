import argparse


def add_bench_args(parser):
    """ add the arguments directly to a given parser """
    parser.add_argument('--repeat', type=int, default=100, help='number of observation timed')
    parser.add_argument('--number', type=int, default=10, help='number of time a task is done in between timer')
    parser.add_argument('--report', type=str, default=None, help='file to store the benchmark result in')
    return parser


def make_bench_args_parser(parser=None):
    """ create a an argument parser for the bench arguments"""
    if parser is None:
        parser = argparse.ArgumentParser('Bench util argument parser')

    add_bench_args(parser)
    return parser


def add_bench_subparser(parser):
    """ add the bench argument as a subparser """

    p = parser.add_subparsers(dest='bench')
    p = p.add_parser('bench')
    add_bench_args(p)
    return parser


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='DeepSpeech training')
    parser.add_argument('--checkpoint', dest='checkpoint', action='store_true', help='Enables checkpoints')
    parser.add_argument('--save_folder', default=None, help='Location to save epoch models')
    parser.add_argument('--model_path', default=None, help='Location to save best validation model')
    parser.add_argument('--continue_from', default='', help='Continue from checkpoint model')
    parser.add_argument('--labels_path', default='', help='path to labels.json')
    parser.add_argument('--seed', default=0xdeadbeef, type=int, help='Random Seed')
    parser.add_argument('--acc', default=23.0, type=float, help='Target WER')
    parser.add_argument('--cuda', default=False, action='store_true', help='use cuda?')
    parser.add_argument('--start_epoch', default=-1, type=int, help='Number of epochs at which to start from')

    parser = add_bench_subparser(parser)

    args = parser.parse_args('--checkpoint --seed 0 --cuda bench --repeat 9 --number 6 --report test.csv'.split(' '))

    print(args)
