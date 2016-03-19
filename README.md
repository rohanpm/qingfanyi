qingfanyi
=========

*qingfanyi* or *qfy* is an interactive Chinese to English translation
tool for Linux desktop systems.

Usage
=====

(To be written...)

Enabling Accessibility
======================

This program relies on accessibility support via AT-SPI 2.
Generally, this is disabled by default and must be explicitly enabled
before the program will work.

This is an incomplete list of methods for enabling accessibility:

- GTK programs
    - set environment variable `GTK_MODULES=gail:atk-bridge`
- Firefox
    - set environment variable `GNOME_ACCESSIBILITY=1`
- Qt4 applications
    - Install qt-at-spi. You need at least version 0.4.0, due to the bug
      fixed by
      [this commit](http://commits.kde.org/qtatspi/fd0d5867348f6450a61294d6f85965e963bf1d48).
    - set environment variable `QT_ACCESSIBILITY=1`
- Qt5 applications
    - set environment variable `QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`
- Java applications
    - (to be determined...)

Please be aware that the quality of accessibility support varies between
programs. Enabling accessibility may cause performance or stability
issues in some programs.

License
=======

This software is licensed under the GNU General Public License version
3. Please see the included LICENSE.GPL for the terms of this license.

This software incorporates a copy of
[CC-CEDICT](http://www.mdbg.net/chindict/chindict.php?page=cc-cedict),
a complete Chinese to English dictionary. This data is licensed under
the
[Creative Commons Attribution-Share Alike 3.0 License](http://creativecommons.org/licenses/by-sa/3.0/)