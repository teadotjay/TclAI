namespace eval ::redirect {
    oo::class create TeeChannel {
        variable buffer
        method initialize {handle mode} {
            if {$mode ne "write"} {error "can't handle reading"}
            set buffer ""
            return {finalize initialize write}
        }
        method finalize {handle} {
        }
        method write {handle bytes} {
            append buffer $bytes
            return $bytes
        }
        method getBuffer {} {
            return $buffer
        }
    }

    proc redirect {command stdout_var stderr_var} {
        upvar $stdout_var stdout_value
        upvar $stderr_var stderr_value
        set stdout_capture [TeeChannel new]
        set stderr_capture [TeeChannel new]
        chan push stdout $stdout_capture
        chan push stderr $stderr_capture

        try {
            set result [uplevel #0 $command]
        } on error {TclError} {
            set result ""
            set error $TclError
        }

        chan pop stdout
        chan pop stderr
        set stdout_value [string trim [$stdout_capture getBuffer]]
        set stderr_value [string trim [$stderr_capture getBuffer]]
        if [info exists error] {append stderr_value $error}
        return $result
    }
}