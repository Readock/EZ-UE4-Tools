set target="C:\Users\Admin\AppData\Roaming\Blender Foundation\Blender\4.1\scripts\addons\EZ-UE4-Tools"
@RD /S /Q %target%
xcopy /i /s ".\*" %target%