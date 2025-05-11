source redirect.tcl

set result [redirect::redirect {
    puts "testing"
    puts stderr "hello world"
    puts stderr "dying"
    puts "dead"
    expr {1 + 1}
} out err]

if {[string trim $out] ne ""} {
    puts "BEGIN STDOUT\n$out\nEND STDOUT"
}
if {[string trim $err] ne ""} {
    puts "BEGIN STDERR\n$err\nEND STDERR"
}
if {$result ne ""} {
    puts "BEGIN RESULT\n$result\nEND RESULT"
}