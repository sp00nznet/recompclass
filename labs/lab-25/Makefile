CC = gcc
CFLAGS = -Wall -Wextra -I.

all: test_lifted

test_lifted: test_lifted.c lifted.c z80_runtime.h
	$(CC) $(CFLAGS) -o test_lifted test_lifted.c lifted.c

test: test_lifted
	./test_lifted

clean:
	rm -f test_lifted test_lifted.exe

.PHONY: all test clean
