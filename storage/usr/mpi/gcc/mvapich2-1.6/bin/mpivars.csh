if ($?path) then
    if ( "${path}" !~ */usr/mpi/gcc/mvapich2-1.6/bin* ) then
	set path = ( /usr/mpi/gcc/mvapich2-1.6/bin $path )
    endif
else
    set path = ( /usr/mpi/gcc/mvapich2-1.6/bin )
endif

if ("1" == "$?LD_LIBRARY_PATH") then
    if ("$LD_LIBRARY_PATH" !~ */usr/mpi/gcc/mvapich2-1.6/lib) then
        setenv LD_LIBRARY_PATH /usr/mpi/gcc/mvapich2-1.6/lib:${LD_LIBRARY_PATH}
    endif
else
    setenv LD_LIBRARY_PATH /usr/mpi/gcc/mvapich2-1.6/lib
endif

if ($?MANPATH) then
    if ( "${MANPATH}" !~ */usr/mpi/gcc/mvapich2-1.6/man* ) then
	setenv MANPATH /usr/mpi/gcc/mvapich2-1.6/man:$MANPATH
    endif
else
    setenv MANPATH /usr/mpi/gcc/mvapich2-1.6/man:
endif
