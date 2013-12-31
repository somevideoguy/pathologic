@echo off
set PATH=%PATH%;C:\Python27
set FILE=%1
if [%1] ==[] set FILE=main.dat
python %~dp0\decode_keys.py -i %file% -o main.dat.xml
rem python "%~dp0"decode_keys.py -i main_.dat -o main_.dat.xml
