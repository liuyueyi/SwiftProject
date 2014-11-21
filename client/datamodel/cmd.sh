#!/bin/bash
if [ $1 != 'help' ]; then
	sudo swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb $1 $2 $3 $4 $5 $6 $7
else
	echo 'command format: [ post | upload | download | list | stat ] + ...'
fi
