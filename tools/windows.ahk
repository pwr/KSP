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
global STOP_CODE := ""

Menu Tray, NoStandard
Menu Tray, Icon, %PYTHON%
Menu Tray, Tip, KSP Daemon Monitor
Menu Tray, Add, Start Daemon, _start
Menu Tray, Add, Stop Daemon, _stop
Menu Tray, Add, Restart Daemon, _restart
Menu Tray, Add
Menu Tray, Add, Stop Daemon and Exit Monitor,  _exit_ahk

SetTimer _watch, 500

_start: ; auto-executed
	Random STOP_CODE
	Run %PYTHON% %PYOPTIONS% ..\main.py --stop %STOP_CODE%, , , python_pid
	OutputDebug started %PYTHON% => %python_pid% (%ErrorLevel%) stop code %STOP_CODE%
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
		ppid := pid
		pid := 0
		; OutputDebug Closing process %ppid%
		; stupid Windows does not have signals, so we have to tell it some other way to stop gracefully
		http_ping("http://127.0.0.1:45350/?" . STOP_CODE)
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

http_ping(url) {
	io := DLLCall("wininet\InternetOpen", Ptr, 0, UInt, 0, Ptr, 0, Ptr, 0, UInt, 0, Ptr)
	if (io) {
		ok := DllCall("wininet\InternetSetOptionW", Ptr, io, UInt, 2, UIntP, 500, UInt, 4, UInt)	; INTERNET_OPTION_CONNECT_TIMEOUT
		ok := DllCall("wininet\InternetSetOptionW", Ptr, io, UInt, 5, UIntP, 1000, UInt, 4, UInt)	; INTERNET_OPTION_CONTROL_SEND_TIMEOUT
		ok := DllCall("wininet\InternetSetOptionW", Ptr, io, UInt, 6, UIntP, 1000, UInt, 4, UInt)	; INTERNET_OPTION_CONTROL_RECEIVE_TIMEOUT
		;ok := DllCall("wininet\InternetQueryOptionW", Ptr, io, UInt, 31, Ptr, &security_flags, UIntP, 4, UInt)	; INTERNET_OPTION_SECURITY_FLAGS

		headers := "Connection: close\r\n"
		ourl := DLLCall("wininet\InternetOpenUrlW", Ptr, io, Str, url, Str, headers, UInt, StrLen(headers), UInt, 0, UIntP, 1, Ptr)
		if (ourl) {
			DllCall("wininet\InternetCloseHandle", Ptr, ourl, UInt)
		}
		DLLCall("wininet\InternetCloseHandle", Ptr, io, UInt)
		if (!ourl) {
			err := DllCall("GetLastError")
			OutputDebug InternetOpenUrlW failed with error %err%
			return 0
		}
		return 1
	}
	return 0
}
