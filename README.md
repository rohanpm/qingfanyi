qingfanyi
=========

*qingfanyi* or *qfy* is an interactive Chinese to English translation
tool for Linux desktop systems.

Usage
=====

1. Enable accessibility support for your desktop environment, or the
   program(s) where you'll want to use qingfanyi.
   (See *Enabling Accessibility* below for additional details.)
2. Run `qfy`.
3. When the active window contains some traditional or simplified
   Chinese text, press the global shortcut (default: `<Ctrl><Alt>z`).
4. A window will pop up highlighting all translatable Chinese text in
   the active window. Click on a Chinese word or phrase to look up the
   English definition, or use the keyboard to navigate between
   words/phrases:
    - Left/Right: move backwards/forwards one word or phrase
    - Up/Down: jump many words backwards/forwards
    - Enter: close window

![qingfanyi with Firefox demo](misc/doc/ff-demo.gif?raw=true)

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
    - Install qt-at-spi. Currently you will need a pre-release version
      (greater than 0.4.0) because all released versions contain bugs.
      Fedora or CentOS users may use the version from
      [copr](https://copr.fedorainfracloud.org/coprs/rohanpm/qingfanyi/).
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