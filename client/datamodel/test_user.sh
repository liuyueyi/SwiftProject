#!/bin/bash
if [ $1 = 'add' ]; then
    swauth-add-account -K swauthkey Android  -G 'java,it,cs,android,developer,coder,designer,game,application,ad,fressman,veteran' -I 'android develop group'
    swauth-add-user -K swauthkey -a wzb wzb wzb -G 'Android'
    swauth-add-user -K swauthkey -a Android wzb wzb -I 'java it cs android fressman game developer'
    swauth-add-user -K swauthkey -a wxj wxj wxj -G 'Android'
    swauth-add-user -K swauthkey -a Android wxj wxj -I 'java it cs android fressman appliaction designer'

elif [ $1 = 'remove' ]; then
    swauth-delete-user -K swauthkey wzb wzb
    swauth-delete-account -K swauthkey wzb
    swauth-delete-user -K swauthkey wxj wxj
    swauth-delete-account -K swauthkey wxj
    swauth-delete-user -K swauthkey Android wxj
    swauth-delete-user -K swauthkey Android wzb
    swauth-delete-account -K swauthkey Android

elif [ $1 = 'show' ]; then
    swauth-list -K swauthkey $2

elif [ $1 = 'allow' ]; then
	cp upload/allow.jpg .
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb upload Image allow.jpg 
	rm allow.jpg
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb post Image allow.jpg -m 'attr_policy:(developer or designer)and(java or fressman)'

elif [ $1 = 'forbid' ]; then
	cp upload/forbid.jpg .
    swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb upload Image forbid.jpg 
	rm forbid.jpg
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb post Image forbid.jpg -m 'attr_policy:(developer and game)and(java or fressman)' 

elif [ $1 = 'delete' ]; then
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb delete Image $2

elif [ $1 = 'list' ]; then
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb list $2

elif [ $1 = 'cmd' ]; then
	swift -A http://127.0.0.1:8080/auth/v1.0 -U Android:wzb -K wzb $2 $3 $4 $5 $6

else
    echo ''
    echo -e "    command format : add_user.sh [ add | remove | show | allow | forbid | delete | list ]"
    echo -e "\tadd   :\t create one group(Android) and two user(wzb wxj)"
    echo -e "\tremove:\t remove the group and two user"
    echo -e "\tshow  :\t list all the accounts or containers"
    echo -e "\tallow :\t upload allow.jpg to Android Image container, both wzb and wxj can access"
    echo -e "\tforbid:\t upload forbid.jpg to Android Image continer, wzb can access but wxj can not"
    echo -e "\tdelete:\t +object name, delete the object"
    echo -e "\tlist  :\t list the container or objects'"
    echo -e '\tcmd   :\t swift cmd, can be { post container, upload, download, delete ...}'
	echo ''
fi
