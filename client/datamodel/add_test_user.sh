#!/bin/bash
if [ $1 = 'user' ]; then
	swauth-add-account -K swauthkey Test  -G 'attr1,attr2,attr3,attr4,attr5,attr6,attr7,attr8,attr9,attr10,attr11,attr12,attr13,attr14,attr15,attr16,attr17,attr18,attr19,attr20,attr21,attr22,attr23,attr24,attr25,attr26,attr27,attr28,attr29,attr30,attr31,attr32,attr33,attr34,attr35,attr36' -I 'test time cost group'
	swauth-add-user -K swauthkey -a test1 test1 test1 -G 'Test'
	swauth-add-user -K swauthkey -a Test test1 test1 -I 'attr1 attr4 attr7 attr10 attr13 attr16 attr19 attr22 attr25 attr28 attr31 attr34'

	swauth-add-user -K swauthkey -a test2 test2 test2 -G 'Test'
	swauth-add-user -K swauthkey -a Test test2 test2 -I 'attr2 attr5 attr8 attr11 attr14 attr17 attr20 attr23 attr26 attr29 attr32 attr35'

	swauth-add-user -K swauthkey -a test3 test3 test3 -G 'Test'
	swauth-add-user -K swauthkey -a Test test3 test3 -I 'attr3 attr6 attr9 attr12 attr15 attr18 attr21 attr24 attr27 attr30 attr33 attr36'

elif [ $1 = 'file' ]; then
        #two layer......
        # test1 and test2 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image two0.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image two0.jpg -m 'attr_policy:attr10 or attr11'
        # test1 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image two1.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image two1.jpg -m 'attr_policy:attr10 and attr34'
        
        #three layer.........
        # only test1 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image three0.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image three0.jpg -m 'attr_policy:(attr10 or attr11)and(attr13 or attr15)'
        #test1 and test2 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image three1.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image three1.jpg -m 'attr_policy:(attr10 and attr13)or(attr11 and attr53)'
        
        #four layer........
        #test1 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image four0.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image four0.jpg -m 'attr_policy:((attr10 or attr11)and(attr12 or attr13))and((attr16 or attr17)and(attr18 or attr19))'
        #test1 and test2 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image four1.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image four1.jpg -m 'attr_policy:((attr10 and attr13)or(attr11 or attr14))and((attr19 and attr16)or(attr17 and attr20))'
        
        #five layer.....
        #test1 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image five0.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image five0.jpg -m 'attr_policy:(((attr10 or attr11)and(attr12 or attr13))and((attr16 or attr17)and(attr18 or attr19)))and(((attr22 or attr23)and(attr24 or attr25))and((attr28 or attr29)and(attr30 or attr31)))'
        #test1 and test2 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image five1.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image five1.jpg -m 'attr_policy:(((attr10 and attr13)or(attr11 or attr14))and((attr19 and attr16)or(attr17 and attr20)))and(((attr1 and attr4)or(attr5 or attr8))and((attr25 and attr22)or(attr23 and attr26)))'
        
        #six layer.....
        #test1 can access
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 upload Image six.jpg
        swift -A http://127.0.0.1:8080/auth/v1.0 -U Test:test1 -K test1 post Image six.jpg -m 'attr_policy:((((attr10 or attr14)and attr13)and((attr22 or attr23)and(attr24 or attr25)))and(attr27 or attr31)) and ((((attr1 or attr2)and(attr3 or attr4)) and ((attr7 or attr8)and(attr9 or attr10))) and ((attr22 or attr25)and(attr28 and attr31)))'

elif [ $1 = 'delete' ]; then
        swauth-delete-user -K swauthkey Test test1
        swauth-delete-account -K swauthkey test1
        swauth-delete-user -K swauthkey Test test2
        swauth-delete-account -K swauthkey test2
        swauth-delete-user -K swauthKey Test test3
        swauth-delete-account -K swauthkey test3
        
        swauth-delete-account -K swauthkey Test

else
	echo 'command format: [ user | file | delete ]'
fi
