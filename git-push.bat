@echo off
set /p msg="Enter commit message: "
git add .
git commit -m "%msg%"
git push
echo Done!
pause
