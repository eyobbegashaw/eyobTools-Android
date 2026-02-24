[app]
title = eyoTools
package.name = eyotools
package.domain = org.rabon
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json,txt
source.include_patterns = assets/*,fonts/*,functions/*.py
source.exclude_dirs = tests, bin, venv, __pycache__, .git

# ቨርዥን
version = 1.0.0

# Requirements (ቀለል ያሉ እና የሚሰሩ)
requirements = python3, kivy==2.3.0, pillow, pyjnius, pypdf, android, requests, urllib3

# (str) Presplash and Icon (መንገዱን በቀጥታ እንዲህ ብታደርገው ይመረጣል)
presplash.filename = assets/splash.png
icon.filename = assets/icon.png

orientation = portrait
fullscreen = 0

# Permissions (ለአሁኑ አንድሮይድ ስሪቶች INTERNET ብቻ ይበቃል)
android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.archs = arm64-v8a, armeabi-v7a
android.release_artifact = apk
android.debug_artifact = apk
p4a.bootstrap = sdl2
p4a.setup_py = false

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
