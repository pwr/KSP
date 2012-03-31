; AutoHotkey script for Windows
; Gives a nice systray icon to start/stop the proxy
;
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn All, OutputDebug ; Recommended for catching common errors.
SetWorkingDir %A_ScriptDir%

; how long to wait for the python daemon to stop by itself
global SHUTDOWN_GRACE_TIME := 5

SetBatchLines 10ms
#Persistent
#SingleInstance

EnvGet PYTHONHOME, PYTHONHOME
PYTHON := PYTHONHOME . "\pythonw.exe"
PYOPTIONS := "-b -OO -W all"

Menu Tray, NoStandard
Menu Tray, Icon, %PYTHON%
Menu Tray, Tip, KSP Daemon Monitor
Menu Tray, Add, Start Daemon, _start
Menu Tray, Add, Stop Daemon, _stop
Menu Tray, Add, Restart Daemon, _restart
Menu Tray, Add
Menu Tray, Add, Stop Daemon and Exit Monitor,  _exit_ahk

SetTimer _watch, 500

PIPE_NAME := "\\.\pipe\ksp.ctrl"

_start: ; auto-executed
	PIPE := DllCall("CreateNamedPipe","str",PIPE_NAME,"UInt",2,"UInt",0,"UInt",1,"UInt",0,"UInt",0,"UInt",0,"Ptr",0,"Ptr")
	if (PIPE) {
		Run %PYTHON% %PYOPTIONS% ..\main.py --control-pipe %PIPE_NAME%, , , python_pid
		OutputDebug started %PYTHON% => %python_pid% (%ErrorLevel%)
	} else {
		OutputDebug Failed to create control pipe %PIPE_NAME% (%ErrorLevel%/%A_LastError%)
		ExitApp
	}
	return

_stop:
	stop_python(python_pid)
	return

_restart:
	GoSub _stop
	GoTo _start

_watch: ; watches for the python process and updates the menu when necessary
	if (python_pid) {
		Process WaitClose, %python_pid%, 0.001
		if (ErrorLevel) { ; still running
			Menu Tray, Disable, Start Daemon
			Menu Tray, Enable, Stop Daemon
			Menu Tray, Enable, Restart Daemon
		} else {
			if (python_pid) {
				OutputDebug ouch, process %python_pid% died
				python_pid := 0
			}
		}
	}
	if (not python_pid) {
		Menu Tray, Enable, Start Daemon
		Menu Tray, Disable, Stop Daemon
		Menu Tray, Disable, Restart Daemon
	}
	return

_reload_ahk:
	stop_python(python_pid)
	Reload
	return

_exit_ahk:
	stop_python(python_pid)
	ExitApp
	return

_documentation:
	Loop %PYTHONHOME%\Doc\*.chm
		Run %A_LoopFileFullPath%
	return

stop_python(ByRef pid) {
	if (pid) {
		global PIPE
		ppid := pid
		pid := 0
		DllCall("ConnectNamedPipe", ptr, PIPE, ptr, 0)
		if !DllCall("WriteFile", ptr, PIPE, "Str", "C", "UInt", 1, "UInt*", 0, ptr, 0)
		    OutputDebug WriteFile failed: %ErrorLevel%/%A_LastError%
		DllCall("CloseHandle", ptr, PIPE)
		stop_process(ppid, SHUTDOWN_GRACE_TIME)
	}
}

stop_process(pid, grace = 5) {
	sleep_wait := grace
	While (sleep_wait > 0) {
		Process WaitClose, %pid%, 1
		if (ErrorLevel = 0) {
			OutputDebug Process %pid% stopped gracefully
			return
		}
		sleep_wait := sleep_wait - 1
	}
	OutputDebug Failed to close process %pid% in %grace% seconds
	Process Close, %pid%
	Process WaitClose, %pid%, 0.1
	if (ErrorLevel) { ; still runnning?
		OutputDebug Failed to kill process %pid%
	} else {
		OutputDebug Process %pid% terminated
	}
}

