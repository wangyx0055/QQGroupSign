#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import sqlitedict

reload(sys)
sys.setdefaultencoding('utf-8')

def updateUserData(qq, skey):
    mydict = sqlitedict.SqliteDict('users.db', autocommit=True)
    mydict[qq] = skey
    mydict.close()

def updateUserEmailData(qq, email):
    mydict = sqlitedict.SqliteDict('users_email.db', autocommit=True)
    mydict[qq] = email
    mydict.close()

def laodUserData():
    mydict = sqlitedict.SqliteDict('users.db', autocommit=True)
    lst = mydict.items()
    mydict.close()
    return lst

def getUserEmailData(qq):
    mydict = sqlitedict.SqliteDict('users_email.db', autocommit=True)
    email = None
    try:
        email = mydict[qq]
    except:
        pass
    mydict.close()
    return email

def removeUserData(qq):
    mydict = sqlitedict.SqliteDict('users.db', autocommit=True)
    try:
        mydict.pop(qq)
        print mydict.items()
    except:
        pass
    finally:
        mydict.close()

def removeUserEmailData(qq):
    mydict = sqlitedict.SqliteDict('users_email.db', autocommit=True)
    try:
        mydict.pop(qq)
        print mydict.items()
    except:
        pass
    finally:
        mydict.close()