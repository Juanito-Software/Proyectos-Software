
CC = gcc
AR = ar
RM = rm -f
RMDIR = rm -rf

CFLAGS = -std=c17 -Wall -Wextra -Wpedantic -Werror
CPPFLAGS = -Iinclude -Isrc/V2

BUILD_DIR = build
LIBRARY = libforge.a
EXECUTABLE = forge.exe

LIB_SOURCES = \
    src/V1/forge_info.c \
	src/V1/forge_status.c \
	src/V1/validate_fga.c \
	src/V1/forge_pack.c \
	src/V1/forge_unpack.c \
	src/V2/forge_fga2_validate.c \
	src/V2/forge_fga2_write.c \
	src/V2/forge_fga2_pack.c \
	src/V2/forge_fga2_unpack.c \
	src/V2/forge_fga2_info.c \
	src/V2/forge_fga2_list.c

LIB_OBJECTS = $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(LIB_SOURCES))
CLI_OBJECT = $(BUILD_DIR)/forge.o

.PHONY: all clean test

all: $(LIBRARY) $(EXECUTABLE)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/V1 $(BUILD_DIR)/V2:
	mkdir -p $@

$(BUILD_DIR)/%.o: src/%.c include/forge.h | $(BUILD_DIR)
	mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(CLI_OBJECT): src/V1/forge.c include/forge.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(LIBRARY): $(LIB_OBJECTS)
	$(AR) rcs $@ $^

$(EXECUTABLE): $(CLI_OBJECT) $(LIBRARY)
	$(CC) $(CFLAGS) $(CLI_OBJECT) $(LIBRARY) -o $@

clean:
	$(RMDIR) $(BUILD_DIR)
	$(RM) $(LIBRARY) $(EXECUTABLE)

test: $(EXECUTABLE)
	powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_forge.ps1
