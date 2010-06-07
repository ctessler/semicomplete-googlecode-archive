#include "xdo_cmd.h"

int cmd_windowsize(context_t *context) {
  int ret = 0;
  int width, height;
  int c;

  int use_hints = 0;
  struct option longopts[] = {
    { "usehints", 0, NULL, 'u' },
    { "help", no_argument, NULL, 'h' },
    { 0, 0, 0, 0 },
  };

  int size_flags = 0;
  char *cmd = *context->argv;
  int option_index;
  static const char *usage =
            "Usage: %s [--usehints] windowid width height\n" \
            "--usehints  - Use window sizing hints (like font size in terminals)\n";

  while ((c = getopt_long_only(context->argc, context->argv, "uh",
                               longopts, &option_index)) != -1) {
    switch (c) {
      case 'h':
        printf(usage, cmd);
        consume_args(context, context->argc);
        return EXIT_SUCCESS;
      case 'u':
        use_hints = 1;
        break;
      default:
        fprintf(stderr, usage, cmd);
        return EXIT_FAILURE;
    }
  }

  if (use_hints) {
    size_flags |= SIZE_USEHINTS;
  }

  consume_args(context, optind);

  if (context->argc < 3) {
    fprintf(stderr, usage, cmd);
    fprintf(stderr, "Invalid argument count, got %d, expected %d\n", 
            3, context->argc);
    return EXIT_FAILURE;
  }

  width = (int)strtol(context->argv[1], NULL, 0);
  height = (int)strtol(context->argv[2], NULL, 0);

  window_each(context, context->argv[0], {
    ret = xdo_window_setsize(context->xdo, window, width, height, size_flags);
    if (ret) {
      fprintf(stderr, "xdo_window_setsize on window:%ld reported an error\n",
              window);
      return ret;
    }
  }); /* window_each(...) */
  consume_args(context, 3);

  return ret;
}

