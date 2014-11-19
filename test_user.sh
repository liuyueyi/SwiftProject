#!/bin/bash
if [ $1 = 'add' ]; then
	swauth-add-account -K swauthkey Android  -G 'java,it,cs,android,developer,coder,designer,game,application,ad,fressman,veteran' -I 'android develop group'
	swauth-add-user -K swauthkey -a wzb wzb wzb -G 'Android'
	swauth-add-user -K swauthkey -a Android wzb wzb -I 'java,it,cs,android,fressman,game,developer'
	swauth-add-user -K swauhtkey -a wxj wxj wxj -G 'Android'
	swauth-add-user -K swauthkey -a Android wxj wxj -I 'java,it,cs,android,fressman,appliaction,designer'
elif [ $1 = 'remove' ]; then
	swauth-delete-user -K swauthkey wzb wzb
	swauth-delete-account -K swauthkey wzb
	swauth-delete-user -K swauthkey wxj wxj
	swauth-delete-account -K swauthkey wxj
	swauth-delete-user -K swauthkey Android wxj
	swauth-delete-user -K swauthkey Android wzb
	swauth-delete-account -K swauthkey Android
elif [ $1 = 'list' ]; then
	swauth-list -K swauthkey $2
else
	echo "command format : add_user.sh [ add | remove | list ]"
fi
