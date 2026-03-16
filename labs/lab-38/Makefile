CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
TARGET  = test_shim

SRCS = d3d8_shim.c test_shim.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

%.o: %.c d3d8_shim.h
	$(CC) $(CFLAGS) -c $< -o $@

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all test clean
