"""
Utility to write a to a file periodically with options for rollover.

"""
import os
import time
import argparse
from datetime import datetime

from loremipsum import generate_sentence

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('file_path', type=str, help='Path to file to write to')
parser.add_argument(
    '--clean', help='Remove contents first', default=False,
    action="store_true")
parser.add_argument(
    '--rollover', type=int, help='Reset the file after N lines', default=0)
args = parser.parse_args()


def reset_log():
    fd = open(args.file_path, 'w')
    fd.close()


def log():
    fd = open(args.file_path, 'a')
    print("{}: {}".format(
        datetime.now(), generate_sentence()[2]), file=fd)
    fd.close()
    time.sleep(1)


if args.clean:
    reset_log()
else:
    if not os.path.exists(args.file_path):
        print("File does not exists, alternatively use --clean to create it.")

count = 1
while True:
    if args.rollover and count > args.rollover:
        print("Rolling over after {} lines".format(args.rollover))
        reset_log()
        count = 1

    log()
    count += 1
