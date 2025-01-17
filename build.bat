@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 --vcvars_ver=14.16
set CCFLAGS=/nologo /D _USING_V110_SDK71_ /D _WIN32_WINNT=0x0503
set LDFLAGS=/nologo /subsystem:windows,"5.01"
call .venv\Scripts\activate.bat
call nuitka.cmd --windows-console-mode=disable --standalone --onefile --onefile-no-compression --msvc=14.3 --remove-output --nowarn-mnemonic=old-python-windows-console --enable-plugin=tk-inter --include-data-files=walkfree.dll=walkfree.dll --file-version=1.2.0.0 walkman_gui.py
pause
