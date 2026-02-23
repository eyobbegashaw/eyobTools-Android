[app]

# (str) Title of your application
title = eyoTools

# (str) Package name
package.name = eyotools

# (str) Package domain (needed for android/ios packaging)
package.domain = org.rabon

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,ttf,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,fonts/*,functions/*.py

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, __pycache__, .git, buildozer.spec

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3==3.11.6, kivy==2.3.0, pillow==10.1.0, pyjnius==1.6.0, pypdf==3.17.4, android, requests==2.31.0, urllib3==2.1.0

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (list) Supported orientations
orientation = portrait

#
# OSX Specific
#

# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 2.1.0

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color
android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Gradle dependencies to add
android.gradle_dependencies = 'androidx.core:core:1.9.0'

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (int) Numeric version code
android.numeric_version = 1

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) The format used to package the app for release mode
android.release_artifact = apk

# (str) The format used to package the app for debug mode
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (bool) Control passing the --use-setup-py vs --ignore-setup-py to p4a
p4a.setup_py = False

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
p4a.extra_args = --ignore-setup-py

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# (str) Path to a custom ios-deploy
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# (bool) Whether or not to sign the code
ios.codesign.allowed = false


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifact storage
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
