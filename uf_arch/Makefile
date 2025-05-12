# Compiler and flags
CC = g++
CFLAGS = -Wall -Wextra -g -O3

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin
BINDS_DIR = binds

# Target executable
TARGET = $(BIN_DIR)/program

# Source and object files
SRCS = $(wildcard $(SRC_DIR)/*.cpp)
OBJS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))

BIND_SRC = $(BINDS_DIR)/binds.cpp
BIND_OBJ = uf_arch$(shell python3-config --extension-suffix)

# Default target
all: $(TARGET)

# Link object files to create the executable
$(TARGET): $(OBJS)
	mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -o $@ $^

# Compile source files to object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BIND_OBJ): $(BIND_SRC) $(OBJS)
	$(CC) -O3 -Wall -shared -std=c++11 -fPIC $(shell python3 -m pybind11 --includes) -I/usr/include/python3.12 $(BIND_SRC) obj/union_find.o -o $(BIND_OBJ)

# Run the program
run: $(TARGET)
	@$(TARGET)

# Clean build files
clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR) $(BIND_OBJ) $(TARGET)

# Generate bindings module
binds: $(BIND_OBJ)

.PHONY: all clean