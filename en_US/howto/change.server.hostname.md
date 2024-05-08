# Change server hostname

To change server hostname after iRedMail installation, please update below
files to replace old hostname by the new one.

## System config files

* `/etc/hosts`
* RHEL/CentOS:
    * for RHEL/CentOS 6: `/etc/sysconfig/network`
* Debian/Ubuntu:
    * `/etc/hostname`
    * `/etc/mailname`

## Postfix

* `/var/spool/postfix/etc/hosts`
* `/etc/postfix/main.cf` (Linux/OpenBSD) or `/usr/local/etc/postfix/main.cf` (FreeBSD)

## Amavisd

* RHEL/CentOS, OpenBSD: `/etc/amavisd/amavisd.conf`
* Debian/Ubuntu: `/etc/amavis/conf.d/50-user`
* FreeBSD: `/usr/local/etc/amavisd.conf`

## SOGO

* `/etc/httpd/conf.d/SOGo.conf`
* `/etc/apache2/conf.d/SOGo.conf`
* `/etc/apache2/conf-available/SOGo.conf`

## Deprecated Components

### Apache

* RHEL/CentOS: `/etc/httpd/conf/httpd.conf`
* Debian/Ubuntu: `/etc/apache2/apache.conf`

## OpenDMARC:

* Linux/OpenBSD: `/etc/opendmarc.conf` (parameter `AuthservID` and `TrustedAuthservIDs`)
* FreeBSD: `/usr/local/etc/opendmarc.conf` (parameter `AuthservID` and `TrustedAuthservIDs`)
