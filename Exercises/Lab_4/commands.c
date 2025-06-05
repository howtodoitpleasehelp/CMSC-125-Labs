#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>    
#include <sys/types.h>  
#include <sys/stat.h>   
#include <unistd.h>     
#include <time.h>       
#include <errno.h>      
#include "commands.h"

// Global simulated time variable
time_t simulated_time;

// File to store simulated time
#define TIME_FILE "simulated_time.dat"

// Initialize simulated time
void init_simulated_time(void) {
    FILE *fp = fopen(TIME_FILE, "rb");
    if (fp) {
        if (fread(&simulated_time, sizeof(time_t), 1, fp) != 1) {
            simulated_time = time(NULL);  // Use current time if read fails
        }
        fclose(fp);
    } else {
        simulated_time = time(NULL);  // Use current time if file doesn't exist
    }
}

// Save simulated time to file
void save_simulated_time(void) {
    FILE *fp = fopen(TIME_FILE, "wb");
    if (fp) {
        fwrite(&simulated_time, sizeof(time_t), 1, fp);
        fclose(fp);
    }
}

// Forward declarations of command functions
static int cmd_dir(int argc, char *argv[]);
static int cmd_cd(int argc, char *argv[]);
static int cmd_mkdir(int argc, char *argv[]);
static int cmd_rmdir(int argc, char *argv[]);
static int cmd_touch(int argc, char *argv[]);
static int cmd_del(int argc, char *argv[]);
static int cmd_type(int argc, char *argv[]);
static int cmd_cls(int argc, char *argv[]);
static int cmd_help(int argc, char *argv[]);
static int cmd_date(int argc, char *argv[]);
static int cmd_time(int argc, char *argv[]);

// DIR: List current directory
static int cmd_dir(int argc, char *argv[]) {
    DIR *d = opendir(".");
    if (!d) {
        perror("dir");
        return 1;
    }

    struct dirent *entry;
    struct stat st;
    char path[1024];
    unsigned long long totalFiles = 0;
    unsigned long long totalSize = 0;

    printf("\n Directory of %s\n\n", getcwd(path, sizeof(path)));

    while ((entry = readdir(d)) != NULL) {
        if (stat(entry->d_name, &st) == 0) {
            struct tm *tm = localtime(&st.st_mtime);
            char dateStr[20], timeStr[20];
            strftime(dateStr, sizeof(dateStr), "%m/%d/%Y", tm);
            strftime(timeStr, sizeof(timeStr), "%I:%M %p", tm);

            if (S_ISDIR(st.st_mode)) {
                printf("%s  %s    <DIR>          %s\n",
                       dateStr, timeStr, entry->d_name);
            } else {
                printf("%s  %s    %10lld %s\n",
                       dateStr, timeStr, (long long)st.st_size, entry->d_name);
                totalSize += st.st_size;
            }
            totalFiles++;
        }
    }

    printf("\n     Total Files Listed:\n");
    printf("              %llu File(s)    %llu bytes\n", totalFiles - 2, totalSize); // -2 for . and ..

    closedir(d);
    return 0;
}

// CD: Change directory
static int cmd_cd(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "cd: Missing argument\n");
        return 1;
    }

    if (chdir(argv[1]) != 0) {
        perror("cd");
        return 1;
    }

    char path[1024];
    if (getcwd(path, sizeof(path)) != NULL) {
        printf("Now in: %s\n", path);
    }
    return 0;
}

// MKDIR: Create directory
static int cmd_mkdir(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "mkdir: Missing folder name\n");
        return 1;
    }

    if (mkdir(argv[1]) != 0) {
        perror("mkdir");
        return 1;
    }

    printf("Directory '%s' created\n", argv[1]);
    return 0;
}

// RMDIR: Remove directory
static int cmd_rmdir(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "rmdir: Missing folder name\n");
        return 1;
    }

    if (rmdir(argv[1]) != 0) {
        perror("rmdir");
        return 1;
    }

    printf("Directory '%s' removed\n", argv[1]);
    return 0;
}

// TOUCH: Create empty file
static int cmd_touch(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "touch: Missing filename\n");
        return 1;
    }

    FILE *fp = fopen(argv[1], "a");
    if (!fp) {
        perror("touch");
        return 1;
    }
    fclose(fp);

    printf("File '%s' created\n", argv[1]);
    return 0;
}

// DEL: Delete file
static int cmd_del(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "del: Missing filename\n");
        return 1;
    }

    if (unlink(argv[1]) != 0) {
        perror("del");
        return 1;
    }

    printf("File '%s' deleted\n", argv[1]);
    return 0;
}

// TYPE: Display file contents
static int cmd_type(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "type: Missing filename\n");
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror("type");
        return 1;
    }

    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        printf("%s", buffer);
    }

    fclose(fp);
    return 0;
}

// CLS: Clear screen
static int cmd_cls(int argc, char *argv[]) {
    printf("\033[2J\033[H");  // ANSI escape sequence to clear screen
    return 0;
}

// HELP: Show available commands
static int cmd_help(int argc, char *argv[]) {
    printf("Available commands:\n");
    printf("  dir                - List files and folders\n");
    printf("  cd <dir>          - Change directory\n");
    printf("  cd..              - Go to parent directory\n");
    printf("  mkdir <dir>       - Create directory\n");
    printf("  rmdir <dir>       - Remove directory\n");
    printf("  touch <file>      - Create empty file\n");
    printf("  del <file>        - Delete file\n");
    printf("  type <file>       - Display file contents\n");
    printf("  cls               - Clear screen\n");
    printf("  help              - Show this help\n");
    printf("  date              - Show current date\n");
    printf("  time              - Show current time\n");
    printf("  exit              - Exit shell\n");
    return 0;
}

// DATE: Show/set simulated date
static int cmd_date(int argc, char *argv[]) {
    init_simulated_time();
    struct tm *tm_info = localtime(&simulated_time);
    char buffer[64];

    strftime(buffer, sizeof(buffer), "%m/%d/%Y", tm_info);
    printf("Current date (simulated): %s\n", buffer);

    printf("Change date? (y/n): ");
    fflush(stdout);
    char ans;
    if (scanf(" %c", &ans) != 1) {
        while (getchar() != '\n');  // Clear input buffer
        return 1;
    }
    while (getchar() != '\n');  // Clear input buffer

    if (ans == 'y' || ans == 'Y') {
        printf("Enter date (MM DD YYYY): ");
        fflush(stdout);
        int month, day, year;
        if (scanf("%d %d %d", &month, &day, &year) == 3) {
            // Validate input
            if (month < 1 || month > 12) {
                printf("Invalid month (1-12)\n");
                while (getchar() != '\n');
                return 1;
            }
            if (day < 1 || day > 31) {
                printf("Invalid day (1-31)\n");
                while (getchar() != '\n');
                return 1;
            }
            if (year < 1970 || year > 2038) {
                printf("Invalid year (1970-2038)\n");
                while (getchar() != '\n');
                return 1;
            }

            tm_info->tm_mon = month - 1;
            tm_info->tm_mday = day;
            tm_info->tm_year = year - 1900;
            tm_info->tm_isdst = -1;  // Let system determine DST

            time_t new_time = mktime(tm_info);
            if (new_time == -1) {
                printf("Invalid date combination\n");
                while (getchar() != '\n');
                return 1;
            }

            simulated_time = new_time;
            save_simulated_time();
            
            strftime(buffer, sizeof(buffer), "%m/%d/%Y", tm_info);
            printf("Date updated to: %s\n", buffer);
        } else {
            printf("Invalid input format\n");
        }
        while (getchar() != '\n');  // Clear input buffer
    }
    return 0;
}

// TIME: Show/set simulated time
static int cmd_time(int argc, char *argv[]) {
    init_simulated_time();
    struct tm *tm_info = localtime(&simulated_time);
    char buffer[64];

    strftime(buffer, sizeof(buffer), "%I:%M:%S %p", tm_info);
    printf("Current time (simulated): %s\n", buffer);

    printf("Change time? (y/n): ");
    fflush(stdout);
    char ans;
    if (scanf(" %c", &ans) != 1) {
        while (getchar() != '\n');  // Clear input buffer
        return 1;
    }
    while (getchar() != '\n');  // Clear input buffer

    if (ans == 'y' || ans == 'Y') {
        printf("Enter time (HH MM SS): ");
        fflush(stdout);
        int hour, min, sec;
        if (scanf("%d %d %d", &hour, &min, &sec) == 3) {
            // Validate input
            if (hour < 0 || hour > 23) {
                printf("Invalid hour (0-23)\n");
                while (getchar() != '\n');
                return 1;
            }
            if (min < 0 || min > 59) {
                printf("Invalid minute (0-59)\n");
                while (getchar() != '\n');
                return 1;
            }
            if (sec < 0 || sec > 59) {
                printf("Invalid second (0-59)\n");
                while (getchar() != '\n');
                return 1;
            }

            tm_info->tm_hour = hour;
            tm_info->tm_min = min;
            tm_info->tm_sec = sec;
            tm_info->tm_isdst = -1;  // Let system determine DST

            time_t new_time = mktime(tm_info);
            if (new_time == -1) {
                printf("Invalid time combination\n");
                while (getchar() != '\n');
                return 1;
            }

            simulated_time = new_time;
            save_simulated_time();
            
            strftime(buffer, sizeof(buffer), "%I:%M:%S %p", tm_info);
            printf("Time updated to: %s\n", buffer);
        } else {
            printf("Invalid input format\n");
        }
        while (getchar() != '\n');  // Clear input buffer
    }
    return 0;
}

// Command dispatcher
int handle_builtin(int argc, char *argv[]) {
    if (strcmp(argv[0], "dir") == 0) return cmd_dir(argc, argv);
    if (strcmp(argv[0], "cd") == 0) return cmd_cd(argc, argv);
    if (strcmp(argv[0], "cd..") == 0) {
        char *args[] = {"cd", ".."};
        return cmd_cd(2, args);
    }
    if (strcmp(argv[0], "mkdir") == 0) return cmd_mkdir(argc, argv);
    if (strcmp(argv[0], "rmdir") == 0) return cmd_rmdir(argc, argv);
    if (strcmp(argv[0], "touch") == 0) return cmd_touch(argc, argv);
    if (strcmp(argv[0], "del") == 0) return cmd_del(argc, argv);
    if (strcmp(argv[0], "type") == 0) return cmd_type(argc, argv);
    if (strcmp(argv[0], "cls") == 0) return cmd_cls(argc, argv);
    if (strcmp(argv[0], "help") == 0) return cmd_help(argc, argv);
    if (strcmp(argv[0], "date") == 0) return cmd_date(argc, argv);
    if (strcmp(argv[0], "time") == 0) return cmd_time(argc, argv);
    return -1;
} 