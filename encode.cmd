@echo off
set PATH=%PATH%;C:\Python27\
if "%1" equ "" (
    python %~dp0\encode_keys.py -i main.dat.xml -o main.en.dat
)
if "%1" neq "" (
    python %~dp0\encode_keys.py -i %1 -o %1.dat
)
