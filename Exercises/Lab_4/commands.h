#ifndef COMMANDS_H
#define COMMANDS_H

#include <time.h>

// Function to handle built-in commands
int handle_builtin(int argc, char *argv[]);

// Simulated time functions
extern time_t simulated_time;
void init_simulated_time(void);
void save_simulated_time(void);

#endif 
