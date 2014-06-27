#
# Testing for Cooperativity demos in ErLam
#

# Compiler Dependency:
ERLAM_URL='https://github.com/dstar4138/erlam.git'
ELS=$(CURDIR)/deps/erlam/bin/els

# Directory Structure
RUN_ALL_TESTS=$(CURDIR)/bin/run_all.escript
SRC_DIR=$(CURDIR)/src
OUT_DIR=$(CURDIR)/results

.PHONY: all run run-png tests clean distclean

all: deps tests

run: 
	-mkdir $(OUT_DIR)
	$(RUN_ALL_TESTS) $(SRC_DIR) $(OUT_DIR)

run-png:
	-mkdir $(OUT_DIR)
	$(RUN_ALL_TESTS) --png $(SRC_DIR) $(OUT_DIR)

deps:
	mkdir deps
	cd deps ; git clone $(ERLAM_URL)
	cd deps/erlam ; make

tests:
	$(ELS) src/*.els
	chmod +x src/*.ex

clean:
	-rm src/*.els

distclean: clean
	-rm -rf deps
	-rm -r $(OUT_DIR)

