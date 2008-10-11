#ifndef _LOGGING_H_
#define _LOGGING_H_

#include "grok.h"

#define LOG_PREDICATE (1 << 0)
#define LOG_COMPILE (1 << 1)
#define LOG_EXEC (1 << 2)
#define LOG_REGEXPAND (1 << 3)
#define LOG_PATTERNS (1 << 4)
#define LOG_MATCH (1 << 5)
#define LOG_CAPTURE (1 << 6)

#define LOG_ALL (~0)

#ifdef NOLOGGING
/* this 'args...' requires GNU C */
#  define grok_log(grok, level, format, args...) { }
#else
void grok_log(grok_t *grok, int level, const char *format, ...);
#endif

#endif /* _LOGGING_H_ */
