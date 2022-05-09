#!/bin/env python3

import argparse
import re
import sys


def main() -> int:
    args = parse_args()

    fp_out = open(args.output_csv_file, "w")

    tests_sum = 0
    tests_ok = 0
    tests_skip = 0
    tests_fail = 0
    with open(args.kselftest_log, "r") as fp_in:
        for line in fp_in:
            if re.match("^# selftests: (.+: .+)$", line):
                tests_sum += 1
                continue

            match_notok = re.match("^not ok \d+ selftests: (.+): (.+) # (.+)$", line)
            if match_notok:
                fp_out.write("{},{},{}\n".format(*match_notok.groups()))
                if "SKIP" in match_notok.group(3):
                    tests_skip += 1
                else:
                    tests_fail += 1
                continue

            # match 5.10 skip output
            match_skip = re.match("^.*ok \d+ selftests: (.+): (.+) # SKIP$", line)
            if match_skip:
                fp_out.write("{},{},{}\n".format(*match_skip.groups(), "SKIP"))
                tests_skip += 1
                continue

            match_ok = re.match("^.*ok \d+ selftests: (.+): (.+)$", line)
            if match_ok:
                fp_out.write("{},{},{}\n".format(*match_ok.groups(), "OK"))
                tests_ok += 1

    fp_out.write(
        "kselftests: total {} pass {} skip {} fail {}".format(
            tests_sum, tests_ok, tests_skip, tests_fail
        )
    )
    fp_out.close()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "kselftest_log",
        help="kselftest.txt log file",
        metavar="kselftest.txt",
    )
    parser.add_argument(
        "output_csv_file",
        help="Name of the CSV file to save the output to",
        metavar="output.csv",
    )

    args = parser.parse_args()
    return args


if "__main__" == __name__:
    sys.exit(main())
