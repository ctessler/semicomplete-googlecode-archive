#ifndef _GROK_MATCHCONF_H_
#define _GROK_MATCHCONF_H_

#include "grok.h"
#include "grok_program.h"
#include "grok_matchconf.h"

typedef struct grok_matchconf grok_matchconf_t;
typedef struct grok_reaction grok_reaction_t;

struct grok_reaction {
  char *cmd;
};

struct grok_matchconf {
  grok_t grok; /* The grok pattern to match */
  char *reaction;
  char *shell;
  int flush; /* flush on every write to the shell? */

  FILE *shellinput; /* fd to write reactions to */
  int pid; /* pid of shell */
};

void grok_matchconfig_exec(grok_program_t *gprog, grok_matchconf_t *gmc,
                           const char *text);
void grok_matchconfig_start_shell(grok_program_t *gprog, grok_matchconf_t *gmc);
char *grok_matchconfig_filter_reaction(const char *str, grok_match_t *gm);


#endif /*  _GROK_MATCHCONF_H_ */
