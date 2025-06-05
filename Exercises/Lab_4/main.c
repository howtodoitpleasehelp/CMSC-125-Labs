#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "commands.h"

#define MAX_ARGS 10
#define MAX_INPUT 1024

int main() {
    char line[MAX_INPUT];
    char *argv[MAX_ARGS];
    int argc;

    while (1) {
        printf("> ");
        fflush(stdout);

        if (fgets(line, sizeof(line), stdin) == NULL) break;
        
        // Remove newline
        line[strcspn(line, "\n")] = 0;

        if (strlen(line) == 0) continue;

        // Parse command line
        argc = 0;
        char *token = strtok(line, " ");
        while (token && argc < MAX_ARGS - 1) {
            argv[argc++] = token;
            token = strtok(NULL, " ");
        }
        argv[argc] = NULL;

        if (argc == 0) continue;

        if (strcmp(argv[0], "exit") == 0) break;

        if (handle_builtin(argc, argv) == -1) {
            printf("Unknown command: %s\n", argv[0]);
        }
    }
    return 0;
}
