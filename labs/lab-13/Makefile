CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
LDFLAGS =

.PHONY: all clean test

all: test_flags

flags.o: flags.c flags.h
	$(CC) $(CFLAGS) -c flags.c -o flags.o

test_flags: test_flags.c flags.o flags.h
	$(CC) $(CFLAGS) test_flags.c flags.o -o test_flags $(LDFLAGS)

test: test_flags
	./test_flags

clean:
	rm -f *.o test_flags
