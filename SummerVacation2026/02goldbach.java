/*
 A Goldbach number is a positive even integer that can be expressed as the sum of two odd primes.
Example: 6 = 3 + 3
10 = 3 + 7
16 = 5 + 11
Write a program to input an even integer n where n> 9 and n< 100. Find all the odd prime pairs whose sum is equal to the
number n.
Test your program with the following sample data.
Example 1- Input n = 22
Output: Prime pairs are: 3, 19
5, 17
11, 11
Example 2- Input n = 25
Output: Invalid Input. Number is Odd.
Example 3- Input n = 128
Output: Invalid Input. Number out of range.
 */
import java.util.*;
class goldbach
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter an even number between 9 to 100");
        int n;
        n=sc.nextInt();
        if(n%2!=0)
        {
            System.out.println("Invalid Input. Number is Odd.");
            System.exit(0);
        }
        if(n<9||n>100)
        {
            System.out.println("Invalid Input. Number out of range.");
            System.exit(0);
        }
        int i,j;
        System.out.print("Prime pairs are: ");
        for(i=1;i<n;i++)
        {
            if(oddprime(i)==true)
            {
                for(j=i;j<n;j++)
                {
                    if(i+j==n&&oddprime(j)==true)
                    System.out.println(i+", "+j);
                }
            }
        }

    }
    static boolean oddprime(int a)
    {
        int i,c=0;
        for(i=1;i<=a;i++)
        {
            if(a%i==0)
            c++;
        }
        if(a%2!=0&&c==2)
        return true;
        else
        return false;
    }
}