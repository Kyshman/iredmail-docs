# Upgrade iRedMail from 1.3 to 1.3.1

!!! attention

	 Check out the lightweight on-premises email archiving software developed by iRedMail team: [Spider Email Archiver](https://spiderd.io/).

[TOC]

!!! note "Remote Upgrade Assistance"

    Check out our [remote upgrade support](https://www.iredmail.org/support.html) if you need assistance.

## ChangeLog

* Jul  7, 2020: initial release.

## General (All backends should apply these changes)

### Update `/etc/iredmail-release` with new iRedMail version number

iRedMail stores the release version in `/etc/iredmail-release` after
installation, it's recommended to update this file after you upgraded iRedMail,
so that you can know which version of iRedMail you're running. For example:

```
1.3.1
```

### Upgrade iRedAPD (Postfix policy server) to the latest stable release

The recent iRedAPD-4.0 and 4.1 contain a critical bug which causes temporarily
rejection, this new release fixes it.

Please follow below tutorial to upgrade iRedAPD to the latest stable release:
[Upgrade iRedAPD to the latest stable release](./upgrade.iredapd.html)

### Upgrade Roundcube webmail to the latest stable release (1.4.7)

!!! warning "Roundcube 1.4"

    Since Roundcube 1.3, at least __PHP 5.4__ is required. If your server is
    running PHP 5.3 and cannot upgrade to 5.4, please upgrade Roundcube
    the latest 1.2 branch instead.

Roundcube 1.4.6 fixes few security issues, 1.4.7 fixes a new one. All users are encouraged to upgrade
_as soon as possible_.

* [How to upgrade Roundcube](https://github.com/roundcube/roundcubemail/wiki/Upgrade).

References:

- 05 July 2020, [Security updates 1.4.7, 1.3.14 and 1.2.11 released](https://roundcube.net/news/2020/07/05/security-updates-1.4.7-1.3.14-and-1.2.11)
- 07 June 2020, [Updates 1.4.6 and 1.3.13 released](https://roundcube.net/news/2020/06/07/updates-1.4.6-and-1.3.13-released)
- 02 June 2020, [Security updates 1.4.5 and 1.3.12 released](https://roundcube.net/news/2020/06/02/security-updates-1.4.5-and-1.3.12)

### Upgrade netdata to the latest stable release (1.23.1)

If you have netdata installed, you can upgrade it by following this tutorial:
[Upgrade netdata](./upgrade.netdata.html).

### Fixed: update Fail2ban filter rules to match new error log produced by latest Roundcube

Please run commands below as root user to get latest filter file for Roundcube:

```
cd /etc/fail2ban/filter.d/
wget -O roundcube.iredmail.conf https://raw.githubusercontent.com/iredmail/iRedMail/1.3.1/samples/fail2ban/filter.d/roundcube.iredmail.conf
```

Restarting `fail2ban` service is required.
