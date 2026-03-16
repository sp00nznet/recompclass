CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
TARGET  = test_bridge

SRCS = dma_bridge.c test_bridge.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

%.o: %.c dma_bridge.h
	$(CC) $(CFLAGS) -c $< -o $@

test: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all test clean
