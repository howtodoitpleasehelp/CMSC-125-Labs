CC=gcc
CFLAGS=-Wall -g

all: mysh

mysh: main.o commands.o
	$(CC) $(CFLAGS) -o mysh main.o commands.o

main.o: main.c commands.h
	$(CC) $(CFLAGS) -c main.c

commands.o: commands.c commands.h
	$(CC) $(CFLAGS) -c commands.c

clean:
	rm -f *.o mysh
