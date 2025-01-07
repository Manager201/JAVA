/* Program 5:
Write a program to input a number and check whether it is an Emrip No. or not.

Input = 107
Output = 107 is an emrip number
 */
import java.util.*;
class pg5_emrip
{
    static int isprime(int a)
    {
        int i,c=0;
        for(i=1;i<=a;i++)
        {
        if(a%i==0)
        c++;
        }
        if(c==2)
        return 1;
        else
        return 0;
    }
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number");
        int n,d,r=0;
        n=sc.nextInt();
        int m=n;
        while(n!=0)
        {
            d=n%10;
            r=r*10+d;
            n=n/10;
        }
        if(isprime(r)==1&&isprime(m)==1)
        System.out.println(m+" is an emrip number");
        else
        System.out.println(m+" is not an emrip number");
        
    }
}