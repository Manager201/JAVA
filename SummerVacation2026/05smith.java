/*
A Smith number is a composite number, the sum of whose digits is the sum of the digits of its prime factors (excluding 1).
The first few such numbers are 4, 22, 27. . .
Example- 1. Input: 58
Prime factors are: 2, 29
Sum of the digits are 5 + 8 = 13
Sum of the digits of the factors 2 + (2 + 9) =13

2. Input: 666
Prime factors are: 2, 3, 3, 37
Sum of the digits are 6 + 6 + 6 = 18
Sum of the digits of the factors 2 + 3 + 3 + (3 + 7) =18
Write a program to input a number and display whether the number is a Smith number or not.
 */
import java.util.*;
class smith
{
    static int n;
    static String pf="";
    static String sod="";
    static String sof="";
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number");
        n=sc.nextInt();
        if (isprime(n)==true) 
        {
            System.out.println("Retry with a composite number.");
            System.exit(0);
        }
        if (digitsum(reverse(n))==primefact_sum(n))
        {
            System.out.println("Prime factors are: "+pf);
            System.out.println("Sum of the digits are "+sod);
            System.out.println("Sum of the digits of the factors "+sof);
            System.out.println(n+" is a smith number");
        }
        else
            System.out.println(n+" is not a Smith number");

    }
    static boolean isprime(int a)
    {
        int i,count=0;
        for(i=1;i<=a;i++)
        if(a%i==0)
        count++;
        if(count>2)
        return false;
        else
        return true;
    }
    static int reverse(int a)
    {
        int d,r=0;
        while(a!=0)
        {
            d=a%10;
            r=r*10+d;
            a=a/10;
        }
        return r;
    }
    static int digitsum(int a)
    {
        int d,s=0,m=reverse(n);
        while(a!=0)
        {
            d=a%10;
            s=s+d;
            if(a==m)
            {
                if(a/10!=0)
                {
                sod=sod+d+" + ";
                m=m/10;
                }
                else
                sod=sod+d+" = "+s;
            }
            a=a/10;
        }
        return s;
    }
static int primefact_sum(int a)
{
    int i=2, sum=0;
    while (a>1)
    {
        if (a % i == 0 && isprime(i) == true)    
        {
            sum =sum+digitsum(i);
            a = a/i;
            if (a!=1)
                pf =pf+Integer.toString(i)+", ";
            else
                pf =pf+Integer.toString(i);
            if (i<10)
                sof =sof+i+" + ";
            else {
                int t=i;
                String tstr="";
                while (t!=0) {
                    int d=t%10;
                    if (t==i)
                    tstr=Integer.toString(d);
                    else
                    tstr=d+" + "+tstr;
                    t=t/10;
                }
                sof=sof+"(" +tstr+")"+" = "+sum;
            }

            i = 2;
        }
        else
            i++;
    }
    return sum;
    }
}
/*
sample outputs from 1 to 1000 :
4 22 27 58 85 94 121 166 202 265 274 319 346 355 378 382 391 
438 454 483 517 526 535 562 576 588 627 634 636 645 648 654 663 
666 690 706 728 729 762 778 825 852 861 895 913 915 922 958 985
 */