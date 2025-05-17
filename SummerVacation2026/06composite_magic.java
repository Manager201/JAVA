/*
A composite Magic number is a positive integer which is composite as well as a magic number.
Composite Number : A composite number is a number that has more than two factors.
Example- 10, 12 etc.
Magic Number : A magic number is a number in which the eventual sum of the digits is equal to 1.
Example- 37 = 3 + 7 = 10 = 1 + 0 = 1
Accept two positive integers m and n (assume m<n). Display the number of Composite Magic integers that are in the range
between m and n and output them along with frequency, in the format specified below.
Example- Input: m=20, n=95
Output: The Composite Magic integers are: 28, 46, 55, 64, 82, 91
Frequency of Composite Magic integers is = 6
 */
import java.util.*;
class composite_magic
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter lower limit 'm' : ");
        int m,n,i,count=0;
        String magicString="";
        m=sc.nextInt();
        System.out.print("Enter higher limit 'n' : ");
        n=sc.nextInt();
        if(m<0||n<0)
        {
            System.out.println("Retry with a positive number");
            System.exit(0);
        }
        if(m>n)
        {
        System.out.println("Invalid lower and higher limit");
        System.exit(0);
        }
        for(i=m+1;i<n;i++)
        {
            if(iscomposite(i)&&find_magic(i))
            {
            magicString=magicString+i+", ";
            count++;
            }
        }
        System.out.println("The Composite Magic integers are: "+(magicString.substring(0, magicString.length() - 2)));
        System.out.println("Frequency of Composite Magic integers is = "+count);
    }
    static boolean iscomposite(int a)
    {
        int i,count=0;
        for(i=1;i<=a;i++)
        if(a%i==0)
        count++;
        if(count>2)
        return true;
        else
        return false;
    }
    static boolean find_magic(int a)
    {
        int s=0,d;
        while(a>9)
        {
            while(a!=0)
            {
                d=a%10;
                s=s+d;
                a=a/10;
            }
            a=s;
            s=0;
        }
        if(a==1)
        return true;
        else
        return false;
    }
}
/*
sample outputs from 1 to 500 :
The Composite Magic integers are: 10, 28, 46, 55, 64, 82, 91, 100, 118, 136, 145, 154, 172, 190, 
208, 217, 226, 235, 244, 253, 262, 280, 289, 298, 316, 325, 334, 343, 352, 361, 370, 388, 406, 415, 
424, 442, 451, 460, 469, 478, 496

terminal output :
Enter lower limit 'm' : 361
Enter higher limit 'n' : 496
The Composite Magic integers are: 370, 388, 406, 415, 424, 442, 451, 460, 469, 478
Frequency of Composite Magic integers is = 10
 */