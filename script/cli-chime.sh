#!/bin/sh

# script/cli-chime: run the cli with file parameter

rm ./output/*.csv




set -e
cd "$(dirname "$0")/.."


#script/bootstrap
#script/-check-docker-compose

#echo
#echo "==> Rebuilding containers…"
docker-compose up -d --build

clear

echo "Processing models..."
d=$(date +"%Y%m%d")

i=0

while read -r line;
do
  c="docker container exec chime_app_1 python ./src/cli.py ""$line";
  $c;
  i=$(( $i + 1 ))
  printf "Model: "$i"\r"
done < "./parameters/params.txt"

echo "Model run complete...(count: "$i")"

i=$(($i * 3))

echo "Waiting for "$i" files to transfer from docker ... "
cd ./output

fc=$(ls -l | grep -v ^t | wc -l)
while [ $fc != $i ]; do
  sleep 1;
  fc=$(ls -l | grep -v ^t | wc -l)
done

echo "Combining raw results..."
output_file="chimeprojections_raw_"$d".csv"
i=0

files=$(ls raw*.csv )
for filename in $files; do
   if [[ $i -eq 0 ]] ; then
     # copy csv headers from first file
    head -1 $filename > $output_file
    fi
   # copy csv without headers from other files
   tail -n +2 $filename >> $output_file
   i=$(( $i + 1 ))
   rm $filename
done

echo "Combining admissions results..."
output_file="chimeprojections_admissions_"$d".csv"
i=0

files=$(ls admits*.csv )
for filename in $files; do
   if [[ $i -eq 0 ]] ; then
     # copy csv headers from first file
     head -1 $filename > $output_file
   fi
   # copy csv without headers from other files
   tail -n +2 $filename >> $output_file
   i=$(( $i + 1 ))
   rm $filename
done

echo "Combining census results..."
output_file="chimeprojections_census_"$d".csv"
i=0
files=$(ls census*.csv )
for filename in $files; do
   if [[ $i -eq 0 ]] ; then
     # copy csv headers from first file
     head -1 $filename > $output_file
   fi
   # copy csv without headers from other files
   tail -n +2 $filename >> $output_file
   i=$(( $i + 1 ))
   rm $filename
done

echo "Completed processing..."
echo ""

cd ..
