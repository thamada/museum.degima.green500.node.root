if ! echo ${PATH} | grep -q /usr/mpi/gcc/mvapich-1.2.0/bin ; then
    export PATH=/usr/mpi/gcc/mvapich-1.2.0/bin:${PATH}
fi
if ! echo ${LD_LIBRARY_PATH} | grep -q /usr/mpi/gcc/mvapich-1.2.0/lib ; then
    export LD_LIBRARY_PATH=/usr/mpi/gcc/mvapich-1.2.0/lib:/usr/mpi/gcc/mvapich-1.2.0/lib/shared:${LD_LIBRARY_PATH}
fi
