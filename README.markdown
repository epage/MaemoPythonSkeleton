This is a skeleton for building packages for Maemo 4.1, Maemo 5, Meego-1.2-Harmattan, and eventually MeeGo.

For some background:

* http://eopage.blogspot.com/2011/08/python-packaging-for-harmattan.html

The main git home for src/utils is: https://github.com/epage/PythonUtils

Depends on (I just copy it into my project):

* https://gitorious.org/sdist_maemo/sdist_maemo

Setting up a project
===================
grep for REPLACEME which is scattered throughout the files.

    grep --color -Irn "REPLACEME" .

To find files that need renaming

    find . -iname "*REPLACEME*"

Rename "src" to your project name

ln -s PROJECT_NAME src

Update support/obs_upload.sh with your OBS project path

Examples:

* https://github.com/epage/ejpi
* https://github.com/epage/Gonvert

Building a package
===================
Run

    make package
    make upload

Build Process
===================

The makefile generate the following

* setup.PLATFORM.py
* data/PLATFORM/PROJECT.desktop
* data/icons/ICON_SIZES/PROJECT.png

setup.PLATFORM.py then creates a source package

For Ubuntu, the Makefile then creates a binary package

Uploading process
===================

dput is used for uploading Diablo and Fremantle packages

OSC is used for uploading Harmattan packages

Maemo Garage's git integration is used for distribution the Ubuntu binary package
