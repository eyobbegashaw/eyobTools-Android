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
# ⚠️ ትኩረት: buildozer.spec እዚህ መዘርዘር አይገባም!
source.exclude_dirs = tests, venv, bin, __pycache__, .git

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# ቀላል በሆነ መልኩ python3 ብቻ እንጠቀም (ስሪት አንጥቀስም)
requirements = python3, kivy==2.3.0, pillow, pyjnius, pypdf, android, requests, urllib3

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (list) Supported orientations
orientation = portrait

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

# (bool) Use --private data storage
android.private_storage = True

# (bool) Skip updating Android sdk
android.skip_update = False

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Gradle dependencies
android.gradle_dependencies = 'androidx.core:core:1.9.0'

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (list) Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (int) Numeric version code
android.numeric_version = 1

# (bool) Enable Android auto backup
android.allow_backup = True

# (str) Release artifact format
android.release_artifact = apk

# (str) Debug artifact format
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) Bootstrap
p4a.bootstrap = sdl2

# (bool) Use setup.py
p4a.setup_py = False

# (str) Extra command line arguments
p4a.extra_args = --ignore-setup-py

[buildozer]

# (int) Log level
log_level = 2

# (int) Warn on root
warn_on_root = 1

# (str) Build directory
build_dir = ./.buildozer

# (str) Bin directory
bin_dir = ./bin
