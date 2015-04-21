# dnslookup.py                    Version 1.00                               #
# Copyright 2011 Phoenix Knowledge Ventures, LLC info@phoenixkv.com          #
# Created 2011-07-30              Last Modified 2011-07-30                   #
# Phoenix Knowledge Ventures, LLC: http://www.phoenixkv.com/                 #
##############################################################################
# COPYRIGHT NOTICE                                                           #
# Copyright 2011 Phoenix Knowledge Ventures, LLC  All Rights Reserved.       #
#                                                                            #
# This script can be freely distributed, as long as these copyright          #
# and ownership statements remain in tact. Changes/modifications to this     #
# script are permitted, as long as a referral is made.                       #
#                                                                            #
# At no time is anyone permitted to charge for this script, nor add a        #
# premium when including this script as a value added item/service.          #
#                                                                            #
# Please send all questions/comments to the author: info@phoenixkv.com       #
############################################################################## 


########## db settings here ############
  
DBHOST = "localhost"
DBNAME = "pdns"
DBUSER = "pdns_admin"
DBPASS = "your_pdns_admin_password"
NS_SERVER = "1.2.3.4"

## end of db settings : Don't edit past this line ##

############ DB Class ###################
import time
import datetime
import MySQLdb
import commands
import gc
class DBManager(object):
	def __init__(self):

		self.db= MySQLdb.connect(host=DBHOST, user=DBUSER , passwd=DBPASS, db=DBNAME)


	def get_domains(self):
		cursor = self.db.cursor()
		sql ="""SELECT id, name from domains;"""
		cursor.execute(sql)
		rows = cursor.fetchall()
		return rows

	def clean_records(self,id):
		cursor = self.db.cursor()
		sql ="""DELETE FROM records where domain_id='%s';"""%(id)
		cursor.execute(sql)
		self.db.commit()
		sql ="""DELETE FROM domains where id='%s';"""%(id)
		cursor.execute(sql)
		self.db.commit()
		return True

	def close(self):

		self.db.close()


################################################
###### the main script  here #########################
db = DBManager()

domains = db.get_domains()
for domain in domains:
	id = domain[0]
	name = domain[1]
	cmd = "nslookup %s %s"%(name,NS_SERVER)
	out = commands.getoutput(cmd)
	if 'REFUSED' in out:
		print name,'REFUSED'
		db.clean_records(id)
	else:
		print name,'OK'

db.close()
