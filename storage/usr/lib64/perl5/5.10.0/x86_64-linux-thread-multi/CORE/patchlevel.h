/*    patchlevel.h
 *
 *    Copyright (C) 1993, 1995, 1996, 1997, 1998, 1999, 2000, 2001,
 *    2002, 2003, 2004, 2005, 2006, 2007, by Larry Wall and others
 *
 *    You may distribute under the terms of either the GNU General Public
 *    License or the Artistic License, as specified in the README file.
 *
 */

#ifndef __PATCHLEVEL_H_INCLUDED__

/* do not adjust the whitespace! Configure expects the numbers to be
 * exactly on the third column */

#define PERL_REVISION	5		/* age */
#define PERL_VERSION	10		/* epoch */
#define PERL_SUBVERSION	0		/* generation */

/* The following numbers describe the earliest compatible version of
   Perl ("compatibility" here being defined as sufficient binary/API
   compatibility to run XS code built with the older version).
   Normally this should not change across maintenance releases.

   Note that this only refers to an out-of-the-box build.  Many non-default
   options such as usemultiplicity tend to break binary compatibility
   more often.

   This is used by Configure et al to figure out 
   PERL_INC_VERSION_LIST, which lists version libraries
   to include in @INC.  See INSTALL for how this works.
*/
#define PERL_API_REVISION	5	/* Adjust manually as needed.  */
#define PERL_API_VERSION	10	/* Adjust manually as needed.  */
#define PERL_API_SUBVERSION	0	/* Adjust manually as needed.  */
/*
   XXX Note:  The selection of non-default Configure options, such
   as -Duselonglong may invalidate these settings.  Currently, Configure
   does not adequately test for this.   A.D.  Jan 13, 2000
*/

#define __PATCHLEVEL_H_INCLUDED__
#endif

/*
	local_patches -- list of locally applied less-than-subversion patches.
	If you're distributing such a patch, please give it a name and a
	one-line description, placed just before the last NULL in the array
	below.  If your patch fixes a bug in the perlbug database, please
	mention the bugid.  If your patch *IS* dependent on a prior patch,
	please place your applied patch line after its dependencies. This
	will help tracking of patch dependencies.

	Please either use 'diff --unified=0' if your diff supports
	that or edit the hunk of the diff output which adds your patch
	to this list, to remove context lines which would give patch
	problems. For instance, if the original context diff is

	   *** patchlevel.h.orig	<date here>
	   --- patchlevel.h	<date here>
	   *** 38,43 ***
	   --- 38,44 ---
	     	,"FOO1235 - some patch"
	     	,"BAR3141 - another patch"
	     	,"BAZ2718 - and another patch"
	   + 	,"MINE001 - my new patch"
	     	,NULL
	     };
	
	please change it to 
	   *** patchlevel.h.orig	<date here>
	   --- patchlevel.h	<date here>
	   *** 41,43 ***
	   --- 41,44 ---
	   + 	,"MINE001 - my new patch"
	     	,NULL
	     };
	
	(Note changes to line numbers as well as removal of context lines.)
	This will prevent patch from choking if someone has previously
	applied different patches than you.

        History has shown that nobody distributes patches that also
        modify patchlevel.h. Do it yourself. The following perl
        program can be used to add a comment to patchlevel.h:

#!perl
die "Usage: perl -x patchlevel.h comment ..." unless @ARGV;
open PLIN, "patchlevel.h" or die "Couldn't open patchlevel.h : $!";
open PLOUT, ">patchlevel.new" or die "Couldn't write on patchlevel.new : $!";
my $seen=0;
while (<PLIN>) {
    if (/\t,NULL/ and $seen) {
       while (my $c = shift @ARGV){
            print PLOUT qq{\t,"$c"\n};
       }
    }
    $seen++ if /local_patches\[\]/;
    print PLOUT;
}
close PLOUT or die "Couldn't close filehandle writing to patchlevel.new : $!";
close PLIN or die "Couldn't close filehandle reading from patchlevel.h : $!";
close DATA; # needed to allow unlink to work win32.
unlink "patchlevel.bak" or warn "Couldn't unlink patchlevel.bak : $!"
  if -e "patchlevel.bak";
rename "patchlevel.h", "patchlevel.bak" or
  die "Couldn't rename patchlevel.h to patchlevel.bak : $!";
rename "patchlevel.new", "patchlevel.h" or
  die "Couldn't rename patchlevel.new to patchlevel.h : $!";
__END__

Please keep empty lines below so that context diffs of this file do
not ever collect the lines belonging to local_patches() into the same
hunk.

 */

#if !defined(PERL_PATCHLEVEL_H_IMPLICIT) && !defined(LOCAL_PATCH_COUNT)
static const char * const local_patches[] = {
	NULL
	,"Fedora Patch1: Permit suidperl to install as nonroot"
	,"Fedora Patch2: Removes date check, Fedora/RHEL specific"
	,"Fedora Patch4: Work around annoying rpath issue"
	,"Fedora Patch5: support for libdir64"
	,"Fedora Patch6: use libresolv instead of libbind"
	,"Fedora Patch7: USE_MM_LD_RUN_PATH"
	,"Fedora Patch8: Skip hostname tests, due to builders not being network capable"
	,"Fedora Patch10: Dont run one io test due to random builder failures"
	,"32891 fix big slowdown in 5.10 @_ parameter passing"
	,"Fedora Patch15: Adopt upstream commit for assertion"
	,"Fedora Patch16: Access permission - rt49003"
	,"Fedora Patch20: pos function handle unicode correct"
	,"Fedora Patch26: Fix crash when localizing a symtab entry - rt52740"
	,"33640 Integrate Changes 33399, 33621, 33622, 33623, 33624"
	,"33881 Integrate Changes 33825, 33826, 33829"
	,"33896 Eliminate POSIX::int_macro_int, and all the complex AUTOLOAD fandango"
	,"33897 Replaced the WEXITSTATUS, WIFEXITED, WIFSIGNALED, WIFSTOPPED, WSTOPSIG"
	,"54934 Change 34025 refcount of the globs generated by PerlIO::via balanced"
	,"34507 Fix memory leak in single-char character class optimization"
	,"Fedora Patch35: Reorder @INC, based on b9ba2fadb18b54e35e5de54f945111a56cbcb249"
	,"Fedora Patch36: Fix from Archive::Extract maintainer to only look at stdout from tar"
	,"Fedora Patch37: Do not distort lib/CGI/t/util-58.t"
	,"32727 Fix issue with (nested) definition lists in lib/Pod/Html.pm"
	,"33287 Fix NULLOK items"
	,"33554 Fix a typo in the predefined common protocols to make _udp_ resolve without netbase"
	,"33388 Fix a segmentation fault with debugperl -Dm"
	,"33835 Allow the quote mark delimiter also for those #include directives chased with h2ph -a."
	,"32910 Disable the v-string in use/require is non-portable warning."
	,"33807 Fix a segmentation fault occurring in the mod_perl2 test suite."
	,"33370 Fix the PerlIO_teardown prototype to suppress a compiler warning."
	,"Fedora Patch48: Remove numeric overloading of Getopt::Long callback functions."
	,"33821 Fix Math::BigFloat::sqrt() breaking with too many digits."
	,"33937 Fix memory corruption with in-place sorting"
	,"33732 Revert an incorrect substitution optimization introduced in 5.10.0"
	,"33265 Fix Unknown error messages with attribute.pm."
	,"33749 Stop t/op/fork.t relying on rand()"
	,"34506 Fix memory leak with qr//"
	,"Fedora Patch55: File::Path::rmtree no longer allows creating of setuid files."
	,"Fedora Patch56: Fix $? when dumping core"
	,"34209 Fix a memory leak with Scalar::Util::weaken()"
	,"fix RT 39060, errno incorrectly set in perlio"
	,"Fedora Patch59: h2ph: generated *.ph files no longer produce warnings when processed"
	,"Fedora Patch60: remove PREREQ_FATAL from Makefile.PLs processed by miniperl"
	,"Fedora Patch61: much better swap logic to support reentrancy and fix assert failure"
	,"Fedora Patch62: Fix paths to Encode"
	,"Fedora Patch63: Fix nested loop variable free warning"
	,"Fedora Patch100: Update module constant to 1.17"
	,"Fedora Patch101: Update Archive::Extract to 0.30"
	,"Fedora Patch102: Update Archive::Tar to 1.62"
	,"Fedora Patch103: Update CGI to 3.43"
	,"Fedora Patch104: Update ExtUtils::CBuilder to 0.24"
	,"Fedora Patch105: Update File::Fetch to 0.18"
	,"Fedora Patch106: Update File::Path to 2.07"
	,"Fedora Patch107: Update File::Temp to 0.21"
	,"Fedora Patch108: Update IPC::Cmd to 0.42"
	,"Fedora Patch109: Update Module::Build to %{Module_Build_version}"
	,"Fedora Patch110: Update Module::CoreList to 2.17"
	,"Fedora Patch111: Update Module::Load::Conditional to 0.30"
	,"Fedora Patch112: Update Pod::Simple to 3.07"
	,"Fedora Patch113: Update Sys::Syslog to 0.27"
	,"Fedora Patch114: Update Test::Harness to 3.16"
	,"Fedora Patch115: Update Test::Simple to 0.92"
	,"Fedora Patch116: Update Time::HiRes to 1.9719"
	,"Fedora Patch117: Update Digest::SHA to 5.47"
	,"Fedora Patch117: Update module autodie to 1.999"
	,"Fedora Patch119: Update File::Spec to 3.30"
	,"Fedora Patch120: Update Compress::Raw::Zlib to 2.023"
	,"Fedora Patch121: Update Scalar-List-Utils to 1.21"
	,"Fedora Patch122: Update Module-Pluggable to 3.90"
	,"Fedora Patch123: Update Storable to 2.21"
	,"Fedora Patch124: Update IO::Compress::Base to 2.015"
	,"Fedora Patch125: Update IO::Compress::Zlib to 2.015"
	,"Fedora Patch126: Update Safe to 2.27"
	,"Fedora Patch127: Update threads to 1.79 "
	,"Fedora Patch128: Update threads::shared to 1.34"
	,"Fedora Patch129: Update Thread::Queue to 2.11"
	,"Fedora Patch130: Fix files in MANIFEST "
	,"Fedora Patch201: Fedora uses links instead of lynx"
	,"Fedora Patch202: RT#73814 - unpack scalar context correctly "
	,"Fedora Patch203: Fix taint.t test in Test::Harness "
	,NULL
};



/* Initial space prevents this variable from being inserted in config.sh  */
#  define	LOCAL_PATCH_COUNT	\
	((int)(sizeof(local_patches)/sizeof(local_patches[0])-2))

/* the old terms of reference, add them only when explicitly included */
#define PATCHLEVEL		PERL_VERSION
#undef  SUBVERSION		/* OS/390 has a SUBVERSION in a system header */
#define SUBVERSION		PERL_SUBVERSION
#endif
