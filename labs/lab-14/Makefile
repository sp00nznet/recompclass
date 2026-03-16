CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
LDFLAGS =

.PHONY: all clean test

all: test_shim

kernel_shim.o: kernel_shim.c kernel_shim.h
	$(CC) $(CFLAGS) -c kernel_shim.c -o kernel_shim.o

test_shim: test_shim.c kernel_shim.o kernel_shim.h
	$(CC) $(CFLAGS) test_shim.c kernel_shim.o -o test_shim $(LDFLAGS)

test: test_shim
	./test_shim

clean:
	rm -f *.o test_shim
