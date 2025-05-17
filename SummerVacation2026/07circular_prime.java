/*
A Circular Prime is a prime number that remains prime under cyclic shifts of its digits. When the leftmost digit is removed and
replaced at the end of the remaining string of digits, the generated number is still prime. The process is repeated until the
original number is reached again.
A number is said to be prime if it has only two factors 1 and itself.
Example: 131
311
113
Hence, 131 is a circular prime.
Input a positive number n and check whether it is a circular prime or not. The new numbers formed after the shifting of the
digits should also be displayed.
Example 1- Input n=197
Output: 197
971
719
197 is a Circular Prime.
Example 2- Input n=29
Output: 29
92
29 is not a Circular Prime.
 */
import java.util.*;
class circular_prime
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter a positive number : ");
        int n,len,i,digit=0,err=0;
        String str="",str2="",str1="";
        n=sc.nextInt();
        if(n<0)
        {
            System.out.println("Retry with a positive number.");
            System.exit(0);
        }
        if (isprime(n)==false) {
            System.out.println(n + " is not a Circular Prime.");
            System.exit(0);
        }
        str = Integer.toString(n);
        len = str.length();
        str1 = str;
        System.out.println(str);
        while (!str2.equals(str))
        {
            str2=str1.substring(1,len)+str1.charAt(0);
            if(!str2.equals(str))
            System.out.println(str2);
            if(isprime(Integer.parseInt(str2))==false)
            {
                err++;
                break;
            }
            str1=str2;
        }
        if(str2.equals(str)&&err==0)
        System.out.println(str+" is a Circular Prime.");
        else
        System.out.println(str+" is not a Circular Prime.");
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
}
/*
sample outputs from 1 to 1000:
2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, 97, 113, 
131, 197, 199, 311, 337, 373, 719, 733, 919, 971, 991

terminal output :
Enter a positive number : 719
719
197
971
719 is a Circular Prime.

Enter a positive number : 991
991
919
199
991 is a Circular Prime.
 */