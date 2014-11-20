#!/bin/bash

if [ $1 = 'remote' ]; then
	sudo swift -A http://192.168.0.122:8080/auth/v1.0 -U Android:wzb -K wzb $2 $3 $4 $5 $6 $7
elif [ $1 = 'local' ]; then
	sudo swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb $2 $3 $4 $5 $6 $7
else
	echo 'command format: [ remote | local ] + [ post | upload | download | list | stat ] + ...'
fi
