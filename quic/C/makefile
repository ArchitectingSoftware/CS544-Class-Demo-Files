CC := gcc
CFLAGS := -Wall -Wextra -g

#On Macos at least make sure -rpath is set to /usr/local/lib or wherever
#the libmsquic.dylib is installed
LDFLAGS :=  -lmsquic -lm -lpthread  -rpath /usr/local/lib

SRCDIR := .
BINDIR := bin
TARGET := echo

SRCFILES := $(wildcard $(SRCDIR)/*.c)
OBJFILES := $(patsubst $(SRCDIR)/%.c,$(BINDIR)/%.o,$(SRCFILES))

.PHONY: all clean

all: $(BINDIR) $(TARGET)

$(BINDIR):
	mkdir -p $(BINDIR)

$(BINDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJFILES)
	$(CC) $(OBJFILES) -o $(TARGET) $(LDFLAGS)

clean:
	rm -rf $(BINDIR) $(TARGET)
