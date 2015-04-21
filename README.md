# python-plesk-secondary-dns

SECONDARY DNS USING PARALLELS PLESK PANEL AND POWERDNS

This tutorial is provided as-is, with no warranty or guarantee that it will work as described.

Our environment consists of the following:

- Server with Parallels Plesk Server 10.3 (IP Address: 1.2.3.4)
- Server with Ubuntu 10.04 with PowerDNS (IP Address: 2.3.4.5)

INSTALLATION OF POWERDNS ON SECONDARY SERVER

We started with a completely vanilla install of Ubuntu 10.04 with only an SSH server installed. Please make sure the system is up-to-date prior to installation. Please note, that this tutorial does not cover the configuration of PowerDNS to run optimally for you. Please consult the PowerDNS documentation for this.

# sudo aptitude install mysql-server mysql-client

You will be asked to provide a password for the MySQL root user. Enter a password of your choosing, and then re-enter it when prompted.

Once installation of MySQL has completed, now we install PowerDNS:

# sudo aptitude install pdns-server pdns-backend-mysql

Now, we create the database and database user for PowerDNS to use:

# mysql -u root -p

Enter the password you chose during the install of MySQL.

mysql> CREATE DATABASE pdns;
mysql> GRANT ALL ON pdns.* TO 'pdns_admin'@'localhost' IDENTIFIED BY 'enter_a_password_here';
mysql> FLUSH PRIVILEGES;

Before creating the database tables, you need to decide if you want to manage the server via command line only, or using PowerAdmin. If using PowerAdmin, you will need to install the apache2 and php5 packages using aptitude. Once you do that, you can download and install PowerAdmin from their website.

To administer the PowerDNS server from the command line, you will need to now create tables for the PowerDNS database, but first we select the database:

mysql> use pdns;

Now at the MySQL prompt, you need to create your tables:

CREATE TABLE domains (
id INT auto_increment,
name VARCHAR(255) NOT NULL,
master VARCHAR(128) DEFAULT NULL,
last_check INT DEFAULT NULL,
type VARCHAR(6) NOT NULL,
notified_serial INT DEFAULT NULL,
account VARCHAR(40) DEFAULT NULL,
primary key (id)
);

CREATE UNIQUE INDEX name_index ON domains(name);

CREATE TABLE records (
id INT auto_increment,
domain_id INT DEFAULT NULL,
name VARCHAR(255) DEFAULT NULL,
type VARCHAR(6) DEFAULT NULL,
content VARCHAR(255) DEFAULT NULL,
ttl INT DEFAULT NULL,
prio INT DEFAULT NULL,
change_date INT DEFAULT NULL,
primary key(id)
);

CREATE INDEX rec_name_index ON records(name);
CREATE INDEX nametype_index ON records(name,type);
CREATE INDEX domain_id ON records(domain_id);

CREATE TABLE supermasters (
ip VARCHAR(25) NOT NULL,
nameserver VARCHAR(255) NOT NULL,
account VARCHAR(40) DEFAULT NULL
);

quit;

We now need to edit the configuration files for PowerDNS, starting with /etc/powerdns/pdns.conf. Find the Launch section, and add the following line:

launch=gmysql

Now, edit the file /etc/powerdns/pdns.d/pdns.local and add the following lines:

gmysql-host=127.0.0.1
gmysql-user=pdns_admin
gmysql-password=same_password_chosen_above
gmysql-dbname=pdns

Now, restart PowerDNS:

/etc/init.d/pdns restart

We now need to prepare our PowerDNS server to accept incoming zone transfers from our primary server (running Plesk Panel). To do this, we log back into MySQL:

# mysql -u root -p

Once we enter our MySQL root password, we change to the PowerDNS database, and then enter the details into the supermaster table (changing the IP address of 1.2.3.4 to the real IP of your Plesk server):

mysql> use pdns;
mysql> INSERT INTO supermasters (ip, nameserver) VALUES (1.2.3.4, ns1.yourdomain.com);
mysql> quit;

CONFIGURATION OF PARALLELS PLESK PANEL SERVER TO SEND ZONE DATA

Log in to your server, and then into MySQL:

# mysql -uadmin -p`cat /etc/psa/.psa.shadow`

At the MySQL server prompt, we now need to change to the Plesk Server database, and then enter our command to change the configuration for zone transfers (changing the IP address of 2.3.4.5 to the real IP of your secondary server):

mysql> use psa;
mysql> insert misc values('DNS_Allow_Transfer01','2.3.4.5');
mysql> quit;

To complete the setup and start the zone transfers, log into your Parallels Plesk Panel server administration site, and edit a domain. Once you click the button to update the zone, you will start seeing the zone data being passed to your secondary nameserver.

CHECKING THE ZONES ON YOUR SECONDARY NAMESERVER

We needed a method to check that the zones listed in the PowerDNS database were still active on the Plesk server since the current setup only provides for the creation and updates of zone - not deletions. When an account is removed from the Plesk server, the zone still exists on your secondary server. We originally created a script in PHP, but found that Python was quicker required less resources on the server. To use this script, we need to ensure that Python is installed:

# sudo aptitude install python python-mysqldb

You can download the Python script here:

http://cdn.phoenixkv.com/tutorials/secondary-dns.zip

Once you have the script downloaded, you need to edit the following lines at the top of the script, changing your database, username, password, and primary NS server IP as necessary:

DBHOST = "localhost"
DBNAME = "pdns"
DBUSER = "pdns_admin"
DBPASS = "your_pdns_admin_password"
NS_SERVER = "1.2.3.4"

Once you save and upload the script to your server, you can run the script to verify that it is working as expected:

python dnslookup.py

The output will list the domain name in the database and "OK" for domains that exist at your Plesk server. If the domain does not exist, you will see the word "REFUSED" next to the domain name. The script will then remove all "REFUSED" domains and records associated with that domain from your PowerDNS database.

To finish, you can create a cron job to run the script periodically.

# crontab -e

To set your script to run at 50 minutes past the hour, every hour, enter:

50 */1 * * * python /path/to/dnslookup.py > /dev/null 2>&1

Now you're all set with a completely automated primary and secondary DNS system for your customers hosted on your Plesk server! 
