#!/bin/env python3

import sys
import re


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage:\n\t{} kselftest.txt output.csv".format(sys.argv[0]))
        sys.exit(1)

    fp_out = open(sys.argv[2], "w")

    tests_sum = 0
    tests_ok = 0
    tests_skip = 0
    tests_fail = 0
    with open(sys.argv[1], "r") as fp_in:
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


if "__main__" == __name__:
    sys.exit(main())
