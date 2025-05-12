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
            append buffer "[encoding convertfrom unicode $bytes]"
            return $bytes
        }
        method getBuffer {} {
            return $buffer
        }
    }

    proc redirect {command outvar} {
        upvar $outvar out_value
        set capture [TeeChannel new]
        chan push stdout $capture
        chan push stderr $capture

        try {
            set result [uplevel #0 $command]
        } on error {TclError} {
            set result ""
            set error $TclError
        }

        chan pop stdout
        chan pop stderr
        set out_value [string trim [$capture getBuffer]]
        if [info exists error] {append out_value $error}
        return $result
    }

    namespace export redirect
}