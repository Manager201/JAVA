/*
A Prime-Adam integer is a positive integer which is a prime as well as an Adam number. Prime number: A number which has
only two factors, i.e. 1 and the number itself. Example: 2, 3, 5, 7 … etc.
Adam number: The Square of a number and the square of its reverse are reverse to each other.
Example- 1. Input: m = 13
Output: Yes! Prime-Adam
*/
import java.util.*;
class prime_adam{
    public static void main(String[] args) {           
    Scanner sc=new Scanner(System.in);
    System.out.println("Enter a number");
    int n;
    n=sc.nextInt();
    if(n<0)
    {
        System.out.println("Retry again with a positive number.");
        System.exit(0);
    }
    if(reverse(n*n)==(reverse(n)*reverse(n))&&isprime(n)==true)
    System.out.println("Yes! Prime-Adam");
    else
    System.out.println("No! Not Prime-Adam");
    }
    static boolean isprime(int a)
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
}
//sample outputs from 1 to 1000:
//2, 3, 11, 13, 31, 101, 103, 113, 211, 311 