#!/bin/bash
for i in {1..100}
do
    echo "Suuup bro $(($i*100))"
    adb shell input swipe 540 $(($i*100)) 540 0
done
