CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -g
LDFLAGS =

# Source files
RUNTIME_SRC = runtime.c
OUTPUT_SRC  = output.c

# Object files
RUNTIME_OBJ = runtime.o
OUTPUT_OBJ  = output.o

# Final binary
TARGET = mini_gb

.PHONY: all clean recomp run

all: $(TARGET)

$(TARGET): $(RUNTIME_OBJ) $(OUTPUT_OBJ)
	$(CC) $(LDFLAGS) -o $@ $^

$(RUNTIME_OBJ): runtime.c runtime.h
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUTPUT_OBJ): output.c runtime.h
	$(CC) $(CFLAGS) -c -o $@ $<

# Run the recompiler to generate output.c, then build
recomp:
	python mini_recomp.py
	$(MAKE) all

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(RUNTIME_OBJ) $(OUTPUT_OBJ) $(TARGET) output.c
