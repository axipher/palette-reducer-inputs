@echo off

for %%A IN (inputs\*.png) do start /b /wait "" python .\reduce.py -i "%%~fA" -p 32 -a