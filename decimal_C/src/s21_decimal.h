#ifndef S21_DECIMAL_H
#define S21_DECIMAL_H

#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Constants
#define DECIMAL_SUCCESS 0
#define DECIMAL_ERROR 1
#define DECIMAL_OVERFLOW 1
#define DECIMAL_UNDERFLOW 2
#define DECIMAL_DIV_BY_ZERO 3

#define DECIMAL_MAX_SCALE 28
#define DECIMAL_BITS_IN_WORD 32
#define DECIMAL_WORDS_COUNT 3
#define DECIMAL_BIG_WORDS_COUNT 7
#define DECIMAL_MAX_BITS 96
#define DECIMAL_BIG_MAX_BITS 224

// Macros for bit operations
#define SET_BIG_BIT(bd, bit, value)         \
  do {                                      \
    int idx = (bit) / DECIMAL_BITS_IN_WORD; \
    int pos = (bit) % DECIMAL_BITS_IN_WORD; \
    uint32_t mask = 1u << (pos);            \
    if (value) {                            \
      (bd).bits[idx] |= mask;               \
    } else {                                \
      (bd).bits[idx] &= ~mask;              \
    }                                       \
  } while (0)

#define GET_BIG_BIT(bd, bit)                   \
  (((bd).bits[(bit) / DECIMAL_BITS_IN_WORD] >> \
    ((bit) % DECIMAL_BITS_IN_WORD)) &          \
   1)

typedef struct {
  uint32_t bits[4];
} s21_decimal;

typedef struct {
  uint32_t bits[7];
} s21_big_decimal;

// ==================== BASIC FUNCTIONS ====================
int s21_get_bit(s21_decimal decimal, int bit);
int s21_get_sign(s21_decimal decimal);
void s21_set_sign(s21_decimal* decimal, int sign);
int s21_get_scale(s21_decimal decimal);
void s21_set_scale(s21_decimal* decimal, int scale);
void s21_clear_decimal(s21_decimal* value);
void s21_clear_big_decimal(s21_big_decimal* value);
int s21_is_zero_decimal(s21_decimal value);
int s21_is_zero_big_decimal(s21_big_decimal value);
int s21_validate_decimal(s21_decimal value);
s21_big_decimal s21_convert_to_big(s21_decimal value);
s21_decimal s21_convert_from_big_low(s21_big_decimal big_value);
void s21_decimal_divide_by_10(s21_decimal* value);

// ==================== HELPER OPERATIONS ====================
void s21_big_decimal_shift_left(s21_big_decimal* value);
int s21_big_decimal_add(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result);
int s21_big_decimal_sub(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result);
int s21_big_decimal_mul(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result);
int s21_big_decimal_compare(s21_big_decimal value_1, s21_big_decimal value_2);
int s21_big_decimal_multiply_by_10(s21_big_decimal* value);
int s21_big_decimal_multiply_by_power_of_10(s21_big_decimal* value, int power);
int s21_normalize_decimals(s21_big_decimal* big_1, s21_big_decimal* big_2,
                           int scale_1, int scale_2);
int s21_check_big_decimal_overflow(s21_big_decimal value);
int s21_handle_overflow_and_scale(s21_big_decimal* big_result, int* scale,
                                  int sign, s21_decimal* result);
int s21_big_decimal_div_with_remainder(s21_big_decimal value_1,
                                       s21_big_decimal value_2,
                                       s21_big_decimal* result,
                                       s21_big_decimal* remainder);
void s21_round_and_reduce_step(s21_big_decimal* big_result, int* scale);

// ==================== CONVERSION FUNCTIONS ====================
int s21_from_int_to_decimal(int src, s21_decimal* dst);
int s21_from_decimal_to_int(s21_decimal src, int* dst);
int s21_from_float_to_decimal(float src, s21_decimal* dst);
int s21_from_decimal_to_float(s21_decimal src, float* dst);
int s21_parse_float_string(float src, char* digits, int* exponent,
                           int* negative);
int s21_build_decimal_from_digits(const char* digits, int exponent,
                                  s21_decimal* dst);

// ==================== COMPARISON FUNCTIONS ====================
int s21_is_equal(s21_decimal value_1, s21_decimal value_2);
int s21_is_not_equal(s21_decimal value_1, s21_decimal value_2);
int s21_is_less(s21_decimal value_1, s21_decimal value_2);
int s21_is_less_or_equal(s21_decimal value_1, s21_decimal value_2);
int s21_is_greater(s21_decimal value_1, s21_decimal value_2);
int s21_is_greater_or_equal(s21_decimal value_1, s21_decimal value_2);
int s21_compare_with_normalization(s21_decimal value_1, s21_decimal value_2);

// ==================== ARITHMETIC FUNCTIONS ====================
int s21_add(s21_decimal value_1, s21_decimal value_2, s21_decimal* result);
int s21_sub(s21_decimal value_1, s21_decimal value_2, s21_decimal* result);
int s21_mul(s21_decimal value_1, s21_decimal value_2, s21_decimal* result);
int s21_div(s21_decimal value_1, s21_decimal value_2, s21_decimal* result);
int s21_add_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result);
int s21_mul_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result);
int s21_div_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result);

// ==================== OTHER FUNCTIONS ====================
int s21_floor(s21_decimal value, s21_decimal* result);
int s21_round(s21_decimal value, s21_decimal* result);
int s21_truncate(s21_decimal value, s21_decimal* result);
int s21_negate(s21_decimal value, s21_decimal* result);

#endif  // S21_DECIMAL_H
