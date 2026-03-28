#include "s21_decimal.h"

// ==================== BASIC FUNCTIONS ====================

int s21_get_bit(s21_decimal decimal, int bit) {
  int result = (decimal.bits[bit / DECIMAL_BITS_IN_WORD] >>
                (bit % DECIMAL_BITS_IN_WORD)) &
               1;
  return result;
}

int s21_get_sign(s21_decimal decimal) {
  int result = 0;
  result = (decimal.bits[3] >> 31) & 1;
  return result;
}

void s21_set_sign(s21_decimal* decimal, int sign) {
  if (sign) {
    decimal->bits[3] |= 0x80000000;
  } else {
    decimal->bits[3] &= 0x7FFFFFFF;
  }
}

int s21_get_scale(s21_decimal decimal) {
  int result = 0;
  result = (decimal.bits[3] >> 16) & 0xFF;
  return result;
}

void s21_set_scale(s21_decimal* decimal, int scale) {
  if (scale < 0) scale = 0;
  if (scale > DECIMAL_MAX_SCALE) scale = DECIMAL_MAX_SCALE;
  decimal->bits[3] = (decimal->bits[3] & 0x80000000) | ((scale & 0xFF) << 16);
}

void s21_clear_decimal(s21_decimal* value) {
  for (int i = 0; i < 4; i++) value->bits[i] = 0;
}

void s21_clear_big_decimal(s21_big_decimal* value) {
  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) value->bits[i] = 0;
}

int s21_is_zero_decimal(s21_decimal value) {
  int result = 1;
  for (int i = 0; i < DECIMAL_WORDS_COUNT && result; i++)
    result = value.bits[i] == 0;
  return result;
}

int s21_is_zero_big_decimal(s21_big_decimal value) {
  int result = 1;
  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT && result; i++)
    result = value.bits[i] == 0;
  return result;
}

int s21_validate_decimal(s21_decimal value) {
  if (value.bits[3] & 0x7F00FFFF) {
    return DECIMAL_ERROR;
  }

  int scale = s21_get_scale(value);
  if (scale < 0 || scale > DECIMAL_MAX_SCALE) {
    return DECIMAL_ERROR;
  }

  return DECIMAL_SUCCESS;
}

s21_big_decimal s21_convert_to_big(s21_decimal value) {
  s21_big_decimal result = {0};
  for (int i = 0; i < 3; i++) result.bits[i] = value.bits[i];
  return result;
}

s21_decimal s21_convert_from_big_low(s21_big_decimal big_value) {
  s21_decimal result;
  for (int i = 0; i < DECIMAL_WORDS_COUNT; i++)
    result.bits[i] = big_value.bits[i];
  return result;
}

void s21_decimal_divide_by_10(s21_decimal* value) {
  uint64_t remainder = 0;

  for (int i = DECIMAL_WORDS_COUNT - 1; i >= 0; i--) {
    uint64_t current = ((uint64_t)remainder << 32) | value->bits[i];
    value->bits[i] = (uint32_t)(current / 10);
    remainder = current % 10;
  }
}

// ==================== HELPER OPERATIONS ====================

void s21_big_decimal_shift_left(s21_big_decimal* value) {
  uint32_t carry = 0;

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    uint32_t new_carry = value->bits[i] >> 31;
    value->bits[i] = (value->bits[i] << 1) | carry;
    carry = new_carry;
  }
}

int s21_big_decimal_add(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result) {
  int error = DECIMAL_SUCCESS;
  uint32_t carry = 0;
  s21_clear_big_decimal(result);

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    uint64_t sum = (uint64_t)value_1.bits[i] + value_2.bits[i] + carry;
    result->bits[i] = (uint32_t)sum;
    carry = (uint32_t)(sum >> 32);
  }

  if (carry) error = DECIMAL_OVERFLOW;
  return error;
}

int s21_big_decimal_sub(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result) {
  uint32_t borrow = 0;
  s21_clear_big_decimal(result);

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    uint64_t subtrahend = (uint64_t)value_2.bits[i] + borrow;

    if (value_1.bits[i] >= (uint32_t)subtrahend) {
      result->bits[i] = value_1.bits[i] - (uint32_t)subtrahend;
      borrow = 0;
    } else {
      result->bits[i] =
          (uint32_t)((uint64_t)value_1.bits[i] + 0x100000000ULL - subtrahend);
      borrow = 1;
    }
  }

  return DECIMAL_SUCCESS;
}

int s21_big_decimal_mul(s21_big_decimal value_1, s21_big_decimal value_2,
                        s21_big_decimal* result) {
  int error = DECIMAL_SUCCESS;
  s21_clear_big_decimal(result);

  if (!s21_is_zero_big_decimal(value_1) && !s21_is_zero_big_decimal(value_2)) {
    s21_big_decimal temp = {{0}};

    for (int i = 0; i < DECIMAL_BIG_MAX_BITS && error == DECIMAL_SUCCESS; i++) {
      if (GET_BIG_BIT(value_1, i)) {
        s21_big_decimal shifted = value_2;
        for (int j = 0; j < i; j++) s21_big_decimal_shift_left(&shifted);
        error = s21_big_decimal_add(temp, shifted, &temp);
      }
    }

    if (error == DECIMAL_SUCCESS) *result = temp;
  }

  return error;
}

int s21_big_decimal_compare(s21_big_decimal value_1, s21_big_decimal value_2) {
  int result = 0;

  for (int i = DECIMAL_BIG_WORDS_COUNT - 1; i >= 0 && !result; i--) {
    if (value_1.bits[i] > value_2.bits[i]) {
      result = 1;
    } else if (value_1.bits[i] < value_2.bits[i]) {
      result = -1;
    }
  }

  return result;
}

int s21_big_decimal_multiply_by_10(s21_big_decimal* value) {
  s21_big_decimal result = {{0}};
  uint64_t carry = 0;
  int error = DECIMAL_SUCCESS;

  for (int i = 0; i < DECIMAL_BIG_WORDS_COUNT; i++) {
    uint64_t temp = (uint64_t)value->bits[i] * 10 + carry;
    result.bits[i] = (uint32_t)temp, carry = temp >> 32;
  }

  if (carry)
    error = DECIMAL_OVERFLOW;
  else
    *value = result;
  return error;
}

int s21_big_decimal_multiply_by_power_of_10(s21_big_decimal* value, int power) {
  int error = DECIMAL_SUCCESS;

  for (int count = 0; count < power && error == DECIMAL_SUCCESS; count++) {
    error = s21_big_decimal_multiply_by_10(value);
  }

  return error;
}

int s21_normalize_decimals(s21_big_decimal* big_1, s21_big_decimal* big_2,
                           int scale_1, int scale_2) {
  int error = DECIMAL_SUCCESS;

  if (scale_1 != scale_2) {
    if (scale_1 > scale_2) {
      error = s21_big_decimal_multiply_by_power_of_10(big_2, scale_1 - scale_2);
    } else {
      error = s21_big_decimal_multiply_by_power_of_10(big_1, scale_2 - scale_1);
    }
  }

  return error;
}

int s21_check_big_decimal_overflow(s21_big_decimal value) {
  int overflow = 0;
  for (int i = DECIMAL_WORDS_COUNT; i < DECIMAL_BIG_WORDS_COUNT && !overflow;
       i++)
    overflow = value.bits[i] != 0;
  return overflow;
}

void s21_round_and_reduce_step(s21_big_decimal* big_result, int* scale) {
  s21_big_decimal remainder;
  s21_big_decimal temp_result;

  s21_big_decimal ten = {{10, 0, 0, 0, 0, 0, 0}};
  s21_big_decimal_div_with_remainder(*big_result, ten, &temp_result,
                                     &remainder);

  int round_up = 0;
  if (remainder.bits[0] > 5) {
    round_up = 1;
  } else if (remainder.bits[0] == 5) {
    if (temp_result.bits[0] & 1) {
      round_up = 1;
    }
  }

  if (round_up) {
    s21_big_decimal one = {{1, 0, 0, 0, 0, 0, 0}};
    s21_big_decimal_add(temp_result, one, big_result);
  } else {
    *big_result = temp_result;
  }

  *scale = *scale - 1;
}

int s21_handle_overflow_and_scale(s21_big_decimal* big_result, int* scale,
                                  int sign, s21_decimal* result) {
  int error = DECIMAL_SUCCESS;
  while ((s21_check_big_decimal_overflow(*big_result) ||
          *scale > DECIMAL_MAX_SCALE) &&
         *scale > 0) {
    s21_round_and_reduce_step(big_result, scale);
  }

  if (s21_check_big_decimal_overflow(*big_result)) {
    if (sign) {
      error = DECIMAL_UNDERFLOW;
    } else {
      error = DECIMAL_OVERFLOW;
    }
  } else if (*scale > DECIMAL_MAX_SCALE) {
    s21_clear_decimal(result);
    if (sign) s21_set_sign(result, 1);
    error = DECIMAL_SUCCESS;
  } else {
    *result = s21_convert_from_big_low(*big_result);
    s21_set_scale(result, *scale);
    s21_set_sign(result, sign);
  }

  return error;
}

int s21_big_decimal_div_with_remainder(s21_big_decimal value_1,
                                       s21_big_decimal value_2,
                                       s21_big_decimal* result,
                                       s21_big_decimal* remainder) {
  int error = DECIMAL_SUCCESS;
  s21_clear_big_decimal(result);
  s21_clear_big_decimal(remainder);

  if (s21_is_zero_big_decimal(value_2)) {
    error = DECIMAL_DIV_BY_ZERO;
  } else if (!s21_is_zero_big_decimal(value_1)) {
    int compare = s21_big_decimal_compare(value_1, value_2);
    if (compare < 0) {
      *remainder = value_1;
    } else {
      int msb_pos = -1;
      for (int i = DECIMAL_BIG_MAX_BITS - 1; i >= 0 && msb_pos == -1; i--) {
        if (GET_BIG_BIT(value_1, i)) msb_pos = i;
      }

      for (int i = msb_pos; i >= 0; i--) {
        s21_big_decimal_shift_left(remainder);
        if (GET_BIG_BIT(value_1, i)) SET_BIG_BIT(*remainder, 0, 1);

        if (s21_big_decimal_compare(*remainder, value_2) >= 0) {
          s21_big_decimal_sub(*remainder, value_2, remainder);
          SET_BIG_BIT(*result, i, 1);
        }
      }
    }
  }

  return error;
}

// ==================== CONVERSION FUNCTIONS ====================

int s21_from_int_to_decimal(int src, s21_decimal* dst) {
  int error = DECIMAL_ERROR;

  if (dst != NULL) {
    s21_clear_decimal(dst);

    if (src == 0) {
      error = DECIMAL_SUCCESS;
    } else {
      int is_negative = 0;
      unsigned int absolute_value = 0;

      if (src < 0) {
        is_negative = 1;
        if (src == INT_MIN) {
          absolute_value = (unsigned int)INT_MAX + 1;
        } else {
          absolute_value = (unsigned int)(-src);
        }
      } else {
        absolute_value = (unsigned int)src;
      }

      dst->bits[0] = absolute_value;
      if (is_negative) {
        s21_set_sign(dst, 1);
      }
      error = DECIMAL_SUCCESS;
    }
  }

  return error;
}

int s21_from_decimal_to_int(s21_decimal src, int* dst) {
  int error = DECIMAL_ERROR;

  if (dst != NULL && s21_validate_decimal(src) == DECIMAL_SUCCESS) {
    *dst = 0;

    s21_decimal temp = src;
    int sign = s21_get_sign(temp);
    s21_set_sign(&temp, 0);

    s21_decimal max_int = {{(uint32_t)INT_MAX, 0, 0, 0}};
    s21_decimal max_int_plus_one = {{(uint32_t)INT_MAX + 1, 0, 0, 0}};

    int scale = s21_get_scale(temp);
    s21_set_scale(&temp, 0);

    for (int i = 0; i < scale; i++) {
      s21_decimal_divide_by_10(&temp);
    }

    if (sign) {
      if (s21_is_greater(temp, max_int_plus_one)) {
        error = DECIMAL_ERROR;
      } else {
        uint32_t value = temp.bits[0];
        if (value == (uint32_t)INT_MAX + 1) {
          *dst = INT_MIN;
        } else {
          *dst = -(int)value;
        }
        error = DECIMAL_SUCCESS;
      }
    } else {
      if (s21_is_greater(temp, max_int)) {
        error = DECIMAL_ERROR;
      } else {
        *dst = (int)temp.bits[0];
        error = DECIMAL_SUCCESS;
      }
    }
  }

  return error;
}

int s21_parse_float_string(float src, char digits[], int* exponent,
                           int* negative) {
  int error = DECIMAL_SUCCESS;
  if (src == 0.0f) {
    digits[0] = '0';
    digits[1] = '\0';
    *exponent = 0;
    *negative = 0;
  } else {
    *negative = 0;
    if (src < 0.0f) {
      *negative = 1;
      src = -src;
    }

    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%.6e", src);
    char* e_ptr = strchr(buffer, 'e');
    if (e_ptr) {
      *exponent = atoi(e_ptr + 1);
      *e_ptr = '\0';
    }

    char* dot_ptr = strchr(buffer, '.');
    if (dot_ptr) {
      int fraction_len = 0;
      const char* read = dot_ptr + 1;
      char* write = dot_ptr;
      while (*read) {
        *write++ = *read++;
        fraction_len++;
      }
      *write = '\0';
      *exponent -= fraction_len;
    }

    strcpy(digits, buffer);
  }
  return error;
}

int s21_build_decimal_from_digits(const char* digits, int exponent,
                                  s21_decimal* dst) {
  int error = DECIMAL_SUCCESS;
  s21_clear_decimal(dst);

  for (int i = 0; digits[i] != '\0' && error == DECIMAL_SUCCESS; ++i) {
    s21_decimal temp = *dst;
    s21_decimal ten = {{10, 0, 0, 0}};
    s21_decimal digit = {{digits[i] - '0', 0, 0, 0}};
    error = s21_mul(temp, ten, &temp);
    if (error == DECIMAL_SUCCESS) {
      error = s21_add(temp, digit, dst);
    }
  }

  if (error == DECIMAL_SUCCESS && exponent != 0) {
    if (exponent > 0) {
      for (int j = 0; j < exponent && error == DECIMAL_SUCCESS; ++j) {
        s21_decimal temp = *dst;
        s21_decimal ten = {{10, 0, 0, 0}};
        error = s21_mul(temp, ten, dst);
      }
    } else {
      int scale = -exponent;
      if (scale > DECIMAL_MAX_SCALE) {
        s21_big_decimal big = s21_convert_to_big(*dst);
        int sign = s21_get_sign(*dst);
        error = s21_handle_overflow_and_scale(&big, &scale, sign, dst);
      } else {
        s21_set_scale(dst, scale);
      }
    }
  }

  return error;
}

int s21_from_float_to_decimal(float src, s21_decimal* dst) {
  int error = DECIMAL_ERROR;

  if (dst != NULL) {
    s21_clear_decimal(dst);

    if (src == 0.0f) {
      error = DECIMAL_SUCCESS;
      if (signbit(src)) {
        s21_set_sign(dst, 1);
      }
    } else if (isnan(src) || isinf(src)) {
      error = DECIMAL_ERROR;
    } else if (fabsf(src) < 1e-28f) {
      error = DECIMAL_ERROR;
    } else {
      char digits[50];
      int exponent = 0;
      int negative = 0;

      error = s21_parse_float_string(src, digits, &exponent, &negative);
      if (error == DECIMAL_SUCCESS) {
        error = s21_build_decimal_from_digits(digits, exponent, dst);
        if (error == DECIMAL_SUCCESS && negative) {
          s21_set_sign(dst, 1);
        }
      }
    }
  }

  return error;
}

int s21_from_decimal_to_float(s21_decimal src, float* dst) {
  int error = DECIMAL_ERROR;

  if (dst != NULL) {
    *dst = 0.0f;

    if (s21_validate_decimal(src) == DECIMAL_SUCCESS) {
      if (s21_is_zero_decimal(src)) {
        if (s21_get_sign(src)) {
          *dst = -0.0f;
        } else {
          *dst = 0.0f;
        }
        error = DECIMAL_SUCCESS;
      } else {
        double result = 0.0;
        for (int i = 0; i < DECIMAL_WORDS_COUNT; i++) {
          result += (double)src.bits[i] * pow(2.0, 32 * i);
        }

        int scale = s21_get_scale(src);
        for (int j = 0; j < scale; j++) {
          result /= 10.0;
        }

        if (s21_get_sign(src)) {
          result = -result;
        }

        *dst = (float)result;
        error = DECIMAL_SUCCESS;
      }
    }
  }

  return error;
}

// ==================== COMPARISON FUNCTIONS ====================

int s21_compare_with_normalization(s21_decimal value_1, s21_decimal value_2) {
  int result = 0;
  s21_big_decimal big1 = s21_convert_to_big(value_1);
  s21_big_decimal big2 = s21_convert_to_big(value_2);

  int scale1 = s21_get_scale(value_1);
  int scale2 = s21_get_scale(value_2);

  int normalize_error = s21_normalize_decimals(&big1, &big2, scale1, scale2);

  if (normalize_error == DECIMAL_SUCCESS) {
    result = s21_big_decimal_compare(big1, big2);
  }

  return result;
}

int s21_is_equal(s21_decimal value_1, s21_decimal value_2) {
  int result = 0;

  if (s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    int sign1 = s21_get_sign(value_1);
    int sign2 = s21_get_sign(value_2);

    if (s21_is_zero_decimal(value_1) && s21_is_zero_decimal(value_2)) {
      result = 1;
    } else if (sign1 == sign2) {
      result = s21_compare_with_normalization(value_1, value_2) == 0;
    }
  }

  return result;
}

int s21_is_less(s21_decimal value_1, s21_decimal value_2) {
  int result = 0;

  if (s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    int sign1 = s21_get_sign(value_1);
    int sign2 = s21_get_sign(value_2);

    if (sign1 != sign2) {
      result = sign1 && !sign2;
    } else {
      int compare = s21_compare_with_normalization(value_1, value_2);
      result = (sign1 == 0 && compare == -1) || (sign1 == 1 && compare == 1);
    }
  }

  return result;
}

int s21_is_less_or_equal(s21_decimal value_1, s21_decimal value_2) {
  int result = s21_is_less(value_1, value_2) || s21_is_equal(value_1, value_2);
  return result;
}

int s21_is_greater(s21_decimal value_1, s21_decimal value_2) {
  int result =
      !s21_is_less(value_1, value_2) && !s21_is_equal(value_1, value_2);
  return result;
}

int s21_is_greater_or_equal(s21_decimal value_1, s21_decimal value_2) {
  int result = !s21_is_less(value_1, value_2);
  return result;
}

int s21_is_not_equal(s21_decimal value_1, s21_decimal value_2) {
  int result = !s21_is_equal(value_1, value_2);
  return result;
}

// ==================== ARITHMETIC FUNCTIONS ====================

int s21_add_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result) {
  int error = DECIMAL_SUCCESS;
  s21_clear_decimal(result);
  int common_scale;

  if (scale1 > scale2) {
    s21_big_decimal_multiply_by_power_of_10(&big_2, scale1 - scale2);
    common_scale = scale1;
  } else if (scale2 > scale1) {
    s21_big_decimal_multiply_by_power_of_10(&big_1, scale2 - scale1);
    common_scale = scale2;
  } else {
    common_scale = scale1;
  }

  s21_big_decimal big_result = {{0}};
  int result_sign = 0;

  if (sign1 == sign2) {
    error = s21_big_decimal_add(big_1, big_2, &big_result);
    result_sign = sign1;
    if (error == DECIMAL_OVERFLOW && result_sign) {
      error = DECIMAL_UNDERFLOW;
    }
  } else {
    int compare = s21_big_decimal_compare(big_1, big_2);
    if (compare > 0) {
      error = s21_big_decimal_sub(big_1, big_2, &big_result);
      result_sign = sign1;
    } else if (compare < 0) {
      error = s21_big_decimal_sub(big_2, big_1, &big_result);
      result_sign = sign2;
    } else {
      s21_clear_decimal(result);
      return DECIMAL_SUCCESS;
    }
  }

  if (error == DECIMAL_SUCCESS && !s21_is_zero_big_decimal(big_result)) {
    error = s21_handle_overflow_and_scale(&big_result, &common_scale,
                                          result_sign, result);
  }

  return error;
}

int s21_add(s21_decimal value_1, s21_decimal value_2, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    s21_clear_decimal(result);

    if (s21_is_zero_decimal(value_1)) {
      *result = value_2;
      error = DECIMAL_SUCCESS;
    } else if (s21_is_zero_decimal(value_2)) {
      *result = value_1;
      error = DECIMAL_SUCCESS;
    } else {
      int sign1 = s21_get_sign(value_1);
      int sign2 = s21_get_sign(value_2);
      int scale1 = s21_get_scale(value_1);
      int scale2 = s21_get_scale(value_2);

      s21_big_decimal big1 = s21_convert_to_big(value_1);
      s21_big_decimal big2 = s21_convert_to_big(value_2);

      error = s21_add_core(big1, big2, sign1, sign2, scale1, scale2, result);
    }
  }

  return error;
}

int s21_sub(s21_decimal value_1, s21_decimal value_2, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    s21_decimal negated_value_2;
    s21_negate(value_2, &negated_value_2);

    error = s21_add(value_1, negated_value_2, result);
  }

  return error;
}

int s21_mul_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result) {
  int error = DECIMAL_SUCCESS;
  int result_sign = 0;
  int result_scale = scale1 + scale2;

  if (sign1 != sign2) {
    result_sign = 1;
  }

  s21_big_decimal big_result;
  error = s21_big_decimal_mul(big_1, big_2, &big_result);

  if (error == DECIMAL_OVERFLOW && result_sign) {
    error = DECIMAL_UNDERFLOW;
  }

  if (error == DECIMAL_SUCCESS) {
    error = s21_handle_overflow_and_scale(&big_result, &result_scale,
                                          result_sign, result);
  }

  return error;
}

int s21_mul(s21_decimal value_1, s21_decimal value_2, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    s21_clear_decimal(result);

    if (s21_is_zero_decimal(value_1) || s21_is_zero_decimal(value_2)) {
      error = DECIMAL_SUCCESS;
    } else {
      int sign1 = s21_get_sign(value_1);
      int sign2 = s21_get_sign(value_2);
      int scale1 = s21_get_scale(value_1);
      int scale2 = s21_get_scale(value_2);

      s21_big_decimal big1 = s21_convert_to_big(value_1);
      s21_big_decimal big2 = s21_convert_to_big(value_2);

      error = s21_mul_core(big1, big2, sign1, sign2, scale1, scale2, result);
    }
  }

  return error;
}

int s21_div_core(s21_big_decimal big_1, s21_big_decimal big_2, int sign1,
                 int sign2, int scale1, int scale2, s21_decimal* result) {
  int error = DECIMAL_SUCCESS;
  int result_sign = 0;
  if (sign1 != sign2) {
    result_sign = 1;
  }

  if (scale1 > scale2) {
    s21_big_decimal_multiply_by_power_of_10(&big_2, scale1 - scale2);
  } else if (scale2 > scale1) {
    s21_big_decimal_multiply_by_power_of_10(&big_1, scale2 - scale1);
  }

  s21_big_decimal big_result;
  s21_big_decimal big_remainder;
  error = s21_big_decimal_div_with_remainder(big_1, big_2, &big_result,
                                             &big_remainder);

  if (error == DECIMAL_SUCCESS) {
    int result_scale = 0;
    int counter = 0;
    while (s21_is_zero_big_decimal(big_remainder) == 0 &&
           counter < DECIMAL_MAX_SCALE + 2) {
      s21_big_decimal temp;
      s21_big_decimal temp_remainder;
      s21_big_decimal ten = {{10, 0, 0, 0, 0, 0, 0}};

      s21_big_decimal_mul(big_remainder, ten, &temp);
      s21_big_decimal_div_with_remainder(temp, big_2, &temp, &temp_remainder);

      s21_big_decimal_mul(big_result, ten, &big_result);
      s21_big_decimal_add(big_result, temp, &big_result);

      big_remainder = temp_remainder;
      result_scale = result_scale + 1;
      counter = counter + 1;
    }

    error = s21_handle_overflow_and_scale(&big_result, &result_scale,
                                          result_sign, result);
  }

  return error;
}

int s21_div(s21_decimal value_1, s21_decimal value_2, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value_1) == DECIMAL_SUCCESS &&
      s21_validate_decimal(value_2) == DECIMAL_SUCCESS) {
    s21_clear_decimal(result);

    if (s21_is_zero_decimal(value_2)) {
      error = DECIMAL_DIV_BY_ZERO;
    } else if (s21_is_zero_decimal(value_1)) {
      error = DECIMAL_SUCCESS;
    } else {
      int sign1 = s21_get_sign(value_1);
      int sign2 = s21_get_sign(value_2);
      int scale1 = s21_get_scale(value_1);
      int scale2 = s21_get_scale(value_2);

      s21_big_decimal big1 = s21_convert_to_big(value_1);
      s21_big_decimal big2 = s21_convert_to_big(value_2);

      error = s21_div_core(big1, big2, sign1, sign2, scale1, scale2, result);
    }
  }

  return error;
}

// ==================== OTHER FUNCTIONS ====================

int s21_truncate(s21_decimal value, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value) == DECIMAL_SUCCESS) {
    *result = value;
    int scale = s21_get_scale(*result);

    s21_set_scale(result, 0);
    int i = 0;
    while (i < scale) {
      s21_decimal_divide_by_10(result);
      i = i + 1;
    }

    error = DECIMAL_SUCCESS;
  }

  return error;
}

int s21_negate(s21_decimal value, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value) == DECIMAL_SUCCESS) {
    *result = value;
    int current_sign = s21_get_sign(*result);

    if (current_sign) {
      s21_set_sign(result, 0);
    } else {
      s21_set_sign(result, 1);
    }

    error = DECIMAL_SUCCESS;
  }

  return error;
}

int s21_floor(s21_decimal value, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value) == DECIMAL_SUCCESS) {
    s21_truncate(value, result);

    int is_negative = s21_get_sign(value);
    int has_fraction = s21_is_equal(value, *result) == 0;

    if (is_negative && has_fraction) {
      s21_decimal one = {{1, 0, 0, 0}};
      s21_sub(*result, one, result);
    }

    error = DECIMAL_SUCCESS;
  }

  return error;
}

int s21_round(s21_decimal value, s21_decimal* result) {
  int error = DECIMAL_ERROR;

  if (result != NULL && s21_validate_decimal(value) == DECIMAL_SUCCESS) {
    int sign = s21_get_sign(value);
    int scale = s21_get_scale(value);

    if (scale == 0) {
      *result = value;
      error = DECIMAL_SUCCESS;
    } else {
      s21_decimal positive = value;
      s21_set_sign(&positive, 0);

      s21_decimal truncated;
      s21_truncate(positive, &truncated);

      s21_decimal remainder;
      s21_sub(positive, truncated, &remainder);

      s21_decimal half = {{5, 0, 0, 0}};
      s21_set_scale(&half, 1);

      int should_add_one = s21_is_greater_or_equal(remainder, half);

      if (should_add_one) {
        s21_decimal one = {{1, 0, 0, 0}};
        s21_add(truncated, one, &truncated);
      }

      s21_set_sign(&truncated, sign);
      *result = truncated;
      error = DECIMAL_SUCCESS;
    }
  }

  return error;
}