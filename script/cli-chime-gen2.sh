#!/bin/sh

# script/cli-chime: run the cli with file parameter

rm ./output/*.csv

set -e
cd "$(dirname "$0")/.."

script/bootstrap
script/-check-docker-compose

echo
echo "==> Rebuilding containers…"
docker-compose up -d --build

clear

echo "Processing models..."
d=$(date +"%Y%m%d-%H%M")

i=0

while read -r line;
do
  c="docker container exec chime_app_1 python ./src/cli-gen2.py ""$line"
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

echo "Combining results..."

output_file_data="chime-data-"$d".csv"
output_file_hdr="chime-hdr-"$d".csv"
output_file_cdata="chime-cdata-"$d".csv"

files=$(ls head*.csv)

i=0

for filename in $files; do
  prefix="$(cut -d'.' -f2 <<<"$filename")"
  output_file=$prefix"-"$d".csv"

  echo $output_file

  while read -r line;
    do
      echo $line | cut -d"," -f2-1000 >> $output_file
  done < $filename

  IFS=$'\r\n' GLOBIGNORE='*' command eval  'hdrp=($(cat $output_file))'

  j=0
  shdr=""
  s=""
  for p in "${hdrp[@]}"
  do
     :
     if [[ $j -gt 0 ]] ; then
       # echo $p

       if [[ $i -eq 0 ]] ; then
         shdr=$shdr,$(echo $p | cut -d"," -f1)
       fi
       s=$s,$(echo $p | cut -d"," -f2)

     fi
     j=$(( $j + 1 ))
  done

  if [[ $i -eq 0 ]] ; then
    echo $shdr | cut -d"," -f2-1000 > $output_file_hdr
  fi
  echo $s | cut -d"," -f2-1000 >> $output_file_hdr

  echo >> $output_file
  echo >> $output_file

  while read -r line;
  do
    echo $line | cut -d"," -f2-1000 >> $output_file
  done < "body."$prefix".csv"

  echo >> $output_file
  echo >> $output_file

  while read -r line;
  do
    echo $line | cut -d"," -f2-1000 >> $output_file
  done < "cdata."$prefix".csv"

  while read -r line;
  do
    echo $line | cut -d"," -f2-1000 >> "tmp."$output_file
  done < "cdata."$prefix".csv"

  IFS=$'\r\n' GLOBIGNORE='*' command eval  'hdrp=($(cat tmp.$output_file))'

  j=0
  shdr=""
  s=""
  for p in "${hdrp[@]}"
  do
     :
     if [[ $j -gt 0 ]] ; then
       # echo $p

       if [[ $i -eq 0 ]] ; then
         shdr=$shdr,$(echo $p | cut -d"," -f1)
       fi
       s=$s,$(echo $p | cut -d"," -f2)

     fi
     j=$(( $j + 1 ))
  done

  if [[ $i -eq 0 ]] ; then
    echo $shdr | cut -d"," -f2-1000 > $output_file_cdata
  fi
  echo $s | cut -d"," -f2-1000 >> $output_file_cdata

  if [[ $i -eq 0 ]] ; then
    # copy csv headers from first file
    head -1 "body."$prefix".csv" | cut -d"," -f2-1000 > $output_file_data
  fi
  # copy csv without headers from other files
  tail -n +2 "body."$prefix".csv" | cut -d"," -f2-1000 >> $output_file_data
  i=$(( $i + 1 ))


  rm "body."$prefix".csv"
  rm "head."$prefix".csv"
  rm "cdata."$prefix".csv"
  rm "tmp."$output_file

  done

echo "Completed processing..."
echo ""

cd ..
