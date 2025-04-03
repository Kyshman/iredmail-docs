# Backup and restore

!!! attention

	 Check out the lightweight on-premises email archiving software developed by iRedMail team: [Spider Email Archiver](https://spiderd.io/).

[TOC]

## Backup

### Backup mailboxes

All mailboxes are stored under `/var/vmail/vmail1` by default, this path is
configurable during iRedMail installation, so the real directory may be
different on your server.

Mail messages are stored in Maildir format by default, that means one mail
message is one plain text file (but mail body is encoded), you can backup
mailboxes with tool like `rsync` or other backup tools.

After restored mailboxes, `/var/vmail/vmail1` must be owned by user `vmail`,
group `vmail`, permission `0700` on iRedMail server.

### Backup mail accounts

iRedMail has daily cron job to backup mail accounts which are stored in
SQL/LDAP database, you can run command below as `root` user to verify it:

```shell
crontab -l -u root
```

Sample output on an iRedMail server with OpenLDAP backend:

```
# iRedMail: Backup OpenLDAP data every day on 03:01 AM
1   3   *   *   *   /bin/bash /var/vmail/backup/backup_openldap.sh

# iRedMail: Backup MySQL databases every day on 03:10 AM
10   3   *   *   *   /bin/bash /var/vmail/backup/backup_mysql.sh
```

Notes:

* Backup files are stored under directory `/var/vmail/backup` by default, if
  you want to change it, please update parameter `BACKUP_ROOTDIR` in
  backup script (e.g. `/var/vmail/backup/backup_mysql.sh`).
* SQL backup is a plain SQL file for each database.
* LDAP backup is only a plain file in LDIF format.
* Backup files are compressed with `bzip2` by default, you can decompress them
  with command `bunzip2`. for example, `bunzip2 file_name.bz2`.
* It's ok to run the backup scripts manually.

### Backup additional data manually

* DKIM keys. They're stored under `/var/lib/dkim/` by default. If you don't
  backup them, it's ok to generate new keys and you must update DNS record
  (`dkim._domainkey.[YOUR_MAIL_DOMAIN]`) with new DKIM key. Refer to another
  document to generate DKIM key and update DNS record:
  [Sign DKIM signature on outgoing emails for new mail domain](./sign.dkim.signature.for.new.domain.html).

* SOGo (Calendar, Contacts, Tasks): check SOGo official document:
  <http://wiki.sogo.nu/backupRestore>

    * since iRedMail-0.9.7, iRedMail will setup a daily cron job to backup SOGo
      data during iRedMail installation.
    * When restoring (with `sogo-tool`), you have to first restore all users
      and their folders, then their preferences. Afterwards you have to restore
      all preferences again to get back shared calendars.

        That is because first it sets the sharing privileges on the folders
        (which have to exist, before you can set them). The sharing will not
        work in most cases, because the privileges of the origin is not yet set.
        Only the second restore of the preferences can set the shared folders,
        because now the privileges are OK.

        Make sure to restart memcached between the two restores of the
        privileges, else SOGo will use old infos from the first run.

* OpenLDAP backend:

    * If you enabled additional LDAP schema files in OpenLDAP, you should
      backup them, copy them to new server and enable them. Otherwise you
      cannot import backup LDIF file due to missing required LDAP attributes.

## Restore

### How to restore SQL databases

You can simply restore plain SQL files backed up by above backup scripts.

!!! warning

    If you're restoring on a __NEW__ iRedMail server, do __NOT__
    restore the database which is named `mysql` exported from old server, it
    contains SQL usernames and passwords used in many components (e.g. Postfix,
    Dovecot, Roundcube webmail) on old server. New iRedMail server already has
    the same SQL accounts with different passwords, so please do not restore
    `mysql` database, otherwise almost all services won't work due to incorrect
    SQL credentials.

Let's take SQL database `iredapd` for example. Assume the backup file is
`/var/vmail/backup/mysql/2021/11/19/iredapd-2021-11-19-23-02-01.sql.bz2`.

- The backup file was compressed with `bzip2` (with `.bz2` extension in file
  name), please decompress it with command `bunzip2` first:

    ```
    bunzip2 /var/vmail/backup/mysql/2021/11/19/iredapd-2021-11-19-23-02-01.sql.bz2
    ```

    You should get decompressed file `/var/vmail/backup/mysql/2021/11/19/iredapd-2021-11-19-23-02-01.sql`

- Login to MySQL / MariaDB server as the SQL root user.
- Restore the decompressed SQL file:

```
USE iredapd;
SOURCE /var/vmail/backup/mysql/2021/11/19/iredapd-2021-11-19-23-02-01.sql;
```

That's it.

You should restore other databases with same steps but different
backup files. Again, __do not restore the database named `mysql`__.

#### After restored databases

If you're restoring from an old iRedMail release, you need to update SQL
structure first.

For example, If you're restoring iRedMail from `0.9.1` to `0.9.5`, you must
check upgrade tutorials for iRedMail-0.9.1 and newer releases, then apply all
SQL structure changes mentioned in the upgrade tutorials.

You can find [all iRedMail upgrade tutorials here](./iredmail.releases.html).

### LDAP

#### How to restore OpenLDAP backup

!!! attention

    * Data dumped with `slapcat` command must be restored with `slapadd` command.
    * Data exported with `ldapsearch` command can be imported with `ldapadd` command.

Backup script runs command `slapcat` to dump whole LDAP tree as a backup copy,
it must be restored with command `slapadd`.

Below example shows how to restore a LDAP backup on RHEL/CentOS 6.x, files and
directories may be different on other Linux/BSD distributions, you can find
the correct ones in this tutorial:
[Locations of configuration and log files of major components](./file.locations.html#openldap).

* LDAP backups are stored under `/var/vmail/backup/ldap/[YEAR]/[MONTH]/` by
  default, for example, `/var/vmail/backup/ldap/2015/05/`. And it's compressed
  with `bzip2` command to save disk space. we must decompress it first.

* Go to the backup directory, find the latest backup. here we use backup file
  `2015-05-10-03:01:01.ldif.bz2` for example.

```
# cd /var/vmail/backup/ldap/2015/05/
# bunzip2 2015-05-10-03:01:01.ldif.bz2
# ls -l 2015-05-10-03:01:01.ldif
-rw-r--r-- 1 root root 7352 May 10 03:01 2015-05-10-03:01:01.ldif
```

* Find passwords for `cn=vmail,dc=xx,dc=xx` and `cn=vmailadmin,dc=xx,dc=xx`
  in the root directory of iRedMail installation directory on __NEW__ iRedMail
  server. for example, `/root/iRedMail-0.9.0/iRedMail.tips`. Notes:

    * They're plain passwords, not hashed or encrypted.
    * You can also find `cn=vmail`'s password in Postfix config files under
      `/etc/postfix/mysql` (MySQL/MariaDB backend) or
      `/etc/postfix/pgsql` (PostgreSQL backend).
    * You can also find `cn=vmailadmin`'s password in
      [iRedAdmin config file](./file.locations.html#iredadmin).

Below is sample copy in file `iRedMail.tips`.

```
OpenLDAP:
    ...
    * LDAP bind dn (read-only): cn=vmail,dc=example,dc=com, password: py2BQwM0zoRM5nciK68AlP8dyu2Mq6
    * LDAP admin dn (used for iRedAdmin): cn=vmailadmin,dc=example,dc=com, password: 9wr0mHeVYz2uaxSAGBLucVkOgYPSBB
```

* Now hash them with command `slappasswd`:

```
# slappasswd -h '{ssha}' -s 'py2BQwM0zoRM5nciK68AlP8dyu2Mq6'    # <- cn=vmail's password
{SSHA}eJEO2yGVryVw+mZ/Qd2HMSyrl6u9WDhd

# slappasswd -h '{ssha}' -s '9wr0mHeVYz2uaxSAGBLucVkOgYPSBB'    # <- cn=vmailadmin's password
{SSHA}lWt6zjOOUq+2WUmiAea2FXLB4oHMYvIb
```

* Open the backup file `2015-05-10-03:01:01.ldif` with your favourite text
  editor, find `usePassword` line of `cn=vmail` and `cn=vmailadmin`.
  __Important notes__:

    * A line that begins with a SPACE denotes that the characters following the
      space are part of the previous line.
    * There're two colons after `userPassword` string (`userPassword::`).

Below is a sample copy in `2015-05-10-03:01:01.ldif`:

```
dn: cn=vmail,dc=iredmail,dc=org
...
userPassword:: e1NTSEF7F8AwbjVqeER1R1dXVmREN1RJU8NtdnFHN0hnekdWYzVHSG9iWEE9PQ=  # <- remove this line
 =                                                                              # <- remove this line
...

dn: cn=vmailadmin,dc=iredmail,dc=org
userPassword:: e1NTSEF9alZi8E12dS9FNllaMktteFh7YkZham1mM3Jqc21cdEFsZjJIeEE9PQ=  # <- remove this line
 =                                                                              # <- remove this line
...
```

Replace these two `userPassword` lines by the newly generated ssha passwords,
save your change, exit your text editor.

```
dn: cn=vmail,dc=iredmail,dc=org
...
userPassword: {SSHA}eJEO2yGVryVw+mZ/Qd2HMSyrl6u9WDhd
...

dn: cn=vmailadmin,dc=iredmail,dc=org
userPassword: {SSHA}lWt6zjOOUq+2WUmiAea2FXLB4oHMYvIb
...
```

__Important note__:  There's only __ONE__ colon after `userPassword` string
(`userPassword:`).

* OpenLDAP service must be stopped while restoring backup. So we stop it first (Note: OpenLDAP service name may be different on your machine, for example, `ldap`, `slapd`, etc, please use the correct one):

```
# systemctl stop slapd
```

* If you enabled additional LDAP schema files on old server, you `MUST` copy
  these schema files to new server, and enable them in OpenLDAP on new server,
  also add new indexes for attributes defined in these additional LDAP schema
  files if necessary. Otherwise you may not be able to import backup LDIF file
  due to missing required attributes.

* Remove all files under OpenLDAP data directory defined in LDAP config file
  `slapd.conf` (parameter `directory`) except file `DB_CONFIG` (this file
  doesn't exist if you're running `mdb` backend, so you can ignore it if you're
  running `mdb` backend).
  For example:

!!! note "About file DB_CONFIG"

    File `DB_CONFIG` is present if you're running `bdb` backend.
    But `mdb` backend doesn't need any config file for database, so you can
    ignore this file if you're running `mdb` backend.

```
# File: /etc/openldap/slapd.conf

...
database    bdb
suffix      dc=iredmail,dc=org
directory   /var/lib/ldap/iredmail.org
...
```

So you should remove all files under directory `/var/lib/ldap/iredmail.org`
except `/var/lib/ldap/iredmail.org/DB_CONFIG`.

```
# cd /var/lib/ldap/iredmail.org/
# mv DB_CONFIG ~
# rm -rf /var/lib/ldap/iredmail.org/*
# mv ~/DB_CONFIG .
```

* Start OpenLDAP service immediately, then stop it again. It will create
  necessary files required by backend db (`dbd` in our case, `database dbd`).

```
# systemctl start slapd
# systemctl stop slapd
```

* Make sure OpenLDAP server is __NOT__ running, then restore backup LDIF file
  with command `slapadd`.

```
# slapadd -f /etc/openldap/slapd.conf -l /var/vmail/backup/ldap/2015/05/2015-05-10-03:01:01.ldif
```

    You may see a message like `The first database does not allow slapadd;
    using the first available one (2)`, it's safe to ignore it since the
    first one is database `monitor` which is created and maintained by
    OpenLDAP internally.

* It's OK to start OpenLDAP server now. It may report errors like below:

```
# systemctl restart slapd
Stopping slapd:                                            [  OK  ]
/var/lib/ldap/iredmail.org/mailMessageStore.bdb is not owned[WARNING]"
/var/lib/ldap/iredmail.org/objectClass.bdb is not owned by "[WARNING]
...
Checking configuration files for slapd:  config file testing succeeded
                                                           [  OK  ]
Starting slapd:                                            [  OK  ]
```

If you see above warning about improper file ownership, please set correct file
owner on newly created db files immediately, then restart OpenLDAP service:

```
# chown ldap:ldap /var/lib/ldap/iredmail.org/*
# systemctl restart slapd
```

If you're restoring LDAP data from an old iRedMail server, you should add
missing LDAP attribute/values, which are introduced in newer iRedMail releases,
by following step below: [After LDAP Restore](#after-ldap-restore).

#### How to restore OpenBSD ldapd(8) backup

iRedMail-0.9.5 and later releases ships script
`/var/vmail/backup/backup_ldapd.sh` for daily backup. It backs up data with
command `ldapsearch` (not `slapcat` - which is used for OpenLDAP), so you have
to restore its data with command `ldapadd`.

* Stop ldapd service first.

```
rcctl stop ldapd
```

* Remove all files under ldapd data directory `/var/db/ldap/`.
* Start ldapd service.

```
rcctl start ldapd
```

* Import backup LDIF file:

    * Please replace `cn=Manager,dc=xx,dc=xx` by the real LDAP root dn.
    * Please replace `/path/to/backup.ldif` by the real path of backup LDIF file.

```
# ldapadd -x -D 'cn=Manager,dc=xx,dc=xx' -W -f /path/to/backup.ldif
```

If you're restoring LDAP data from an old iRedMail server, you should add
missing LDAP attribute/values, which are introduced in newer iRedMail releases,
by following step below: [After LDAP Restore](#after-ldap-restore).

#### After LDAP restore

If you're restoring from an old iRedMail release, you need to add missing LDAP
attribute/values, which are introduced in new iRedMail releases, by running
Python scripts below: <https://github.com/iredmail/iRedMail/tree/master/update/ldap>

For example:

* If you're restoring iRedMail from `0.9.1` to `0.9.5`, you must run all update
  scripts for iRedMail-0.9.1 and newer releases. In this case, only file
  `updateLDAPValues_094_to_095.py` listed in above link is required.

* If you're restoring iRedMail from `0.8.6` to `0.9.5`, you need 3 files:

    * `updateLDAPValues_086_to_087.py`
    * `updateLDAPValues_087_to_090.py`
    * `updateLDAPValues_094_to_095.py`

Please open the file you need to run, for example, `updateLDAPValues_094_to_095.py`,
find parameters like below:

```
uri = 'ldap://127.0.0.1:389'
basedn = 'o=domains,dc=example,dc=com'
bind_dn = 'cn=Manager,dc=example,dc=com'
bind_pw = 'passwd'
```

Please update them with the correct LDAP prefix (`dc=xx,dc=xx`) and bind
password, then run it with `python` command:

```
python updateLDAPValues_094_to_095.py
```
