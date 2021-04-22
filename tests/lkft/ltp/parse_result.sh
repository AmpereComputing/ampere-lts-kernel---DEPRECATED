#!/bin/sh

usage() {
	echo "Usage:\n\t./parse_result.sh input.log output.csv"
}

[ ! -f $1 ] && usage && exit 1
[ -z $2 ] && usage && exit 1

tmpresult=`mktemp -u`
cat $1 | egrep "PASS|CONF|FAIL" | sed 's/CONF/SKIP/' | awk '{print $1","$2","$3}' > $tmpresult
echo "Class,Testcase,Result,Exit Value" > $2
while read -r rline; do
	test_name=$(echo $rline | awk -F , '{printf $1}')
	class_path=$(grep -r "^$test_name" /opt/ltp/runtest/ | head -1 | awk -F : '{printf $1}')
	echo "$(basename $class_path),$rline" >> $2
done < $tmpresult
rm -f $tmpresult

echo -n "LTP TESTS: " >> $2
cat $1 | grep "Total Tests:" | awk '{printf "total %d ",$3}' >> $2
cat $1 | grep "Total Skipped Tests:" | awk '{printf "skip %d ",$4}' >> $2
cat $1 | grep "Total Failures:" | awk '{printf "fail %d",$3}' >> $2

