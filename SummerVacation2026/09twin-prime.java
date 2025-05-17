/*
Write a program to input a positive integer, find twin prime no’s closer to number.
Example- Input: n = 22
Output: Twin prime after number = (29, 31)
Twin prime before number = (17, 19)
Nearest twin prime number = (17, 19)
 */
import java.util.*;
class twin_prime
{
    static int n,dA,dB;
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter a positive number : ");
        n=sc.nextInt();
        if(n<0)
        {
            System.out.println("Retry with a positive number.");
            System.exit(0);
        }
        System.out.println("Twin prime after number = "+after_prime(n));
        System.out.println("Twin prime before number = "+before_prime(n));
        if(dA<dB)
        System.out.println("Nearest twin prime number = "+after_prime(n));
        else
        System.out.println("Nearest twin prime number = "+before_prime(n));
    }
    static boolean prime(int a)
    {
        int i,count=0;
        for(i=1;i<=a;i++)
        if(a%i==0)
        count++;
        if(count==2)
        return true;
        else
        return false;
    }
    static String after_prime(int a)
    {
        int c=0;
        String ap="";
        while(c!=1)
        {
            if(prime(a)&&prime(a+2))
            {
            ap=ap+"("+a+", "+(a+2)+")";
            c++;
            }
            else a++;
        }
        dA=a-n;
        return ap;
    }
        static String before_prime(int a)
    {
        int c=0;
        String bp="";
        while(c!=1)
        {
            if(prime(a)&&prime(a-2))
            {
            bp=bp+"("+(a-2)+", "+a+")";
            c++;
            }
            else a--;
        }
        dB=n-a;
        return bp;
    }
}
/*
terminal output :
Enter a positive number : 53
Twin prime after number = (59, 61)
Twin prime before number = (41, 43)
Nearest twin prime number = (59, 61)
 */