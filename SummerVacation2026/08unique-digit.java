/*
Write a program to input two positive integer’s m and n. print the unique digit numbers in the specified range along with their
values in the following format:
Example- Input:
m = 100
n = 115
Output:
The Unique digit numbers are:
102, 103, 104, 105, 106, 107, 108, 109
Frequency of unique digit numbers is: 8
 */
import java.util.*;
class unique_digit {
    public static void main(String[] args) {
        int a, b, count, freq = 0, d, m, n, x, i;
        String print = "";
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter lower limit 'm':");
        m = sc.nextInt();
        System.out.println("Enter higher limit 'n':");
        n = sc.nextInt();

        if (m > n) {
            System.out.println("Invalid lower and higher limit");
            System.exit(0);
        }

        for (i = m; i <= n; i++) {
            a = i;
            count = 0;
            b = a;

            while (b != 0) {
                d = b % 10;
                b = b / 10;
                x = b;
                while (x != 0) {
                    if (x % 10 == d)
                        count++;
                    x = x / 10;
                }
            }

            if (count == 0) {
                print = print + i + ", ";
                freq++;
            }
        }

        System.out.println("The Unique digit numbers are:");
        if (freq > 0)
            System.out.println(print.substring(0, print.length() - 2));
        else
            System.out.println("None");

        System.out.println("Frequency of unique digit numbers is: " + freq);
    }
}
