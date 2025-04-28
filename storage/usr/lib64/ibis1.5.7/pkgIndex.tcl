proc ibis_load1.5.7 {dir} {
   puts "Loading package ibis from: $dir"
   uplevel \#0 load [file join $dir libibis.so.1.5.7]
}

package ifneeded ibis 1.5.7 [list ibis_load1.5.7 $dir]
