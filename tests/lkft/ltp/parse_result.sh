#!/bin/sh

usage() {
	echo "Usage:\n\t./parse_result.sh input.log output.csv"
}

[ ! -f $1 ] && usage && exit 1
[ -z $2 ] && usage && exit 1

cat $1 | egrep "PASS|CONF|FAIL" | sed 's/CONF/SKIP/' | awk 'BEGIN {print "Testcase,Result,Exit Value"} {print $1","$2","$3}' > $2
echo -n "LTP TESTS: " >> $2
cat $1 | grep "Total Tests:" | awk '{printf "total %d ",$3}' >> $2
cat $1 | grep "Total Skipped Tests:" | awk '{printf "skip %d ",$4}' >> $2
cat $1 | grep "Total Failures:" | awk '{printf "fail %d",$3}' >> $2

