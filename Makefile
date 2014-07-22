#
# Testing for Cooperativity demos in ErLam
#

# Compiler Dependency:
ERLAM_URL='https://github.com/dstar4138/erlam.git'
ELS=$(CURDIR)/deps/erlam/bin/els

# Dynamic Scripts:
COMPOSE=$(CURDIR)/bin/compose_els.py

# Directory Structure
RUN_ALL_TESTS=$(CURDIR)/bin/run_all.py
SRC_DIR=$(CURDIR)/src
OUT_DIR=$(CURDIR)/results

.PHONY: all run run-png tests clean distclean

all: deps tests

run: all 
	-mkdir $(OUT_DIR)
	$(RUN_ALL_TESTS) $(SRC_DIR) $(OUT_DIR)

deps:
	mkdir deps
	cd deps ; git clone $(ERLAM_URL)
	cd deps/erlam ; make

tests: build_compose
	$(ELS) src/*.els
	chmod +x src/*.ex

clean:
	-rm src/*.ex

distclean: clean
	-rm -rf deps
	-rm -r $(OUT_DIR)

build_compose:
	$(COMPOSE) $(SRC_DIR) ./bin/ptree.els_tmp $(SRC_DIR)/ptree.els
	$(COMPOSE) $(SRC_DIR) ./bin/interactivity.els_tmp $(SRC_DIR)/interactivity.els
	$(COMPOSE) $(SRC_DIR) ./bin/unstructured1.els_tmp $(SRC_DIR)/unstructured1.els
