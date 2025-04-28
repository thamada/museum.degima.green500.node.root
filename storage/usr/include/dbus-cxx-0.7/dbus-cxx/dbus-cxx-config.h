#ifndef _DBUS_CXX_DBUS_CXX_CONFIG_H
#define _DBUS_CXX_DBUS_CXX_CONFIG_H 1
 
/*
dbus-cxx/dbus-cxx-config.h.
Generated
automatically
at
end
of
configure.
*/
/* config.h.  Generated from config.h.in by configure.  */
/* config.h.in.  Generated from configure.ac by autoheader.  */

/* Enable debugging output */
/* #undef DBUS_CXX_DEBUG_ENABLED */

/* If defined, dbus 1.2 or higher is present */
#ifndef DBUS_CXX_HAVE_DBUS_12 
#define DBUS_CXX_HAVE_DBUS_12  /**/ 
#endif

/* Define to 1 if you have the <dlfcn.h> header file. */
#ifndef DBUS_CXX_HAVE_DLFCN_H 
#define DBUS_CXX_HAVE_DLFCN_H  1 
#endif

/* Define to 1 if you have the <expat.h> header file. */
#ifndef DBUS_CXX_HAVE_EXPAT_H 
#define DBUS_CXX_HAVE_EXPAT_H  1 
#endif

/* Define to 1 if you have the <inttypes.h> header file. */
#ifndef DBUS_CXX_HAVE_INTTYPES_H 
#define DBUS_CXX_HAVE_INTTYPES_H  1 
#endif

/* Define to 1 if you have the `expat' library (-lexpat). */
#ifndef DBUS_CXX_HAVE_LIBEXPAT 
#define DBUS_CXX_HAVE_LIBEXPAT  1 
#endif

/* Define to 1 if you have the `popt' library (-lpopt). */
#ifndef DBUS_CXX_HAVE_LIBPOPT 
#define DBUS_CXX_HAVE_LIBPOPT  1 
#endif

/* Define to 1 if you have the `pthread' library (-lpthread). */
#ifndef DBUS_CXX_HAVE_LIBPTHREAD 
#define DBUS_CXX_HAVE_LIBPTHREAD  1 
#endif

/* Define to 1 if you have the `rt' library (-lrt). */
#ifndef DBUS_CXX_HAVE_LIBRT 
#define DBUS_CXX_HAVE_LIBRT  1 
#endif

/* Define to 1 if you have the `thread' library (-lthread). */
/* #undef DBUS_CXX_HAVE_LIBTHREAD */

/* Define to 1 if the system has the type `long long int'. */
#ifndef DBUS_CXX_HAVE_LONG_LONG_INT 
#define DBUS_CXX_HAVE_LONG_LONG_INT  1 
#endif

/* Define to 1 if you have the <memory.h> header file. */
#ifndef DBUS_CXX_HAVE_MEMORY_H 
#define DBUS_CXX_HAVE_MEMORY_H  1 
#endif

/* Define to 1 if you have the <popt.h> header file. */
#ifndef DBUS_CXX_HAVE_POPT_H 
#define DBUS_CXX_HAVE_POPT_H  1 
#endif

/* Define if g++ supports C++0x features. */
#ifndef DBUS_CXX_HAVE_STDCXX_0X 
#define DBUS_CXX_HAVE_STDCXX_0X  /**/ 
#endif

/* Define to 1 if you have the <stdint.h> header file. */
#ifndef DBUS_CXX_HAVE_STDINT_H 
#define DBUS_CXX_HAVE_STDINT_H  1 
#endif

/* Define to 1 if you have the <stdlib.h> header file. */
#ifndef DBUS_CXX_HAVE_STDLIB_H 
#define DBUS_CXX_HAVE_STDLIB_H  1 
#endif

/* Define to 1 if you have the <strings.h> header file. */
#ifndef DBUS_CXX_HAVE_STRINGS_H 
#define DBUS_CXX_HAVE_STRINGS_H  1 
#endif

/* Define to 1 if you have the <string.h> header file. */
#ifndef DBUS_CXX_HAVE_STRING_H 
#define DBUS_CXX_HAVE_STRING_H  1 
#endif

/* Define to 1 if you have the <sys/stat.h> header file. */
#ifndef DBUS_CXX_HAVE_SYS_STAT_H 
#define DBUS_CXX_HAVE_SYS_STAT_H  1 
#endif

/* Define to 1 if you have the <sys/types.h> header file. */
#ifndef DBUS_CXX_HAVE_SYS_TYPES_H 
#define DBUS_CXX_HAVE_SYS_TYPES_H  1 
#endif

/* Define to 1 if you have the <unistd.h> header file. */
#ifndef DBUS_CXX_HAVE_UNISTD_H 
#define DBUS_CXX_HAVE_UNISTD_H  1 
#endif

/* Define to 1 if the system has the type `unsigned long long int'. */
#ifndef DBUS_CXX_HAVE_UNSIGNED_LONG_LONG_INT 
#define DBUS_CXX_HAVE_UNSIGNED_LONG_LONG_INT  1 
#endif

/* Define to the sub-directory in which libtool stores uninstalled libraries.
   */
#ifndef DBUS_CXX_LT_OBJDIR 
#define DBUS_CXX_LT_OBJDIR  ".libs/" 
#endif

/* Name of package */
#ifndef DBUS_CXX_PACKAGE 
#define DBUS_CXX_PACKAGE  "dbus-cxx" 
#endif

/* Define to the address where bug reports for this package should be sent. */
#ifndef DBUS_CXX_PACKAGE_BUGREPORT 
#define DBUS_CXX_PACKAGE_BUGREPORT  "rvinyard@cs.nmsu.edu" 
#endif

/* Major version */
#ifndef DBUS_CXX_PACKAGE_MAJOR_VERSION 
#define DBUS_CXX_PACKAGE_MAJOR_VERSION  0 
#endif

/* Micro version */
#ifndef DBUS_CXX_PACKAGE_MICRO_VERSION 
#define DBUS_CXX_PACKAGE_MICRO_VERSION  0 
#endif

/* Minor version */
#ifndef DBUS_CXX_PACKAGE_MINOR_VERSION 
#define DBUS_CXX_PACKAGE_MINOR_VERSION  7 
#endif

/* Define to the full name of this package. */
#ifndef DBUS_CXX_PACKAGE_NAME 
#define DBUS_CXX_PACKAGE_NAME  "dbus-cxx" 
#endif

/* Define to the full name and version of this package. */
#ifndef DBUS_CXX_PACKAGE_STRING 
#define DBUS_CXX_PACKAGE_STRING  "dbus-cxx 0.7.0" 
#endif

/* Define to the one symbol short name of this package. */
#ifndef DBUS_CXX_PACKAGE_TARNAME 
#define DBUS_CXX_PACKAGE_TARNAME  "dbus-cxx" 
#endif

/* Define to the version of this package. */
#ifndef DBUS_CXX_PACKAGE_VERSION 
#define DBUS_CXX_PACKAGE_VERSION  "0.7.0" 
#endif

/* The size of `int', as computed by sizeof. */
#ifndef DBUS_CXX_SIZEOF_INT 
#define DBUS_CXX_SIZEOF_INT  4 
#endif

/* The size of `long int', as computed by sizeof. */
#ifndef DBUS_CXX_SIZEOF_LONG_INT 
#define DBUS_CXX_SIZEOF_LONG_INT  8 
#endif

/* The size of `long long int', as computed by sizeof. */
#ifndef DBUS_CXX_SIZEOF_LONG_LONG_INT 
#define DBUS_CXX_SIZEOF_LONG_LONG_INT  8 
#endif

/* Define to 1 if you have the ANSI C header files. */
#ifndef DBUS_CXX_STDC_HEADERS 
#define DBUS_CXX_STDC_HEADERS  1 
#endif

/* If defined, boost library smart pointers will be used */
/* #undef DBUS_CXX_USE_BOOST_SMART_POINTER */

/* If defined, boost library variants will be used */
/* #undef DBUS_CXX_USE_BOOST_VARIANT */

/* If defined c++0x smart pointers will be used */
#ifndef DBUS_CXX_USE_CXX0X_SMART_POINTER 
#define DBUS_CXX_USE_CXX0X_SMART_POINTER  /**/ 
#endif

/* If defined, internal variants will be used */
#ifndef DBUS_CXX_USE_INTERNAL_VARIANT 
#define DBUS_CXX_USE_INTERNAL_VARIANT  1 
#endif

/* If defined TR1 smart pointers will be used */
/* #undef DBUS_CXX_USE_TR1_SMART_POINTER */

/* Version number of package */
#ifndef DBUS_CXX_VERSION 
#define DBUS_CXX_VERSION  "0.7.0" 
#endif
 
/* once:
_DBUS_CXX_DBUS_CXX_CONFIG_H
*/
#endif
