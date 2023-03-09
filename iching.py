import argparse
from datetime import datetime
import random
import requests
import sys


def test_assertions():
    if first:
        assert throw == 5 or throw == 9
    else:
        assert throw == 4 or throw == 8

def print_fingers(fingers):
    sys.stderr.write(' | '.join([str(finger_stalks) for finger_stalks in fingers]))
    sys.stderr.write('\n')

def get_coins():
    r = requests.get('https://www.random.org/integers/?format=plain&num=18&min=2&max=3&col=18&base=10')
    text = r.text
    return text.strip().split('\t')

def get_stalks():
    r = requests.get('https://www.random.org/decimal-fractions/?num=18&dec=2&col=18&format=plain&rnd=new')
    text = r.text
    return text.strip().split('\t')

def throw_stalks(test):
    '''
    Attempt to capture the spirit of the traditional yarrow stalk method. It's
    supposed to be like this, trust me
    '''
    if test:
        splits = [random.random() for _ in range(18)]
    else:
        splits = [float(x) for x in get_stalks()]
    throws = []
    for _ in range(6):
        sys.stderr.write('\n----------\n')
        if test:
            first = True
        stalks = 50
        for _ in range(3):
            # 1. Remove a yarrow stalk, and put it in front of you, in a direction
            # parallel to your body. This is the observer stalk
            stalks -= 1
            sys.stderr.write('\n    -    \n')
            # 2. Randomly divide the remaining sticks into 2 piles, with one
            # hand holding each pile. Put the 2 piles on both sides of you,
            # pointing away from you, in a direction perpendicular to your body
            split = splits.pop()
            left = int(split * stalks)
            right = stalks - left
            sys.stderr.write('--  |  --\n')
            sys.stderr.write('{:02d}  |  {:02d}\n\n'.format(left, right))
            # 3. Pick up a yarrow stalk from the pile on the RIGHT, and put
            # it between the little finger and the ring finger of the LEFT
            # hand. This is the 2nd stalk.
            right -= 1
            fingers = [1, 0, 0]
            print_fingers(fingers)
            # 4. Pick up the remaining yarrow stalks from the pile on the LEFT
            # with your LEFT hand.
            # 5. Remove 4 stalks at a time from the LEFT hand, and put them on
            # the table, in individual piles of 4 stalks each. This process is
            # stopped when there are 4 or less stalks left. Put these remaining
            # stalks held on the LEFT hand between the ring finger and the
            # middle finger of the LEFT hand.
            fingers[1] = 4 if left % 4 == 0 else left % 4
            print_fingers(fingers)
            # 6. Now, pick up the RIGHT hand heap, and sort it by fours in the
            # same way, placing the remainder into the next gap between your
            # fingers.
            fingers[2] = 4 if right % 4 == 0 else right % 4
            print_fingers(fingers)
            throw = sum(fingers)
            if test:
                test_assertions()
                first = False
            throws.append(2 if throw > 6 else 3)
            sys.stderr.write('\n    {}    '.format(throw))
            sys.stderr.write('\n')
            stalks -= throw
            stalks += 1
            sys.stderr.write('   \n')
    return throws


def throw_coins(test):
    if test:
        throws = [random.randint(2, 3) for _ in range(18)]
    else:
        throws = [int(x) for x in get_coins()]
    return throws


def build_lines(throws):
    line = []
    for throw in throws:
        line.append(throw)
        if len(line) == 3:
            yield sum(line)
            line = []


def format_line(throw):
    if throw == 9:
        return '      -o-', '   - -   ', True
    if throw == 6:
        return '      -x-', '   ---   ', True
    if throw == 7:
        line_string = '{}   ---{}'
        return line_string.format('   ', ''), line_string.format('', '   '), False
    if throw == 8:
        line_string = '{}   - -{}'
        return line_string.format('   ', ''), line_string.format('', '   '), False


def format_throws(throws):
    primary_hexagram, secondary_hexagram = [], []
    use_secondary = False
    for throw in throws:
        primary, secondary, thrown_secondary = format_line(throw)
        primary_hexagram.append(primary)
        secondary_hexagram.append(secondary)
        use_secondary = use_secondary or thrown_secondary
    reversed_output = primary_hexagram
    if use_secondary:
        reversed_output = [''.join(throw) for throw in zip(secondary_hexagram, primary_hexagram)]
        reversed_output.insert(0, '')
        reversed_output.insert(0, 'secondary    primary')
    return '\n'.join(['   {}'.format(line) for line in reversed(reversed_output)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-c', '--coins', action='store_true', help='Throw the coins not the yarrow stalks')
    parser.add_argument('-f', '--file', help='file to append results to')
    args = parser.parse_args()

    method = throw_coins if args.coins else throw_stalks
    throw = build_lines(method(args.test))
    formatted_results = '''
----------------
{date}

{formatted_throw}

{method_name}{test_run}
'''.format(method_name='The Coins' if args.coins else 'The Stalks',
                           formatted_throw=format_throws(throw),
                           test_run=' (test run)' if args.test else '',
                           date=datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    if args.file:
        with open(args.file, 'a') as fh:
            fh.write(formatted_results)
    print(formatted_results)
