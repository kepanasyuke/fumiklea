#include <check.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "s21_decimal.h"

// ==================== TEST HELPERS ====================

static s21_decimal create_decimal(const uint32_t bits[4]) {
  s21_decimal dec;
  for (int i = 0; i < 4; i++) {
    dec.bits[i] = bits[i];
  }
  return dec;
}

static s21_big_decimal create_big_decimal(const uint32_t bits[7]) {
  s21_big_decimal big_dec;
  for (int i = 0; i < 7; i++) {
    big_dec.bits[i] = bits[i];
  }
  return big_dec;
}

static void assert_decimal_equal(s21_decimal d1, s21_decimal d2,
                                 const char *message) {
  for (int i = 0; i < 4; i++) {
    if (d1.bits[i] != d2.bits[i]) {
      ck_assert_msg(0, "%s: bits[%d] differ: 0x%08X vs 0x%08X", message, i,
                    d1.bits[i], d2.bits[i]);
    }
  }
}

// ==================== BASIC FUNCTIONS TESTS ====================

START_TEST(test_get_bit) {
  s21_decimal dec;
  memset(&dec, 0, sizeof(s21_decimal));

  dec.bits[0] = 0x00000001;
  ck_assert_int_eq(s21_get_bit(dec, 0), 1);
  ck_assert_int_eq(s21_get_bit(dec, 1), 0);

  dec.bits[0] = 0x80000000;
  ck_assert_int_eq(s21_get_bit(dec, 31), 1);

  dec.bits[1] = 0x00000001;
  ck_assert_int_eq(s21_get_bit(dec, 32), 1);

  dec.bits[2] = 0x80000000;
  ck_assert_int_eq(s21_get_bit(dec, 95), 1);
}
END_TEST

START_TEST(test_get_set_sign) {
  s21_decimal dec = {{12345, 0, 0, 0}};

  ck_assert_int_eq(s21_get_sign(dec), 0);

  s21_set_sign(&dec, 1);
  ck_assert_int_eq(s21_get_sign(dec), 1);
  ck_assert_int_eq(dec.bits[3] & 0x80000000, 0x80000000);

  s21_set_sign(&dec, 0);
  ck_assert_int_eq(s21_get_sign(dec), 0);
  ck_assert_int_eq(dec.bits[3] & 0x80000000, 0x0);

  dec.bits[3] = 0x00010000;
  s21_set_sign(&dec, 1);
  ck_assert_int_eq(s21_get_sign(dec), 1);
  ck_assert_int_eq(s21_get_scale(dec), 1);
}
END_TEST

START_TEST(test_get_set_scale) {
  s21_decimal dec = {{12345, 0, 0, 0}};

  ck_assert_int_eq(s21_get_scale(dec), 0);

  s21_set_scale(&dec, 5);
  ck_assert_int_eq(s21_get_scale(dec), 5);
  ck_assert_int_eq((dec.bits[3] >> 16) & 0xFF, 5);

  s21_set_scale(&dec, 28);
  ck_assert_int_eq(s21_get_scale(dec), 28);

  s21_set_sign(&dec, 1);
  s21_set_scale(&dec, 10);
  ck_assert_int_eq(s21_get_scale(dec), 10);
  ck_assert_int_eq(s21_get_sign(dec), 1);
}
END_TEST

START_TEST(test_clear_decimal) {
  s21_decimal dec = {{0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF}};
  s21_clear_decimal(&dec);

  for (int i = 0; i < 4; i++) {
    ck_assert_uint_eq(dec.bits[i], 0);
  }
}
END_TEST

START_TEST(test_clear_big_decimal) {
  s21_big_decimal big_dec;

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    big_dec.bits[i] = 0xFFFFFFFF;
  }

  s21_clear_big_decimal(&big_dec);

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(big_dec.bits[i], 0);
  }
}
END_TEST

START_TEST(test_is_zero_decimal) {
  s21_decimal zero = {{0, 0, 0, 0}};
  s21_decimal non_zero = {{1, 0, 0, 0}};
  s21_decimal negative_zero = {{0, 0, 0, 0x80000000}};
  s21_decimal non_zero_middle = {{0, 1, 0, 0}};
  s21_decimal non_zero_high = {{0, 0, 1, 0}};

  ck_assert_int_eq(s21_is_zero_decimal(zero), 1);
  ck_assert_int_eq(s21_is_zero_decimal(negative_zero), 1);
  ck_assert_int_eq(s21_is_zero_decimal(non_zero), 0);
  ck_assert_int_eq(s21_is_zero_decimal(non_zero_middle), 0);
  ck_assert_int_eq(s21_is_zero_decimal(non_zero_high), 0);
}
END_TEST

START_TEST(test_is_zero_big_decimal) {
  s21_big_decimal zero_big = {0};
  s21_big_decimal non_zero_big = {{1, 0, 0, 0, 0, 0, 0}};
  s21_big_decimal non_zero_middle = {{0, 1, 0, 0, 0, 0, 0}};
  s21_big_decimal non_zero_high = {{0, 0, 0, 0, 0, 0, 1}};

  ck_assert_int_eq(s21_is_zero_big_decimal(zero_big), 1);
  ck_assert_int_eq(s21_is_zero_big_decimal(non_zero_big), 0);
  ck_assert_int_eq(s21_is_zero_big_decimal(non_zero_middle), 0);
  ck_assert_int_eq(s21_is_zero_big_decimal(non_zero_high), 0);
}
END_TEST

START_TEST(test_validate_decimal) {
  uint32_t valid_bits[4] = {12345, 0, 0, 0x00050000};
  s21_decimal valid = create_decimal(valid_bits);
  ck_assert_int_eq(s21_validate_decimal(valid), DECIMAL_SUCCESS);

  uint32_t invalid_scale_bits[4] = {12345, 0, 0, 0x001D0000};
  s21_decimal invalid_scale = create_decimal(invalid_scale_bits);
  ck_assert_int_eq(s21_validate_decimal(invalid_scale), DECIMAL_ERROR);

  uint32_t invalid_bits24_30[4] = {12345, 0, 0, 0x01000000};
  s21_decimal invalid_mid = create_decimal(invalid_bits24_30);
  ck_assert_int_eq(s21_validate_decimal(invalid_mid), DECIMAL_ERROR);

  uint32_t invalid_bits0_15[4] = {12345, 0, 0, 0x00050001};
  s21_decimal invalid_low = create_decimal(invalid_bits0_15);
  ck_assert_int_eq(s21_validate_decimal(invalid_low), DECIMAL_ERROR);

  uint32_t valid_neg_bits[4] = {12345, 0, 0, 0x80050000};
  s21_decimal valid_neg = create_decimal(valid_neg_bits);
  ck_assert_int_eq(s21_validate_decimal(valid_neg), DECIMAL_SUCCESS);

  uint32_t zero_scale_bits[4] = {0, 0, 0, 0x000A0000};
  s21_decimal zero_scale = create_decimal(zero_scale_bits);
  ck_assert_int_eq(s21_validate_decimal(zero_scale), DECIMAL_SUCCESS);
}
END_TEST

START_TEST(test_convert_to_from_big) {
  s21_decimal dec;
  s21_big_decimal big_dec;

  uint32_t dec_bits[4] = {0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x00050000};
  dec = create_decimal(dec_bits);

  big_dec = s21_convert_to_big(dec);

  for (int i = 0; i < 3; i++) {
    ck_assert_uint_eq(big_dec.bits[i], dec.bits[i]);
  }
  for (int i = 3; i < 7; i++) {
    ck_assert_uint_eq(big_dec.bits[i], 0);
  }

  s21_decimal dec2 = s21_convert_from_big_low(big_dec);

  for (int i = 0; i < 3; i++) {
    ck_assert_uint_eq(dec2.bits[i], dec.bits[i]);
  }
}
END_TEST

START_TEST(test_decimal_divide_by_10) {
  s21_decimal dec;

  uint32_t bits[4] = {100, 0, 0, 0};
  dec = create_decimal(bits);

  s21_decimal_divide_by_10(&dec);
  ck_assert_uint_eq(dec.bits[0], 10);

  uint32_t bits2[4] = {12345, 0, 0, 0};
  dec = create_decimal(bits2);

  s21_decimal_divide_by_10(&dec);
  ck_assert_uint_eq(dec.bits[0], 1234);

  uint32_t bits3[4] = {0, 1, 0, 0};
  dec = create_decimal(bits3);

  s21_decimal_divide_by_10(&dec);

  uint32_t bits4[4] = {0, 0, 0, 0};
  dec = create_decimal(bits4);

  s21_decimal_divide_by_10(&dec);
  ck_assert_uint_eq(dec.bits[0], 0);
}
END_TEST

// ==================== HELPER OPERATIONS TESTS ====================

START_TEST(test_big_decimal_shift_left) {
  s21_big_decimal big_dec = {{0x80000000, 0x00000001, 0, 0, 0, 0, 0}};

  s21_big_decimal_shift_left(&big_dec);

  ck_assert_uint_eq(big_dec.bits[0], 0x00000000);
  ck_assert_uint_eq(big_dec.bits[1], 0x00000003);
  ck_assert_uint_eq(big_dec.bits[2], 0x00000000);

  s21_big_decimal big_dec2 = {{1, 0, 0, 0, 0, 0, 0}};
  s21_big_decimal_shift_left(&big_dec2);
  ck_assert_uint_eq(big_dec2.bits[0], 2);

  s21_big_decimal big_dec3 = {{0, 0, 0, 0, 0, 0, 0}};
  s21_big_decimal_shift_left(&big_dec3);
  ck_assert_uint_eq(big_dec3.bits[0], 0);
}
END_TEST

START_TEST(test_big_decimal_add) {
  s21_big_decimal a, b, result;

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);

  a.bits[0] = 5;
  b.bits[0] = 3;

  int error = s21_big_decimal_add(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 8);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 0xFFFFFFFF;
  b.bits[0] = 1;

  error = s21_big_decimal_add(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 0);
  ck_assert_uint_eq(result.bits[1], 1);

  for (int i = 2; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    a.bits[i] = 0xFFFFFFFF;
    b.bits[i] = 1;
  }

  error = s21_big_decimal_add(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_OVERFLOW);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  error = s21_big_decimal_add(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(result), 1);
}
END_TEST

START_TEST(test_big_decimal_sub) {
  s21_big_decimal a, b, result;

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);

  a.bits[0] = 10;
  b.bits[0] = 3;

  int error = s21_big_decimal_sub(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 7);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 0;
  a.bits[1] = 1;
  b.bits[0] = 1;

  error = s21_big_decimal_sub(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 0xFFFFFFFF);
  ck_assert_uint_eq(result.bits[1], 0);

  for (int i = 2; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 3;
  b.bits[0] = 10;

  error = s21_big_decimal_sub(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 5;
  b.bits[0] = 5;

  error = s21_big_decimal_sub(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 0);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }
}
END_TEST

START_TEST(test_big_decimal_mul) {
  s21_big_decimal a, b, result;

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 5;
  b.bits[0] = 3;

  int error = s21_big_decimal_mul(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 15);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 5;

  error = s21_big_decimal_mul(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(result), 1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  b.bits[0] = 5;

  error = s21_big_decimal_mul(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(result), 1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 1;
  b.bits[0] = 1 << 15;

  error = s21_big_decimal_mul(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 1 << 15);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 1000;
  b.bits[0] = 1000;

  error = s21_big_decimal_mul(a, b, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 1000000);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(result.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 0xFFFFFFFF;
  b.bits[0] = 2;

  error = s21_big_decimal_mul(a, b, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 0xFFFFFFFE);
  ck_assert_uint_eq(result.bits[1], 1);
}
END_TEST

START_TEST(test_big_decimal_compare) {
  s21_big_decimal a, b;

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 5;
  b.bits[0] = 5;

  ck_assert_int_eq(s21_big_decimal_compare(a, b), 0);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 5;
  b.bits[0] = 10;

  ck_assert_int_eq(s21_big_decimal_compare(a, b), -1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 10;
  b.bits[0] = 5;

  ck_assert_int_eq(s21_big_decimal_compare(a, b), 1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[1] = 1;
  b.bits[0] = 0xFFFFFFFF;

  ck_assert_int_eq(s21_big_decimal_compare(a, b), 1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  ck_assert_int_eq(s21_big_decimal_compare(a, b), 0);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[6] = 1;
  ck_assert_int_eq(s21_big_decimal_compare(a, b), 1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  b.bits[6] = 1;
  ck_assert_int_eq(s21_big_decimal_compare(a, b), -1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 0x12345678;
  a.bits[1] = 0x9ABCDEF0;
  a.bits[2] = 0x0FEDCBA9;
  b.bits[0] = 0x12345678;
  b.bits[1] = 0x9ABCDEF0;
  b.bits[2] = 0x0FEDCBA9;
  ck_assert_int_eq(s21_big_decimal_compare(a, b), 0);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[2] = 0x0FEDCBA8;
  b.bits[2] = 0x0FEDCBA9;
  ck_assert_int_eq(s21_big_decimal_compare(a, b), -1);

  s21_clear_big_decimal(&a);
  s21_clear_big_decimal(&b);
  a.bits[0] = 0x12345679;
  b.bits[0] = 0x12345678;

  a.bits[1] = b.bits[1] = 0x9ABCDEF0;
  a.bits[2] = b.bits[2] = 0x0FEDCBA9;
  ck_assert_int_eq(s21_big_decimal_compare(a, b), 1);
}
END_TEST

START_TEST(test_big_decimal_multiply_by_10) {
  s21_big_decimal a;

  s21_clear_big_decimal(&a);
  a.bits[0] = 5;

  int error = s21_big_decimal_multiply_by_10(&a);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(a.bits[0], 50);

  for (int i = 1; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    ck_assert_uint_eq(a.bits[i], 0);
  }

  s21_clear_big_decimal(&a);
  a.bits[0] = 0x19999999;

  error = s21_big_decimal_multiply_by_10(&a);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(a.bits[0], 4294967290u);

  s21_clear_big_decimal(&a);
  a.bits[0] = 0x99999999;
  a.bits[1] = 0x19999999;

  error = s21_big_decimal_multiply_by_10(&a);
  ck_assert(error == DECIMAL_SUCCESS || error == DECIMAL_OVERFLOW);

  s21_clear_big_decimal(&a);
  error = s21_big_decimal_multiply_by_10(&a);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(a), 1);

  s21_clear_big_decimal(&a);
  a.bits[0] = 0xCCCCCCCC;
  a.bits[1] = 0x33333333;

  error = s21_big_decimal_multiply_by_10(&a);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  s21_clear_big_decimal(&a);

  a.bits[0] = 1;

  error = s21_big_decimal_multiply_by_10(&a);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(a.bits[0], 10);
}
END_TEST

START_TEST(test_big_decimal_multiply_by_power_of_10) {
  s21_big_decimal value;
  int power = 3;

  uint32_t bits[7] = {123, 0, 0, 0, 0, 0, 0};
  value = create_big_decimal(bits);

  int error = s21_big_decimal_multiply_by_power_of_10(&value, power);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(value.bits[0], 123000);

  uint32_t bits2[7] = {456, 0, 0, 0, 0, 0, 0};
  value = create_big_decimal(bits2);
  power = 0;

  error = s21_big_decimal_multiply_by_power_of_10(&value, power);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(value.bits[0], 456);

  uint32_t bits3[7] = {1, 0, 0, 0, 0, 0, 0};
  value = create_big_decimal(bits3);
  power = 10;

  error = s21_big_decimal_multiply_by_power_of_10(&value, power);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
}
END_TEST

START_TEST(test_normalize_decimals) {
  s21_big_decimal big1, big2;

  int scale1 = 3;
  int scale2 = 2;

  uint32_t bits1[7] = {123, 0, 0, 0, 0, 0, 0};
  uint32_t bits2[7] = {456, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits1);
  big2 = create_big_decimal(bits2);

  int error = s21_normalize_decimals(&big1, &big2, scale1, scale2);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  ck_assert_uint_eq(big2.bits[0], 4560);
  ck_assert_uint_eq(big1.bits[0], 123);

  scale1 = 1;
  scale2 = 4;

  uint32_t bits3[7] = {12, 0, 0, 0, 0, 0, 0};
  uint32_t bits4[7] = {5678, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits3);
  big2 = create_big_decimal(bits4);

  error = s21_normalize_decimals(&big1, &big2, scale1, scale2);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  ck_assert_uint_eq(big1.bits[0], 12000);
  ck_assert_uint_eq(big2.bits[0], 5678);

  scale1 = 5;
  scale2 = 5;

  uint32_t bits5[7] = {12345, 0, 0, 0, 0, 0, 0};
  uint32_t bits6[7] = {67890, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits5);
  big2 = create_big_decimal(bits6);

  error = s21_normalize_decimals(&big1, &big2, scale1, scale2);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(big1.bits[0], 12345);
  ck_assert_uint_eq(big2.bits[0], 67890);

  scale1 = 0;
  scale2 = 5;

  uint32_t bits7[7] = {7, 0, 0, 0, 0, 0, 0};
  uint32_t bits8[7] = {12345, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits7);
  big2 = create_big_decimal(bits8);

  error = s21_normalize_decimals(&big1, &big2, scale1, scale2);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  ck_assert_uint_eq(big1.bits[0], 700000);
  ck_assert_uint_eq(big2.bits[0], 12345);
}
END_TEST

START_TEST(test_check_big_decimal_overflow) {
  s21_big_decimal value;

  s21_clear_big_decimal(&value);
  value.bits[0] = 0xFFFFFFFF;
  value.bits[1] = 0xFFFFFFFF;
  value.bits[2] = 0xFFFFFFFF;

  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 0);

  value.bits[3] = 1;
  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 1);

  s21_clear_big_decimal(&value);
  value.bits[4] = 1;
  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 1);

  value.bits[5] = 1;
  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 1);

  value.bits[6] = 1;
  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 1);

  s21_clear_big_decimal(&value);
  ck_assert_int_eq(s21_check_big_decimal_overflow(value), 0);
}
END_TEST

START_TEST(test_round_and_reduce_step) {
  s21_big_decimal big_result;
  int scale = 3;

  uint32_t bits[7] = {12345, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits);

  s21_round_and_reduce_step(&big_result, &scale);

  ck_assert_int_eq(scale, 2);

  ck_assert_uint_eq(big_result.bits[0], 1234);

  scale = 3;
  uint32_t bits2[7] = {12344, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits2);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1234);

  scale = 3;
  uint32_t bits3[7] = {12346, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits3);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1235);

  scale = 3;
  uint32_t bits4[7] = {12345, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits4);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1234);

  scale = 3;
  uint32_t bits5[7] = {12355, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits5);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1236);

  scale = 3;
  uint32_t bits6[7] = {12335, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits6);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1234);

  scale = 3;
  uint32_t bits7[7] = {12325, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits7);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);
  ck_assert_uint_eq(big_result.bits[0], 1232);

  scale = 1;
  uint32_t bits8[7] = {12340, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits8);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 0);
  ck_assert_uint_eq(big_result.bits[0], 1234);

  scale = 3;
  uint32_t bits9[7] = {99995, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits9);

  s21_round_and_reduce_step(&big_result, &scale);
  ck_assert_int_eq(scale, 2);

  ck_assert_uint_eq(big_result.bits[0], 10000);
}
END_TEST

START_TEST(test_handle_overflow_and_scale) {
  s21_big_decimal big_result;
  int scale = 2;
  int sign = 0;
  s21_decimal result;

  uint32_t bits[7] = {12345, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits);

  int error = s21_handle_overflow_and_scale(&big_result, &scale, sign, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 12345);
  ck_assert_int_eq(s21_get_scale(result), scale);
  ck_assert_int_eq(s21_get_sign(result), sign);

  scale = 5;
  sign = 0;
  uint32_t bits2[7] = {123456789, 123456789, 123456789, 1, 0, 0, 0};
  big_result = create_big_decimal(bits2);

  error = s21_handle_overflow_and_scale(&big_result, &scale, sign, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(scale < 5, 1);

  scale = 2;
  sign = 1;
  uint32_t bits3[7] = {12345, 0, 0, 0, 0, 0, 0};
  big_result = create_big_decimal(bits3);

  error = s21_handle_overflow_and_scale(&big_result, &scale, sign, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);

  scale = 0;
  sign = 0;
  uint32_t bits4[7] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 1, 0, 0, 0};
  big_result = create_big_decimal(bits4);

  error = s21_handle_overflow_and_scale(&big_result, &scale, sign, &result);
  ck_assert_int_eq(error, DECIMAL_OVERFLOW);

  scale = 0;
  sign = 1;
  error = s21_handle_overflow_and_scale(&big_result, &scale, sign, &result);
  ck_assert_int_eq(error, DECIMAL_UNDERFLOW);
}
END_TEST

START_TEST(test_big_decimal_div_with_remainder) {
  s21_big_decimal dividend, divisor, result, remainder;

  uint32_t div_bits[7] = {15, 0, 0, 0, 0, 0, 0};
  uint32_t dvs_bits[7] = {3, 0, 0, 0, 0, 0, 0};

  dividend = create_big_decimal(div_bits);
  divisor = create_big_decimal(dvs_bits);

  int error = s21_big_decimal_div_with_remainder(dividend, divisor, &result,
                                                 &remainder);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 5);
  ck_assert_int_eq(s21_is_zero_big_decimal(remainder), 1);

  uint32_t div_bits2[7] = {10, 0, 0, 0, 0, 0, 0};
  dividend = create_big_decimal(div_bits2);

  error = s21_big_decimal_div_with_remainder(dividend, divisor, &result,
                                             &remainder);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 3);
  ck_assert_uint_eq(remainder.bits[0], 1);

  uint32_t zero_bits[7] = {0, 0, 0, 0, 0, 0, 0};
  divisor = create_big_decimal(zero_bits);

  error = s21_big_decimal_div_with_remainder(dividend, divisor, &result,
                                             &remainder);
  ck_assert_int_eq(error, DECIMAL_DIV_BY_ZERO);

  dividend = create_big_decimal(zero_bits);
  divisor.bits[0] = 5;

  error = s21_big_decimal_div_with_remainder(dividend, divisor, &result,
                                             &remainder);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(result), 1);
  ck_assert_int_eq(s21_is_zero_big_decimal(remainder), 1);

  dividend.bits[0] = 3;
  divisor.bits[0] = 10;

  error = s21_big_decimal_div_with_remainder(dividend, divisor, &result,
                                             &remainder);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_big_decimal(result), 1);
  ck_assert_uint_eq(remainder.bits[0], 3);
}
END_TEST

// ==================== CONVERSION FUNCTIONS TESTS ====================

START_TEST(test_from_int_to_decimal) {
  s21_decimal result;

  ck_assert_int_eq(s21_from_int_to_decimal(0, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);
  ck_assert_int_eq(s21_get_sign(result), 0);

  ck_assert_int_eq(s21_from_int_to_decimal(12345, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result.bits[0], 12345);
  ck_assert_int_eq(result.bits[1], 0);
  ck_assert_int_eq(result.bits[2], 0);
  ck_assert_int_eq(s21_get_sign(result), 0);

  ck_assert_int_eq(s21_from_int_to_decimal(-12345, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result.bits[0], 12345);
  ck_assert_int_eq(s21_get_sign(result), 1);

  ck_assert_int_eq(s21_from_int_to_decimal(INT_MAX, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result.bits[0], INT_MAX);
  ck_assert_int_eq(s21_get_sign(result), 0);

  ck_assert_int_eq(s21_from_int_to_decimal(INT_MIN, &result), DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], (uint32_t)INT_MAX + 1);
  ck_assert_int_eq(s21_get_sign(result), 1);

  ck_assert_int_eq(s21_from_int_to_decimal(123, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_from_decimal_to_int) {
  s21_decimal dec;
  int result;

  uint32_t zero_bits[4] = {0, 0, 0, 0};
  dec = create_decimal(zero_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 0);

  uint32_t pos_bits[4] = {12345, 0, 0, 0};
  dec = create_decimal(pos_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 12345);

  uint32_t neg_bits[4] = {12345, 0, 0, 0x80000000};
  dec = create_decimal(neg_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result, -12345);

  uint32_t scaled_bits[4] = {12345, 0, 0, 0x00020000};
  dec = create_decimal(scaled_bits);

  int error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 123);

  uint32_t neg_scaled_bits[4] = {12345, 0, 0, 0x80020000};
  dec = create_decimal(neg_scaled_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(result, -123);

  uint32_t large_bits[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0, 0};
  dec = create_decimal(large_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_decimal_to_int(dec, NULL), DECIMAL_ERROR);

  uint32_t invalid_bits[4] = {12345, 0, 0, 0x001D0000};
  dec = create_decimal(invalid_bits);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, &result), DECIMAL_ERROR);

  uint32_t intmax_bits[4] = {INT_MAX, 0, 0, 0};
  dec = create_decimal(intmax_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, INT_MAX);

  uint32_t intmin_abs = 2147483648u;
  uint32_t intmin_bits[4] = {intmin_abs, 0, 0, 0x80000000};
  dec = create_decimal(intmin_bits);
  error = s21_from_decimal_to_int(dec, &result);

  if (error == DECIMAL_SUCCESS) {
    ck_assert_int_eq(result, INT_MIN);
  }

  uint32_t trunc_bits[4] = {199, 0, 0, 0x00020000};
  dec = create_decimal(trunc_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 1);

  uint32_t neg_trunc_bits[4] = {199, 0, 0, 0x80020000};
  dec = create_decimal(neg_trunc_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, -1);

  uint32_t half_bits[4] = {5, 0, 0, 0x00010000};
  dec = create_decimal(half_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 0);

  uint32_t neg_zero_bits[4] = {0, 0, 0, 0x80000000};
  dec = create_decimal(neg_zero_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, 0);

  uint32_t just_below_max_bits[4] = {INT_MAX - 1, 0, 0, 0};
  dec = create_decimal(just_below_max_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, INT_MAX - 1);

  uint32_t just_above_min_abs = 2147483647u;
  uint32_t just_above_min_bits[4] = {just_above_min_abs, 0, 0, 0x80000000};
  dec = create_decimal(just_above_min_bits);
  error = s21_from_decimal_to_int(dec, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(result, -2147483647);
}
END_TEST

START_TEST(test_parse_float_string) {
  float src = 123.456f;
  char digits[50];
  int exponent = 0;
  int negative = 0;

  int error = s21_parse_float_string(src, digits, &exponent, &negative);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1234560");
  ck_assert_int_eq(negative, 0);
  ck_assert_int_eq(exponent, -4);

  src = -123.456f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(negative, 1);
  ck_assert_str_eq(digits, "1234560");
  ck_assert_int_eq(exponent, -4);

  src = 0.000123f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(negative, 0);
  ck_assert_str_eq(digits, "1230000");
  ck_assert_int_eq(exponent, -10);

  src = 123456789.0f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1234568");
  ck_assert_int_eq(exponent, 2);

  src = 0.0f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "0");
  ck_assert_int_eq(exponent, 0);
  ck_assert_int_eq(negative, 0);

  src = 1e-10f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1000000");
  ck_assert_int_eq(exponent, -16);

  src = 1e10f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1000000");
  ck_assert_int_eq(exponent, 4);

  src = 100.0f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1000000");
  ck_assert_int_eq(exponent, -4);

  src = 0.000001f;
  error = s21_parse_float_string(src, digits, &exponent, &negative);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_str_eq(digits, "1000000");
  ck_assert_int_eq(exponent, -12);
}
END_TEST

START_TEST(test_build_decimal_from_digits) {
  s21_decimal result;
  const char *digits = "123";
  int exponent = 0;

  int error = s21_build_decimal_from_digits(digits, exponent, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_uint_eq(result.bits[0], 123);

  exponent = 2;
  error = s21_build_decimal_from_digits(digits, exponent, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  exponent = -2;
  error = s21_build_decimal_from_digits(digits, exponent, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result), 2);
  ck_assert_uint_eq(result.bits[0], 123);

  digits = "123456789";
  exponent = -5;
  error = s21_build_decimal_from_digits(digits, exponent, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result) > 0, 1);

  digits = "0";
  exponent = 0;
  error = s21_build_decimal_from_digits(digits, exponent, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);

  digits = "7";
  exponent = -1;
  error = s21_build_decimal_from_digits(digits, exponent, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
}
END_TEST

START_TEST(test_from_float_to_decimal) {
  s21_decimal result;

  ck_assert_int_eq(s21_from_float_to_decimal(0.0f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);
  ck_assert_int_eq(s21_get_sign(result), 0);

  ck_assert_int_eq(s21_from_float_to_decimal(42.0f, &result), DECIMAL_SUCCESS);

  ck_assert_int_eq(s21_from_float_to_decimal(123.456f, &result),
                   DECIMAL_SUCCESS);

  ck_assert_int_eq(s21_from_float_to_decimal(-123.456f, &result),
                   DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);

  ck_assert_int_eq(s21_from_float_to_decimal(1e-29f, &result), DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_float_to_decimal(NAN, &result), DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_float_to_decimal(INFINITY, &result), DECIMAL_ERROR);
  ck_assert_int_eq(s21_from_float_to_decimal(-INFINITY, &result),
                   DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_float_to_decimal(123.456f, NULL), DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_float_to_decimal(1.0f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(0.1f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(0.01f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(0.001f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(1000.0f, &result),
                   DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(123456.789f, &result),
                   DECIMAL_SUCCESS);

  ck_assert_int_eq(s21_from_float_to_decimal(1e-38f, &result), DECIMAL_ERROR);

  ck_assert_int_eq(s21_from_float_to_decimal(10.0f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(100.0f, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_from_float_to_decimal(1000.0f, &result),
                   DECIMAL_SUCCESS);
}
END_TEST

START_TEST(test_from_decimal_to_float) {
  s21_decimal dec;
  float result;

  uint32_t zero_bits[4] = {0, 0, 0, 0};
  dec = create_decimal(zero_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, 0.0f, 1e-6);

  uint32_t pos_bits[4] = {42, 0, 0, 0};
  dec = create_decimal(pos_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, 42.0f, 1e-6);

  uint32_t scaled_bits[4] = {12345, 0, 0, 0x00020000};
  dec = create_decimal(scaled_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, 123.45f, 1e-3);

  uint32_t neg_bits[4] = {12345, 0, 0, 0x80020000};
  dec = create_decimal(neg_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, -123.45f, 1e-3);

  uint32_t small_bits[4] = {1, 0, 0, 0x00060000};
  dec = create_decimal(small_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, 0.000001f, 1e-7);

  ck_assert_int_eq(s21_from_decimal_to_float(dec, NULL), DECIMAL_ERROR);

  uint32_t invalid_bits[4] = {12345, 0, 0, 0x001D0000};
  dec = create_decimal(invalid_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_ERROR);

  uint32_t neg_zero_bits[4] = {0, 0, 0, 0x80000000};
  dec = create_decimal(neg_zero_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
  ck_assert_float_eq_tol(result, -0.0f, 1e-6);

  uint32_t large_bits[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0};
  dec = create_decimal(large_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);

  uint32_t max_scale_bits[4] = {123456789, 0, 0, 0x001C0000};
  dec = create_decimal(max_scale_bits);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, &result), DECIMAL_SUCCESS);
}
END_TEST

// ==================== COMPARISON FUNCTIONS TESTS ====================

START_TEST(test_compare_with_normalization) {
  s21_decimal value1, value2;

  uint32_t bits1[4] = {12345, 0, 0, 0x00020000};
  uint32_t bits2[4] = {12345, 0, 0, 0x00020000};
  value1 = create_decimal(bits1);
  value2 = create_decimal(bits2);

  int result = s21_compare_with_normalization(value1, value2);
  ck_assert_int_eq(result, 0);

  uint32_t bits3[4] = {123450, 0, 0, 0x00030000};
  value2 = create_decimal(bits3);
  result = s21_compare_with_normalization(value1, value2);
  ck_assert_int_eq(result, 0);

  uint32_t bits4[4] = {123, 0, 0, 0x00020000};
  uint32_t bits5[4] = {456, 0, 0, 0x00020000};
  value1 = create_decimal(bits4);
  value2 = create_decimal(bits5);
  result = s21_compare_with_normalization(value1, value2);
  ck_assert_int_eq(result, -1);

  result = s21_compare_with_normalization(value2, value1);
  ck_assert_int_eq(result, 1);

  uint32_t bits6[4] = {1230, 0, 0, 0x00030000};
  uint32_t bits7[4] = {456, 0, 0, 0x00020000};
  value1 = create_decimal(bits6);
  value2 = create_decimal(bits7);
  result = s21_compare_with_normalization(value1, value2);

  ck_assert_int_eq(result, -1);
}
END_TEST

START_TEST(test_is_equal) {
  s21_decimal d1 = {{12345, 0, 0, 0}};
  s21_decimal d2 = {{12345, 0, 0, 0}};
  s21_decimal d3 = {{12346, 0, 0, 0}};
  s21_decimal d4 = {{12345, 0, 0, 0x80000000}};

  ck_assert_int_eq(s21_is_equal(d1, d2), 1);
  ck_assert_int_eq(s21_is_equal(d1, d3), 0);
  ck_assert_int_eq(s21_is_equal(d1, d4), 0);

  uint32_t bits1[4] = {12345, 0, 0, 0x00020000};
  uint32_t bits2[4] = {123450, 0, 0, 0x00030000};
  uint32_t bits3[4] = {1234500, 0, 0, 0x00040000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  d3 = create_decimal(bits3);
  ck_assert_int_eq(s21_is_equal(d1, d2), 1);
  ck_assert_int_eq(s21_is_equal(d1, d3), 1);
  ck_assert_int_eq(s21_is_equal(d2, d3), 1);

  s21_decimal zero1 = {{0, 0, 0, 0}};
  s21_decimal zero2 = {{0, 0, 0, 0x80000000}};
  ck_assert_int_eq(s21_is_equal(zero1, zero2), 1);

  uint32_t invalid_bits[4] = {12345, 0, 0, 0x001D0000};
  d1 = create_decimal(invalid_bits);
  d2 = create_decimal(invalid_bits);
  ck_assert_int_eq(s21_is_equal(d1, d2), 0);
}
END_TEST

START_TEST(test_is_not_equal) {
  s21_decimal d1 = {{100, 0, 0, 0}};
  s21_decimal d2 = {{100, 0, 0, 0}};
  s21_decimal d3 = {{200, 0, 0, 0}};
  s21_decimal d4 = {{100, 0, 0, 0x80000000}};

  ck_assert_int_eq(s21_is_not_equal(d1, d2), 0);
  ck_assert_int_eq(s21_is_not_equal(d1, d3), 1);
  ck_assert_int_eq(s21_is_not_equal(d1, d4), 1);

  uint32_t bits1[4] = {100, 0, 0, 0x00010000};
  uint32_t bits2[4] = {1000, 0, 0, 0x00020000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  ck_assert_int_eq(s21_is_not_equal(d1, d2), 0);
}
END_TEST

START_TEST(test_is_less) {
  s21_decimal d1 = {{100, 0, 0, 0}};
  s21_decimal d2 = {{200, 0, 0, 0}};
  s21_decimal d3 = {{100, 0, 0, 0x80000000}};
  s21_decimal d4 = {{200, 0, 0, 0x80000000}};

  ck_assert_int_eq(s21_is_less(d1, d2), 1);
  ck_assert_int_eq(s21_is_less(d2, d1), 0);
  ck_assert_int_eq(s21_is_less(d3, d4), 0);
  ck_assert_int_eq(s21_is_less(d4, d3), 1);
  ck_assert_int_eq(s21_is_less(d3, d1), 1);
  ck_assert_int_eq(s21_is_less(d1, d3), 0);

  uint32_t bits1[4] = {123, 0, 0, 0x00020000};
  uint32_t bits2[4] = {234, 0, 0, 0x00020000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  ck_assert_int_eq(s21_is_less(d1, d2), 1);
  ck_assert_int_eq(s21_is_less(d2, d1), 0);

  uint32_t bits3[4] = {1230, 0, 0, 0x00030000};
  uint32_t bits4[4] = {1231, 0, 0, 0x00030000};
  d1 = create_decimal(bits3);
  d2 = create_decimal(bits4);
  ck_assert_int_eq(s21_is_less(d1, d2), 1);
}
END_TEST

START_TEST(test_is_less_or_equal) {
  s21_decimal d1 = {{100, 0, 0, 0}};
  s21_decimal d2 = {{100, 0, 0, 0}};
  s21_decimal d3 = {{200, 0, 0, 0}};
  s21_decimal d4 = {{50, 0, 0, 0}};

  ck_assert_int_eq(s21_is_less_or_equal(d1, d2), 1);
  ck_assert_int_eq(s21_is_less_or_equal(d1, d3), 1);
  ck_assert_int_eq(s21_is_less_or_equal(d3, d1), 0);
  ck_assert_int_eq(s21_is_less_or_equal(d4, d1), 1);

  uint32_t bits1[4] = {100, 0, 0, 0x80000000};
  uint32_t bits2[4] = {200, 0, 0, 0x80000000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  ck_assert_int_eq(s21_is_less_or_equal(d1, d2), 0);
  ck_assert_int_eq(s21_is_less_or_equal(d2, d1), 1);

  uint32_t bits3[4] = {123, 0, 0, 0x00020000};
  uint32_t bits4[4] = {1230, 0, 0, 0x00030000};
  d1 = create_decimal(bits3);
  d2 = create_decimal(bits4);
  ck_assert_int_eq(s21_is_less_or_equal(d1, d2), 1);
}
END_TEST

START_TEST(test_is_greater) {
  s21_decimal d1 = {{200, 0, 0, 0}};
  s21_decimal d2 = {{100, 0, 0, 0}};
  s21_decimal d3 = {{100, 0, 0, 0x80000000}};
  s21_decimal d4 = {{200, 0, 0, 0x80000000}};

  ck_assert_int_eq(s21_is_greater(d1, d2), 1);
  ck_assert_int_eq(s21_is_greater(d2, d1), 0);
  ck_assert_int_eq(s21_is_greater(d3, d4), 1);
  ck_assert_int_eq(s21_is_greater(d1, d3), 1);

  uint32_t bits1[4] = {234, 0, 0, 0x00020000};
  uint32_t bits2[4] = {123, 0, 0, 0x00020000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  ck_assert_int_eq(s21_is_greater(d1, d2), 1);
  ck_assert_int_eq(s21_is_greater(d2, d1), 0);

  uint32_t bits3[4] = {123, 0, 0, 0x00020000};
  uint32_t bits4[4] = {1230, 0, 0, 0x00030000};
  d1 = create_decimal(bits3);
  d2 = create_decimal(bits4);
  ck_assert_int_eq(s21_is_greater(d1, d2), 0);
}
END_TEST

START_TEST(test_is_greater_or_equal) {
  s21_decimal d1 = {{100, 0, 0, 0}};
  s21_decimal d2 = {{100, 0, 0, 0}};
  s21_decimal d3 = {{200, 0, 0, 0}};
  s21_decimal d4 = {{50, 0, 0, 0}};

  ck_assert_int_eq(s21_is_greater_or_equal(d1, d2), 1);
  ck_assert_int_eq(s21_is_greater_or_equal(d3, d1), 1);
  ck_assert_int_eq(s21_is_greater_or_equal(d4, d1), 0);

  uint32_t bits1[4] = {100, 0, 0, 0x80000000};
  uint32_t bits2[4] = {200, 0, 0, 0x80000000};
  d1 = create_decimal(bits1);
  d2 = create_decimal(bits2);
  ck_assert_int_eq(s21_is_greater_or_equal(d1, d2), 1);
  ck_assert_int_eq(s21_is_greater_or_equal(d2, d1), 0);

  uint32_t bits3[4] = {123, 0, 0, 0x00020000};
  uint32_t bits4[4] = {1230, 0, 0, 0x00030000};
  d1 = create_decimal(bits3);
  d2 = create_decimal(bits4);
  ck_assert_int_eq(s21_is_greater_or_equal(d1, d2), 1);
}
END_TEST

// ==================== ARITHMETIC FUNCTIONS TESTS ====================

START_TEST(test_add_core) {
  s21_big_decimal big1, big2;
  int sign1 = 0, sign2 = 0;
  int scale1 = 2, scale2 = 2;
  s21_decimal result;

  uint32_t bits1[7] = {123, 0, 0, 0, 0, 0, 0};
  uint32_t bits2[7] = {456, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits1);
  big2 = create_big_decimal(bits2);

  int error = s21_add_core(big1, big2, sign1, sign2, scale1, scale2, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result), 2);
  ck_assert_int_eq(s21_get_sign(result), 0);

  sign1 = 0;
  sign2 = 1;
  scale1 = 1;
  scale2 = 1;
  uint32_t bits3[7] = {50, 0, 0, 0, 0, 0, 0};
  uint32_t bits4[7] = {30, 0, 0, 0, 0, 0, 0};
  big1 = create_big_decimal(bits3);
  big2 = create_big_decimal(bits4);

  error = s21_add_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 0);

  sign1 = 0;
  sign2 = 0;
  scale1 = 2;
  scale2 = 3;
  uint32_t bits5[7] = {123, 0, 0, 0, 0, 0, 0};
  uint32_t bits6[7] = {456, 0, 0, 0, 0, 0, 0};
  big1 = create_big_decimal(bits5);
  big2 = create_big_decimal(bits6);

  error = s21_add_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  sign1 = 1;
  sign2 = 1;
  scale1 = 0;
  scale2 = 0;
  uint32_t bits7[7] = {5, 0, 0, 0, 0, 0, 0};
  uint32_t bits8[7] = {3, 0, 0, 0, 0, 0, 0};
  big1 = create_big_decimal(bits7);
  big2 = create_big_decimal(bits8);

  error = s21_add_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);
}
END_TEST

START_TEST(test_add) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {5, 0, 0, 0};
  uint32_t b_bits[4] = {3, 0, 0, 0};
  uint32_t expected_bits[4] = {8, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits), "5 + 3 = 8");

  uint32_t a_bits2[4] = {123, 0, 0, 0x00020000};
  uint32_t b_bits2[4] = {77, 0, 0, 0x00020000};
  uint32_t expected_bits2[4] = {200, 0, 0, 0x00020000};
  a = create_decimal(a_bits2);
  b = create_decimal(b_bits2);
  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_SUCCESS);

  s21_decimal expected = create_decimal(expected_bits2);
  ck_assert_int_eq(s21_is_equal(result, expected), 1);

  uint32_t a_bits3[4] = {5, 0, 0, 0};
  uint32_t b_bits3[4] = {3, 0, 0, 0x80000000};
  uint32_t expected_bits3[4] = {2, 0, 0, 0};
  a = create_decimal(a_bits3);
  b = create_decimal(b_bits3);
  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits3), "5 + (-3) = 2");

  uint32_t a_bits4[4] = {5, 0, 0, 0};
  uint32_t b_bits4[4] = {0, 0, 0, 0};
  a = create_decimal(a_bits4);
  b = create_decimal(b_bits4);
  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, a, "5 + 0 = 5");

  ck_assert_int_eq(s21_add(a, b, NULL), DECIMAL_ERROR);

  uint32_t invalid_bits[4] = {12345, 0, 0, 0x001D0000};
  a = create_decimal(invalid_bits);
  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_sub) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {5, 0, 0, 0};
  uint32_t b_bits[4] = {3, 0, 0, 0};
  uint32_t expected_bits[4] = {2, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_sub(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits), "5 - 3 = 2");

  a_bits[0] = 3;
  b_bits[0] = 5;
  expected_bits[0] = 2;
  expected_bits[3] = 0x80000000;
  a = create_decimal(a_bits);
  b = create_decimal(b_bits);
  ck_assert_int_eq(s21_sub(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits), "3 - 5 = -2");

  a_bits[0] = 5;
  b_bits[0] = 3;
  b_bits[3] = 0x80000000;
  expected_bits[0] = 8;
  expected_bits[3] = 0;
  a = create_decimal(a_bits);
  b = create_decimal(b_bits);
  ck_assert_int_eq(s21_sub(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits), "5 - (-3) = 8");

  ck_assert_int_eq(s21_sub(a, b, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_mul_core) {
  s21_big_decimal big1, big2;
  int sign1 = 0, sign2 = 0;
  int scale1 = 1, scale2 = 1;
  s21_decimal result;

  uint32_t bits1[7] = {15, 0, 0, 0, 0, 0, 0};
  uint32_t bits2[7] = {20, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits1);
  big2 = create_big_decimal(bits2);

  int error = s21_mul_core(big1, big2, sign1, sign2, scale1, scale2, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 0);
  ck_assert_int_eq(s21_get_scale(result), 2);

  sign1 = 1;
  sign2 = 0;
  scale1 = 0;
  scale2 = 0;
  uint32_t bits3[7] = {5, 0, 0, 0, 0, 0, 0};
  uint32_t bits4[7] = {3, 0, 0, 0, 0, 0, 0};
  big1 = create_big_decimal(bits3);
  big2 = create_big_decimal(bits4);

  error = s21_mul_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);

  sign1 = 1;
  sign2 = 1;
  error = s21_mul_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 0);
}
END_TEST

START_TEST(test_mul) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {5, 0, 0, 0};
  uint32_t b_bits[4] = {3, 0, 0, 0};
  uint32_t expected_bits[4] = {15, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_mul(a, b, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits), "5 * 3 = 15");

  uint32_t a_bits2[4] = {15, 0, 0, 0x00010000};
  uint32_t b_bits2[4] = {20, 0, 0, 0x00010000};
  a = create_decimal(a_bits2);
  b = create_decimal(b_bits2);
  ck_assert_int_eq(s21_mul(a, b, &result), DECIMAL_SUCCESS);

  uint32_t a_bits3[4] = {5, 0, 0, 0};
  uint32_t b_bits3[4] = {0, 0, 0, 0};
  a = create_decimal(a_bits3);
  b = create_decimal(b_bits3);
  ck_assert_int_eq(s21_mul(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);

  a_bits[0] = 5;
  b_bits[0] = 3;
  b_bits[3] = 0x80000000;
  a = create_decimal(a_bits);
  b = create_decimal(b_bits);
  ck_assert_int_eq(s21_mul(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);
  ck_assert_int_eq(result.bits[0], 15);

  ck_assert_int_eq(s21_mul(a, b, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_div_core) {
  s21_big_decimal big1, big2;
  int sign1 = 0, sign2 = 0;
  int scale1 = 0, scale2 = 0;
  s21_decimal result;

  uint32_t bits1[7] = {15, 0, 0, 0, 0, 0, 0};
  uint32_t bits2[7] = {3, 0, 0, 0, 0, 0, 0};

  big1 = create_big_decimal(bits1);
  big2 = create_big_decimal(bits2);

  int error = s21_div_core(big1, big2, sign1, sign2, scale1, scale2, &result);

  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 0);

  scale1 = 2;
  scale2 = 1;
  uint32_t bits3[7] = {123, 0, 0, 0, 0, 0, 0};
  uint32_t bits4[7] = {45, 0, 0, 0, 0, 0, 0};
  big1 = create_big_decimal(bits3);
  big2 = create_big_decimal(bits4);

  error = s21_div_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);

  sign1 = 0;
  sign2 = 1;
  scale1 = 0;
  scale2 = 0;
  error = s21_div_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 1);

  sign1 = 1;
  sign2 = 1;
  error = s21_div_core(big1, big2, sign1, sign2, scale1, scale2, &result);
  ck_assert_int_eq(error, DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_sign(result), 0);
}
END_TEST

START_TEST(test_div) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {15, 0, 0, 0};
  uint32_t b_bits[4] = {3, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_div(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 0);

  uint32_t zero_bits[4] = {0, 0, 0, 0};
  b = create_decimal(zero_bits);
  ck_assert_int_eq(s21_div(a, b, &result), DECIMAL_DIV_BY_ZERO);

  a = create_decimal(zero_bits);
  b_bits[0] = 5;
  b = create_decimal(b_bits);
  ck_assert_int_eq(s21_div(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);

  uint32_t a_bits2[4] = {10, 0, 0, 0};
  uint32_t b_bits2[4] = {3, 0, 0, 0};
  a = create_decimal(a_bits2);
  b = create_decimal(b_bits2);
  ck_assert_int_eq(s21_div(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result) > 0, 1);

  ck_assert_int_eq(s21_div(a, b, NULL), DECIMAL_ERROR);
}
END_TEST

// ==================== OTHER FUNCTIONS TESTS ====================

START_TEST(test_truncate) {
  s21_decimal a, result;

  uint32_t a_bits[4] = {123456, 0, 0, 0x00030000};
  uint32_t expected_bits[4] = {123, 0, 0, 0};

  a = create_decimal(a_bits);

  ck_assert_int_eq(s21_truncate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "truncate(123.456) = 123");

  a_bits[3] = 0x80030000;
  expected_bits[3] = 0x80000000;
  a = create_decimal(a_bits);
  ck_assert_int_eq(s21_truncate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "truncate(-123.456) = -123");

  uint32_t a_bits2[4] = {123, 0, 0, 0};
  a = create_decimal(a_bits2);
  ck_assert_int_eq(s21_truncate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, a, "truncate(123) = 123");

  uint32_t a_bits3[4] = {123456789, 0, 0, 0x001C0000};
  a = create_decimal(a_bits3);
  ck_assert_int_eq(s21_truncate(a, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result), 0);

  uint32_t zero_bits[4] = {0, 0, 0, 0x00050000};
  a = create_decimal(zero_bits);
  ck_assert_int_eq(s21_truncate(a, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_is_zero_decimal(result), 1);

  ck_assert_int_eq(s21_truncate(a, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_negate) {
  s21_decimal a, result;

  uint32_t a_bits[4] = {123, 0, 0, 0};
  uint32_t expected_bits[4] = {123, 0, 0, 0x80000000};

  a = create_decimal(a_bits);

  ck_assert_int_eq(s21_negate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "negate(123) = -123");

  a_bits[3] = 0x80000000;
  expected_bits[3] = 0;

  a = create_decimal(a_bits);

  ck_assert_int_eq(s21_negate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "negate(-123) = 123");

  uint32_t zero_bits[4] = {0, 0, 0, 0};
  uint32_t neg_zero_bits[4] = {0, 0, 0, 0x80000000};
  a = create_decimal(zero_bits);
  ck_assert_int_eq(s21_negate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(neg_zero_bits), "negate(0) = -0");

  a = create_decimal(neg_zero_bits);
  ck_assert_int_eq(s21_negate(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(zero_bits), "negate(-0) = 0");

  uint32_t scaled_bits[4] = {12345, 0, 0, 0x00020000};
  a = create_decimal(scaled_bits);
  ck_assert_int_eq(s21_negate(a, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result), 2);
  ck_assert_int_eq(s21_get_sign(result), 1);

  ck_assert_int_eq(s21_negate(a, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_floor) {
  s21_decimal a, result;

  uint32_t a_bits[4] = {123456, 0, 0, 0x00030000};
  uint32_t expected_bits[4] = {123, 0, 0, 0};

  a = create_decimal(a_bits);

  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "floor(123.456) = 123");

  a_bits[3] = 0x80030000;
  expected_bits[0] = 124;
  expected_bits[3] = 0x80000000;
  a = create_decimal(a_bits);
  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "floor(-123.456) = -124");

  uint32_t a_bits2[4] = {123, 0, 0, 0};
  a = create_decimal(a_bits2);
  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, a, "floor(123) = 123");

  a_bits2[3] = 0x80000000;
  a = create_decimal(a_bits2);
  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, a, "floor(-123) = -123");

  uint32_t a_bits3[4] = {99, 0, 0, 0x80020000};
  expected_bits[0] = 1;
  expected_bits[3] = 0x80000000;
  a = create_decimal(a_bits3);
  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "floor(-0.99) = -1");

  a_bits3[3] = 0x00020000;
  expected_bits[0] = 0;
  expected_bits[3] = 0;
  a = create_decimal(a_bits3);
  ck_assert_int_eq(s21_floor(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "floor(0.99) = 0");

  ck_assert_int_eq(s21_floor(a, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_round) {
  s21_decimal a, result;

  uint32_t a_bits[4] = {123456, 0, 0, 0x00030000};
  uint32_t expected_bits[4] = {123, 0, 0, 0};

  a = create_decimal(a_bits);

  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "round(123.456) = 123");

  a_bits[0] = 123556;
  expected_bits[0] = 124;
  a = create_decimal(a_bits);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "round(123.556) = 124");

  a_bits[0] = 123456;
  a_bits[3] = 0x80030000;
  expected_bits[0] = 123;
  expected_bits[3] = 0x80000000;
  a = create_decimal(a_bits);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "round(-123.456) = -123");

  a_bits[0] = 123556;
  expected_bits[0] = 124;
  a = create_decimal(a_bits);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, create_decimal(expected_bits),
                       "round(-123.556) = -124");

  uint32_t a_bits2[4] = {123, 0, 0, 0};
  a = create_decimal(a_bits2);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);
  assert_decimal_equal(result, a, "round(123) = 123");

  uint32_t a_bits3[4] = {15, 0, 0, 0x00010000};
  a = create_decimal(a_bits3);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);

  uint32_t a_bits4[4] = {25, 0, 0, 0x00010000};
  a = create_decimal(a_bits4);
  ck_assert_int_eq(s21_round(a, &result), DECIMAL_SUCCESS);

  ck_assert_int_eq(s21_round(a, NULL), DECIMAL_ERROR);
}
END_TEST

// ==================== EDGE CASE TESTS ====================

START_TEST(test_edge_add_overflow) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0};
  uint32_t b_bits[4] = {1, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_OVERFLOW);

  a_bits[3] = 0x80000000;
  b_bits[3] = 0x80000000;

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_add(a, b, &result), DECIMAL_UNDERFLOW);
}
END_TEST

START_TEST(test_edge_mul_overflow) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0};
  uint32_t b_bits[4] = {2, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  int code = s21_mul(a, b, &result);
  ck_assert(code == DECIMAL_OVERFLOW || code == DECIMAL_ERROR);
}
END_TEST

START_TEST(test_edge_division_precision) {
  s21_decimal a, b, result;

  uint32_t a_bits[4] = {1, 0, 0, 0};
  uint32_t b_bits[4] = {3, 0, 0, 0};

  a = create_decimal(a_bits);
  b = create_decimal(b_bits);

  ck_assert_int_eq(s21_div(a, b, &result), DECIMAL_SUCCESS);
  ck_assert_int_eq(s21_get_scale(result) > 0, 1);
}
END_TEST

START_TEST(test_edge_null_pointers) {
  s21_decimal dec = {{1, 0, 0, 0}};

  ck_assert_int_eq(s21_from_int_to_decimal(5, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_from_decimal_to_int(dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_from_float_to_decimal(1.0f, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_from_decimal_to_float(dec, NULL), DECIMAL_ERROR);

  ck_assert_int_eq(s21_add(dec, dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_sub(dec, dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_mul(dec, dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_div(dec, dec, NULL), DECIMAL_ERROR);

  ck_assert_int_eq(s21_truncate(dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_negate(dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_floor(dec, NULL), DECIMAL_ERROR);
  ck_assert_int_eq(s21_round(dec, NULL), DECIMAL_ERROR);
}
END_TEST

START_TEST(test_edge_invalid_decimals) {
  s21_decimal invalid_dec, result;

  uint32_t invalid_bits[4] = {123, 0, 0, 0x001D0000};
  invalid_dec = create_decimal(invalid_bits);

  int int_val;
  float float_val;
  ck_assert_int_eq(s21_from_decimal_to_int(invalid_dec, &int_val),
                   DECIMAL_ERROR);
  ck_assert_int_eq(s21_from_decimal_to_float(invalid_dec, &float_val),
                   DECIMAL_ERROR);

  s21_decimal valid_dec = {{123, 0, 0, 0}};

  ck_assert_int_eq(s21_add(invalid_dec, valid_dec, &result), DECIMAL_ERROR);
  ck_assert_int_eq(s21_add(valid_dec, invalid_dec, &result), DECIMAL_ERROR);

  ck_assert_int_eq(s21_is_equal(invalid_dec, valid_dec), 0);
  ck_assert_int_eq(s21_is_less(invalid_dec, valid_dec), 0);

  ck_assert_int_eq(s21_truncate(invalid_dec, &result), DECIMAL_ERROR);
  ck_assert_int_eq(s21_negate(invalid_dec, &result), DECIMAL_ERROR);
  ck_assert_int_eq(s21_floor(invalid_dec, &result), DECIMAL_ERROR);
  ck_assert_int_eq(s21_round(invalid_dec, &result), DECIMAL_ERROR);
}
END_TEST

// ==================== SUITE CREATION ====================

Suite *basic_functions_suite(void) {
  Suite *s = suite_create("Basic Functions");

  TCase *tc_basic = tcase_create("Basic");
  tcase_add_test(tc_basic, test_get_bit);
  tcase_add_test(tc_basic, test_get_set_sign);
  tcase_add_test(tc_basic, test_get_set_scale);
  tcase_add_test(tc_basic, test_clear_decimal);
  tcase_add_test(tc_basic, test_clear_big_decimal);
  tcase_add_test(tc_basic, test_is_zero_decimal);
  tcase_add_test(tc_basic, test_is_zero_big_decimal);
  tcase_add_test(tc_basic, test_validate_decimal);
  tcase_add_test(tc_basic, test_convert_to_from_big);
  tcase_add_test(tc_basic, test_decimal_divide_by_10);

  suite_add_tcase(s, tc_basic);
  return s;
}

Suite *helper_operations_suite(void) {
  Suite *s = suite_create("Helper Operations");

  TCase *tc_helpers = tcase_create("Helpers");
  tcase_add_test(tc_helpers, test_big_decimal_shift_left);
  tcase_add_test(tc_helpers, test_big_decimal_add);
  tcase_add_test(tc_helpers, test_big_decimal_sub);
  tcase_add_test(tc_helpers, test_big_decimal_mul);
  tcase_add_test(tc_helpers, test_big_decimal_compare);
  tcase_add_test(tc_helpers, test_big_decimal_multiply_by_10);
  tcase_add_test(tc_helpers, test_big_decimal_multiply_by_power_of_10);
  tcase_add_test(tc_helpers, test_normalize_decimals);
  tcase_add_test(tc_helpers, test_check_big_decimal_overflow);
  tcase_add_test(tc_helpers, test_round_and_reduce_step);
  tcase_add_test(tc_helpers, test_handle_overflow_and_scale);
  tcase_add_test(tc_helpers, test_big_decimal_div_with_remainder);

  suite_add_tcase(s, tc_helpers);
  return s;
}

Suite *conversion_suite(void) {
  Suite *s = suite_create("Conversion Functions");

  TCase *tc_convert = tcase_create("Conversion");
  tcase_add_test(tc_convert, test_from_int_to_decimal);
  tcase_add_test(tc_convert, test_from_decimal_to_int);
  tcase_add_test(tc_convert, test_parse_float_string);
  tcase_add_test(tc_convert, test_build_decimal_from_digits);
  tcase_add_test(tc_convert, test_from_float_to_decimal);
  tcase_add_test(tc_convert, test_from_decimal_to_float);

  suite_add_tcase(s, tc_convert);
  return s;
}

Suite *comparison_suite(void) {
  Suite *s = suite_create("Comparison Functions");

  TCase *tc_compare = tcase_create("Comparison");
  tcase_add_test(tc_compare, test_compare_with_normalization);
  tcase_add_test(tc_compare, test_is_equal);
  tcase_add_test(tc_compare, test_is_not_equal);
  tcase_add_test(tc_compare, test_is_less);
  tcase_add_test(tc_compare, test_is_less_or_equal);
  tcase_add_test(tc_compare, test_is_greater);
  tcase_add_test(tc_compare, test_is_greater_or_equal);

  suite_add_tcase(s, tc_compare);
  return s;
}

Suite *arithmetic_suite(void) {
  Suite *s = suite_create("Arithmetic Functions");

  TCase *tc_arithmetic = tcase_create("Arithmetic");
  tcase_add_test(tc_arithmetic, test_add_core);
  tcase_add_test(tc_arithmetic, test_add);
  tcase_add_test(tc_arithmetic, test_sub);
  tcase_add_test(tc_arithmetic, test_mul_core);
  tcase_add_test(tc_arithmetic, test_mul);
  tcase_add_test(tc_arithmetic, test_div_core);
  tcase_add_test(tc_arithmetic, test_div);

  suite_add_tcase(s, tc_arithmetic);
  return s;
}

Suite *other_functions_suite(void) {
  Suite *s = suite_create("Other Functions");

  TCase *tc_other = tcase_create("Other");
  tcase_add_test(tc_other, test_truncate);
  tcase_add_test(tc_other, test_negate);
  tcase_add_test(tc_other, test_floor);
  tcase_add_test(tc_other, test_round);

  suite_add_tcase(s, tc_other);
  return s;
}

Suite *edge_cases_suite(void) {
  Suite *s = suite_create("Edge Cases");

  TCase *tc_edge = tcase_create("Edge");
  tcase_add_test(tc_edge, test_edge_add_overflow);
  tcase_add_test(tc_edge, test_edge_mul_overflow);
  tcase_add_test(tc_edge, test_edge_division_precision);
  tcase_add_test(tc_edge, test_edge_null_pointers);
  tcase_add_test(tc_edge, test_edge_invalid_decimals);

  suite_add_tcase(s, tc_edge);
  return s;
}

// ==================== MAIN ====================

int main(void) {
  int number_failed = 0;
  SRunner *sr;

  sr = srunner_create(NULL);

  srunner_add_suite(sr, basic_functions_suite());
  srunner_add_suite(sr, helper_operations_suite());
  srunner_add_suite(sr, conversion_suite());
  srunner_add_suite(sr, comparison_suite());
  srunner_add_suite(sr, arithmetic_suite());
  srunner_add_suite(sr, other_functions_suite());
  srunner_add_suite(sr, edge_cases_suite());

  srunner_set_fork_status(sr, CK_NOFORK);
  setenv("CK_DEFAULT_TIMEOUT", "60", 1);

  srunner_run_all(sr, CK_NORMAL);

  number_failed = srunner_ntests_failed(sr);

  srunner_free(sr);

  return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}