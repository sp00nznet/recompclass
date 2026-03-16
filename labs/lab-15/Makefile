CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g $(shell sdl2-config --cflags)
LDFLAGS = $(shell sdl2-config --libs)

.PHONY: all clean

all: graphics_demo

graphics_bridge.o: graphics_bridge.c graphics_bridge.h
	$(CC) $(CFLAGS) -c graphics_bridge.c -o graphics_bridge.o

graphics_demo: main.c graphics_bridge.o graphics_bridge.h
	$(CC) $(CFLAGS) main.c graphics_bridge.o -o graphics_demo $(LDFLAGS)

clean:
	rm -f *.o graphics_demo
