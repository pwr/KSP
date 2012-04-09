#!/bin/sh

PYBIN=$(which python3)
if test -z "$PYBIN"; then
	PYBIN=$(which python)
fi
if test -z "$PYBIN"; then
	echo "No 'python[3]' found in path."
	exit 1
fi

PIDFILE=~/.ksp.pid
MAIN=~/ksp/main.py
if ! test -r "$MAIN"; then
	MAIN=$(dirname "$0")/../main.py
fi
if ! test -r "$MAIN"; then
	echo "Did not find 'main.py', looked in ~/ksp/main.py and $MAIN"
	exit 1
fi

case "$1" in
	start)
		PID=$(cat $PIDFILE 2>/dev/null)
		if test -n "$PID"; then
			if ps -p "$PID" >/dev/null; then
				echo "KSP already running? ($PID)"
				exit 1
			fi
		fi
		$PYBIN $MAIN --config ~/etc &
		echo $! > $PIDFILE
		echo "KSP started ($!)"
		;;
	stop)
		PID=$(cat $PIDFILE 2>/dev/null)
		rm -f $PIDFILE
		if test -n "$PID"; then
			if ps -p "$PID" >/dev/null; then
				kill "$PID"
				echo "KSP killed"
				exit 0
			fi
		fi
		echo "KSP not running?"
		;;
	restart)
		$0 stop
		sleep 3
		exec $0 start
		;;
	status)
		PID=$(cat $PIDFILE 2>/dev/null)
		if test -n "$PID"; then
			if ps -p "$PID" >/dev/null; then
				echo "KSP is running ($PID)"
				exit 0
			fi
		fi
		echo "KSP is not running"
		;;
	*)
		echo "Use: $0 start|stop|restart|status"
		exit 1
esac

