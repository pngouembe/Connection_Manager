#!/bin/bash

RANDOM=$$
for i in {1..10}
do
   ../src/Connection_manager_client.py -t $(($(($RANDOM%2))+1)) &
   echo "launched client $i"
   sleep 0.5
done