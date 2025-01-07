/* Program 6:
Write a program to input a number and check whether it is a Special No. or not.

Input = 145
Output = 145 is a special number
 */
import java.util.*;
class pg6_special
{
    static int isfactorial(int n)
    {
        int i,f=1;
        for(i=1;i<=n;i++)
            f=f*i;
        return f;
    }
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a,b,s=0;
            a=sc.nextInt();
            b=a;
            while(b!=0)
            {
                s=s+isfactorial(b%10);
                b=b/10;
            }
            if(s==a)
            System.out.println(a+" is a special number");
            else
            System.out.println(a+" is not a special number");
    }
}
