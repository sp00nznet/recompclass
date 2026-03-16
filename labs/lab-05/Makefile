CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
LDFLAGS =

# Source files
BUS_SRC = memory_bus.c
TEST_SRC = test_bus.c

# Object files
BUS_OBJ = memory_bus.o
TEST_OBJ = test_bus.o

# Output binary
TEST_BIN = test_bus

.PHONY: all clean test

all: $(TEST_BIN)

$(TEST_BIN): $(BUS_OBJ) $(TEST_OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

$(BUS_OBJ): memory_bus.c memory_bus.h
	$(CC) $(CFLAGS) -c -o $@ $<

$(TEST_OBJ): test_bus.c memory_bus.h
	$(CC) $(CFLAGS) -c -o $@ $<

test: $(TEST_BIN)
	./$(TEST_BIN)

clean:
	rm -f $(BUS_OBJ) $(TEST_OBJ) $(TEST_BIN)
