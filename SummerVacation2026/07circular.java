/*
A Circular Prime is a prime number that remains prime under cyclic shifts of its digits. When the leftmost digit is removed and
replaced at the end of the remaining string of digits, the generated number is still prime. The process is repeated until the
original number is reached again.
A number is said to be prime if it has only two factors 1 and itself.
Example: 131
311
113
Hence, 131 is a circular prime.
Input a positive number n and check whether it is a circular prime or not. The new numbers formed after the shifting of the
digits should also be displayed.
Example 1- Input n=197
Output: 197
971
719
197 is a Circular Prime.
Example 2- Input n=29
Output: 19
92
29 is not a Circular Prime.
 */