CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
LDFLAGS =

.PHONY: all clean test

all: test_spu

spu_sim.o: spu_sim.c spu_sim.h
	$(CC) $(CFLAGS) -c spu_sim.c -o spu_sim.o

test_spu: test_spu.c spu_sim.o spu_sim.h
	$(CC) $(CFLAGS) test_spu.c spu_sim.o -o test_spu $(LDFLAGS)

test: test_spu
	./test_spu

clean:
	rm -f *.o test_spu
