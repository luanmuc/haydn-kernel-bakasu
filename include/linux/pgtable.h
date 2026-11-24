#ifndef _LINUX_PGTABLE_H
#define _LINUX_PGTABLE_H

/*
 * 5.4 compatibility shim for KernelSU/SukiSU-Nova sources that include
 * <linux/pgtable.h>.  The split linux/pgtable.h header only appeared in
 * later kernels; on 5.4 the definitions live in asm/pgtable.h and
 * asm-generic/pgtable.h.
 */
#include <asm/pgtable.h>
#include <asm-generic/pgtable.h>

#endif /* _LINUX_PGTABLE_H */
