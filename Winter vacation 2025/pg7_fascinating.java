/* Program 7
Write a program to input a number and check whether it is a Fascinating No. or not.

Input = 273
Output = 273 is a fascinating number
 */
import java.util.*;
class pg7_fascinating 
{
    public static void main(String[] args) 
    {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a number:");
        int a, i = 0, n, m, d, c = 0, e = 0;
        String w = "";
        a = sc.nextInt();
        for (i = 1; i <= 3; i++) 
            w = w + Integer.toString(a * i);
        n = Integer.parseInt(w);
        m = n;
        for (i = 0; i <= 9; i++) 
        {
            while (n != 0) 
            {
                d = n % 10;
                if (d == i)
                    c++;
                n = n / 10;
            }
            if (c > 1)
                e++;
            n = m;
            c = 0;
        }
        if (e > 0)
            System.out.println(a + " is not a fascinating number");
        else
            System.out.println(a + " is a fascinating number");

    }
}
