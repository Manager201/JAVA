/* Program 8:
A Smith number is a composite number, the sum of whose digits is the sum of the digits of its
prime factors (excluding 1). The first few such numbers are 4, 22, 27. . .
Write a program to input a number and display whether the number is a Smith number or not.

Input = 666
Output = 666 is a Smith number
 */
import java.util.*;
class pg8_smith 
{
    static int isPrime(int n) 
    {
        int i,c=0;
        for(i=1;i<=n;i++)
        {
            if(n%i==0)
            c++;
        }
        if(c==2)
        return 1;
        else
        return 0;
    }
    public static void main(String[] args) 
    {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a number:");
        int n = sc.nextInt();
        int i = 2, m = n, o = n, d, s = 0, s1 = 0, a;
        if (isPrime(n)==1) 
        {
            System.out.println(n + " is not a Smith number");
            System.exit(0); 
        }
        while (n != 0) 
        {
            d = n % 10;
            s = s + d;
            n = n / 10;
        }
        while (m != 1) 
        {
            if (m % i == 0) 
            {
                a = i;
                while (a != 0) 
                {
                    d = a % 10;
                    s1 = s1 + d;
                    a = a / 10;
                }
                m = m / i;
            } 
            else 
                i++;
        }
        if (s == s1)
            System.out.println(o + " is a Smith number");
        else
            System.out.println(o + " is not a Smith number");
    }
    
}
