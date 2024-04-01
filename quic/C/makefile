CC := gcc
CFLAGS := -Wall -Wextra -g

#On Macos at least make sure -rpath is set to /usr/local/lib or wherever
#the libmsquic.dylib is installed
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  LDFLAGS :=  -lmsquic -lm -lpthread  -rpath /usr/local/lib
endif
ifeq ($(UNAME_S),Linux)
	LDFLAGS :=  -lmsquic -lm -lpthread  
endif

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

.PHONY:
run_server:
	./$(TARGET) -server -cert_file:./certs/quic_certificate.crt -key_file:./certs/quic_private_key.pem

.PHONY:
run_client:
	./$(TARGET) -client -unsecure -target:localhost

