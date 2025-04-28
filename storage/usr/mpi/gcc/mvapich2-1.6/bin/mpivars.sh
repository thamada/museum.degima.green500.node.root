if ! echo ${PATH} | grep -q /usr/mpi/gcc/mvapich2-1.6/bin ; then
    PATH=/usr/mpi/gcc/mvapich2-1.6/bin:${PATH}
fi

if ! echo ${LD_LIBRARY_PATH} | grep -q /usr/mpi/gcc/mvapich2-1.6/lib ; then
    export LD_LIBRARY_PATH=/usr/mpi/gcc/mvapich2-1.6/lib:${LD_LIBRARY_PATH} 
fi

if ! echo ${MANPATH} | grep -q /usr/mpi/gcc/mvapich2-1.6/man ; then
    MANPATH=/usr/mpi/gcc/mvapich2-1.6/man:${MANPATH}
fi
