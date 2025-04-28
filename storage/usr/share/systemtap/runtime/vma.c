/* -*- linux-c -*- 
 * VMA tracking and lookup functions.
 *
 * Copyright (C) 2005-2010 Red Hat Inc.
 * Copyright (C) 2006 Intel Corporation.
 *
 * This file is part of systemtap, and is free software.  You can
 * redistribute it and/or modify it under the terms of the GNU General
 * Public License (GPL); either version 2, or (at your option) any
 * later version.
 */

#ifndef _STP_VMA_C_
#define _STP_VMA_C_

#include "sym.h"
#include "string.c"
#include "task_finder_vma.c"

#include <asm/uaccess.h>

static void _stp_vma_match_vdso(struct task_struct *tsk)
{
/* vdso is arch specific */
#ifdef STAPCONF_MM_CONTEXT_VDSO
  int i, j;
  if (tsk->mm)
    {
      struct _stp_module *found = NULL;
      unsigned long vdso_addr = (unsigned long) tsk->mm->context.vdso;
#ifdef DEBUG_TASK_FINDER_VMA
      _dbug("tsk: %d vdso: 0x%lx\n", tsk->pid, vdso_addr);
#endif
      for (i = 0; i < _stp_num_modules && found == NULL; i++) {
	struct _stp_module *m = _stp_modules[i];
	if (m->path[0] == '/'
	    && m->num_sections == 1
	    && strncmp(m->name, "vdso", 4) == 0)
	  {
	    unsigned long notes_addr;
	    int all_ok = 1;
	    notes_addr = vdso_addr + m->build_id_offset - m->build_id_len;
#ifdef DEBUG_TASK_FINDER_VMA
	    _dbug("notes_addr %s: 0x%lx\n", m->name, notes_addr);
#endif
	    for (j = 0; j < m->build_id_len; j++)
	      {
		int rc;
		unsigned char b;
		/* We are called from the task_finder, so it should be
		   save to just copy_from_user here. utrace callback. */
		rc = copy_from_user(&b, (void*)(notes_addr + j), 1);
		if (rc || b != m->build_id_bits[j])
		  {
#ifdef DEBUG_TASK_FINDER_VMA
		    _dbug("darn, not equal (rc=%d) at %d (%d != %d)\n",
			  rc, j, b, m->build_id_bits[j]);
#endif
		    all_ok = 0;
		    break;
		  }
	      }
	    if (all_ok)
	      found = m;
	  }
      }
      if (found != NULL)
	{
	  stap_add_vma_map_info(tsk, vdso_addr,
				vdso_addr + found->sections[0].size,
				"vdso", found);
#ifdef DEBUG_TASK_FINDER_VMA
	  _dbug("found vdso: %s\n", found->path);
#endif
	}
    }
#endif /* STAPCONF_MM_CONTEXT_VDSO */
}

/* exec callback, will try to match vdso for new process,
   will drop all vma maps for a process that disappears. */
static int _stp_vma_exec_cb(struct stap_task_finder_target *tgt,
			    struct task_struct *tsk,
			    int register_p,
			    int process_p)
{
#ifdef DEBUG_TASK_FINDER_VMA
  _stp_dbug(__FUNCTION__, __LINE__,
	    "tsk %d:%d , register_p: %d, process_p: %d\n",
	    tsk->pid, tsk->tgid, register_p, process_p);
#endif
  if (process_p)
    {
      if (register_p)
	_stp_vma_match_vdso(tsk);
      else
	stap_drop_vma_maps(tsk);
    }

  return 0;
}

/* mmap callback, will match new vma with _stp_module or register vma name. */
static int _stp_vma_mmap_cb(struct stap_task_finder_target *tgt,
			    struct task_struct *tsk,
			    char *path, struct dentry *dentry,
			    unsigned long addr,
			    unsigned long length,
			    unsigned long offset,
			    unsigned long vm_flags)
{
	int i, res;
	struct _stp_module *module = NULL;
	const char *name = (dentry != NULL) ? dentry->d_name.name : NULL;

#ifdef DEBUG_TASK_FINDER_VMA
	_stp_dbug(__FUNCTION__, __LINE__,
		  "mmap_cb: tsk %d:%d path %s, addr 0x%08lx, length 0x%08lx, offset 0x%lx, flags 0x%lx\n",
		  tsk->pid, tsk->tgid, path, addr, length, offset, vm_flags);
#endif
	// We are only interested in the first load of the whole module that
	// is executable. We register whether or not we know the module,
	// so we can later lookup the name given an address for this task.
	if (path != NULL && offset == 0 && (vm_flags & VM_EXEC)) {
		for (i = 0; i < _stp_num_modules; i++) {
			if (strcmp(path, _stp_modules[i]->path) == 0)
			{
#ifdef DEBUG_TASK_FINDER_VMA
			  _stp_dbug(__FUNCTION__, __LINE__,
				    "vm_cb: matched path %s to module (sec: %s)\n",
				    path, _stp_modules[i]->sections[0].name);
#endif
			  module = _stp_modules[i];
			  /* XXX We really only need to register .dynamic
			     sections, but .absolute exes are also necessary
			     atm. */
			  res = stap_add_vma_map_info(tsk->group_leader,
						      addr, addr + length,
						      name, module);
			  /* Warn, but don't error out. */
			  if (res != 0)
				_stp_warn ("Couldn't register module '%s' for pid %d\n", _stp_modules[i]->path, tsk->group_leader->pid);
			  return 0;
			}
		}

		/* None of the tracked modules matched, register without,
		 * to make sure we can lookup the name later. Ignore errors,
		 * we will just report unknown when asked and tables were
		 * full. Restrict to target process when given to preserve
		 * vma_map entry slots. */
		if (_stp_target == 0
		    || _stp_target == tsk->group_leader->pid)
		  {
		    res = stap_add_vma_map_info(tsk->group_leader, addr,
						addr + length, name, NULL);
#ifdef DEBUG_TASK_FINDER_VMA
		    _stp_dbug(__FUNCTION__, __LINE__,
			      "registered '%s' for %d (res:%d)\n",
			      name, tsk->group_leader->pid,
			      res);
#endif
		  }

	}
	return 0;
}

/* munmap callback, removes vma map info. */
static int _stp_vma_munmap_cb(struct stap_task_finder_target *tgt,
			      struct task_struct *tsk,
			      unsigned long addr,
			      unsigned long length)
{
        /* Unconditionally remove vm map info, ignore if not present. */
	stap_remove_vma_map_info(tsk->group_leader, addr);
	return 0;
}

/* Initializes the vma tracker. */
static int _stp_vma_init(void)
{
        int rc = 0;
#if defined(CONFIG_UTRACE)
        static struct stap_task_finder_target vmcb = {
                // NB: no .pid, no .procname filters here.
                // This means that we get a system-wide mmap monitoring
                // widget while the script is running. (The
                // system-wideness may be restricted by stap -c or
                // -x.)  But this seems to be necessary if we want to
                // to stack tracebacks through arbitrary shared libraries.
                //
                // XXX: There may be an optimization opportunity
                // for executables (for which the main task-finder
                // callback should be sufficient).
                .pid = 0,
                .procname = NULL,
                .callback = &_stp_vma_exec_cb,
                .mmap_callback = &_stp_vma_mmap_cb,
                .munmap_callback = &_stp_vma_munmap_cb,
                .mprotect_callback = NULL
        };
	stap_initialize_vma_map ();
#ifdef DEBUG_TASK_FINDER_VMA
	_stp_dbug(__FUNCTION__, __LINE__,
		  "registering vmcb (_stap_target: %d)\n", _stp_target);
#endif
	rc = stap_register_task_finder_target (& vmcb);
	if (rc != 0)
		_stp_error("Couldn't register task finder target: %d\n", rc);
#endif
	return rc;
}

#endif /* _STP_VMA_C_ */
