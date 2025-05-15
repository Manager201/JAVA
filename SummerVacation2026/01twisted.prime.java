/*
A prime number is said to be twisted prime, if the new number obtained after reversing the digits is also a prime number.
Given two positive integers m and n, where m<n, Write a program to determine how many twisted primes are there in the
range between m and n (both inclusive) and output them.
Input: m = 100, n =200
Output: The Twisted Prime Numbers are: 101 107 113 131 149 151 157 167 179 181 191 199
Frequency of Twisted Prime Numbers is: 12jj
*/
import java.util.*;
class twisted_prime
{
 public static void main(String[] args) {
    Scanner sc=new Scanner(System.in);
    System.out.println("Enter lower limit 'm':");
    int m=sc.nextInt();
   System.out.println("Enter higher limit 'n':");
    int n=sc.nextInt();
    int i,freq=0;
    String tp="";
    if(m>n)
    {
      System.out.println("Invalid lower and higher limit");
      System.exit(0);
    }
    for(i=m;i<=n;i++)
    {
      if(isprime(i)==true&&isprime(reverse(i))==true)
         {
            tp=tp+" "+Integer.toString(i);
            freq++;
         }
    }
    if(freq>0)
    {
      System.out.println("The Twisted Prime Numbers are: "+tp);
      System.out.println("Frequency of Twisted Prime Numbers is: "+freq);
    }
    else
    System.out.println("No twisted primes are there in the range between "+m+" and "+n);
 }
     static boolean isprime(int a)
    {
      int i,p=0;
      for(i=1;i<=a;i++)
      {
         if(a%i==0)
         p++;
      }
      if(p==2)
      return true;
      else
      return false;
    }
    static int reverse(int a)
    {
      int r=0,d;
      while(a!=0)
      {
         d=a%10;
         r=r*10+d;
         a=a/10;
      }
      return r;
    }
}