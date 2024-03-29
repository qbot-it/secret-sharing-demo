import random
import sympy
import functools


class SharesData:
    prime: int
    shares: list

    def __init__(self, prime: int, shares: list):
        self.prime = prime
        self.shares = shares

class SecretSharing:

    def generate_shares(self, secret: str, min_shares: int, shares: int) -> SharesData:
        bit_length = len(secret.encode('utf-8')) * 8 * 2
        prime = self.__generate_prime(bit_length)

        return SharesData(prime, self.__generate_shares(self.__string_to_number(secret), min_shares, shares, prime))

    def reconstruct_secret(self, provided_shares: list, prime: int) -> str:
        return self.__number_to_string(self.__lagrange_interpolation(provided_shares, prime))

    def __generate_prime(self, bits):
        """ Generate a prime number approximately of a given bit length. """
        lower_bound = 1 << (bits - 1)
        upper_bound = (1 << bits) - 1

        return sympy.randprime(lower_bound, upper_bound)


    def __generate_polynomial(self, secret, degree, prime):
        """ Generate a polynomial with a given secret as constant term """
        return [secret] + [random.randint(0, prime) for _ in range(degree)]

    def __evaluate_polynomial(self, coeffs, x, prime):
        """ Evaluate the polynomial at a given x value """
        return sum([coeff * (x ** power) for power, coeff in enumerate(coeffs)]) % prime

    def __generate_shares(self, secret, threshold, total_shares, prime):
        """ Generate secret shares """
        polynomial = self.__generate_polynomial(secret, threshold - 1, prime)
        shares = [(i, self.__evaluate_polynomial(polynomial, i, prime))
                  for i in range(1, total_shares + 1)]

        return shares

    def __string_to_number(self, s):
        """ Convert a string to a number by converting each character to its ASCII value """

        return int(''.join(f"{ord(c):03d}" for c in s))

    def __number_to_string(self, n):
        """ Convert a number back to a string by converting each group of digits to a character """
        s = str(n)
        # Ensure the string length is a multiple of 3
        while len(s) % 3 != 0:
            s = '0' + s

        return ''.join(chr(int(s[i:i + 3])) for i in range(0, len(s), 3))

    def __lagrange_interpolation(self, shares, prime):
        """ Reconstruct the secret using Lagrange interpolation """

        def product(seq):
            return functools.reduce(lambda a, b: a * b, seq, 1)

        sums = 0
        for j, share_j in shares:
            terms = [(x, share_x) for x, share_x in shares if x != j]
            prod = product([(0 - x) * pow(j - x, -1, prime)
                            for x, _ in terms]) % prime
            sums += share_j * prod

        return sums % prime