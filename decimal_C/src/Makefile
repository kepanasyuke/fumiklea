CC := gcc
C_FLAGS := -Wall -Werror -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L
GCOV_FLAGS := -fprofile-arcs -ftest-coverage
OBJ_DIR = ./objectFiles
TEST_DIR = ./test
GCOV_REPORT_DIR = ./gcov_report
TEST.OUT = test.out
UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S), Linux)
	TEST_LIBS := -lcheck -lm -lsubunit
else ifeq ($(UNAME_S), Darwin)
	TEST_LIBS := -lcheck
endif

all: s21_decimal.a

s21_decimal.a:
	rm -f s21_decimal.a
	rm -rf $(OBJ_DIR)
	mkdir $(OBJ_DIR)
	$(CC) $(C_FLAGS) -c s21_decimal.c -o $(OBJ_DIR)/s21_decimal.o
	ar r s21_decimal.a $(OBJ_DIR)/*.o

test: s21_decimal.a
	rm -rf $(TEST_DIR)
	mkdir $(TEST_DIR)
	$(CC) $(C_FLAGS) tests.c -L . s21_decimal.a -o $(TEST_DIR)/$(TEST.OUT) $(TEST_LIBS)
	$(TEST_DIR)/$(TEST.OUT)

gcov_report:
	rm -rf $(GCOV_REPORT_DIR)
	mkdir $(GCOV_REPORT_DIR)
	$(CC) $(C_FLAGS) tests.c s21_decimal.c -o $(GCOV_REPORT_DIR)/$(TEST.OUT) $(GCOV_FLAGS) $(TEST_LIBS)
	$(GCOV_REPORT_DIR)/$(TEST.OUT)
	gcovr -r . --html --html-details --exclude 'tests\.c' -o $(GCOV_REPORT_DIR)/coverage_report.html


clean:
	rm -f *.a *.gcov
	rm -rf $(OBJ_DIR)
	rm -rf $(GCOV_REPORT_DIR)
	rm -rf $(TEST_DIR)

.PHONY: all s21_decimal.a test gcov_report clean