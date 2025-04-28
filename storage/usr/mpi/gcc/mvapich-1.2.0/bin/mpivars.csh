if ("1" == "$?path") then
    if ( "${path}" !~ */usr/mpi/gcc/mvapich-1.2.0/bin* ) then
        setenv path /usr/mpi/gcc/mvapich-1.2.0/bin:$path
    endif
else
    setenv path /usr/mpi/gcc/mvapich-1.2.0/bin:
endif

if ("1" == "$?LD_LIBRARY_PATH") then
    if ("$LD_LIBRARY_PATH" !~ */usr/mpi/gcc/mvapich-1.2.0/lib) then
        setenv LD_LIBRARY_PATH /usr/mpi/gcc/mvapich-1.2.0/lib:/usr/mpi/gcc/mvapich-1.2.0/lib/shared:${LD_LIBRARY_PATH}
    endif
else
    setenv LD_LIBRARY_PATH /usr/mpi/gcc/mvapich-1.2.0/lib:/usr/mpi/gcc/mvapich-1.2.0/lib/shared
endif

