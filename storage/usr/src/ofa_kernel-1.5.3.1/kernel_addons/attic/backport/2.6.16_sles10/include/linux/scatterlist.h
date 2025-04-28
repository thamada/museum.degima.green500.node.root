#ifndef __BACKPORT_LINUX_SCATTERLIST_H_TO_2_6_23__
#define __BACKPORT_LINUX_SCATTERLIST_H_TO_2_6_23__
#include_next<linux/scatterlist.h>

static inline void sg_set_page(struct scatterlist *sg, struct page *page,
                               unsigned int len, unsigned int offset)
{
	sg->page = page;
	sg->offset = offset;
	sg->length = len;
}

static inline void sg_assign_page(struct scatterlist *sg, struct page *page)
{
	sg->page = page;
}

#define sg_page(a) (a)->page
#define sg_init_table(a, b)

#define for_each_sg(sglist, sg, nr, __i)	\
	for (__i = 0, sg = (sglist); __i < (nr); __i++, sg++)

static inline struct scatterlist *sg_next(struct scatterlist *sg)
{
	if (!sg) {
		BUG();
		return NULL;
	}
	return sg + 1;
}

#endif
