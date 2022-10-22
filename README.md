## Description
This project was created thanks to the following video. https://www.youtube.com/watch?v=FTQx17vz_3E&t=209s
Many thanks to https://www.youtube.com/c/TimaeuSS and his team for their google sheet that computes the efficiency of each gear.
Please have a look at the original calculator @ https://tinyurl.com/gearcalcv1

Open QT Designer with
```powershell
qt5-tools designer
```
convert ui file to py file
```powershell
pyuic5 -x gui.ui -o gui.py
```

If you have a python environment, you can run the script using python.
If not, you can unzip dist.zip and run the main.exe file init.

db.csv consist of the min-max of each sub-stat.
