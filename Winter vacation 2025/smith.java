import java.util.*;
class smith
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number:");
        int n=sc.nextInt();
        int i=2,m=n,o=n,d,s=0,s1=0,a;
        while(n!=0)
        {
            d=n%10;
            s=s+d;
            n=n/10;
        }
        while(m!=1)
        {
            if(m%i==0)
            {
                a=i;
                while(a!=0)
                {
                    d=a%10;
                    s1=s1+d;
                    a=a/10;
                }
                m=m/i;
            }
            else
            i++;
        }
        if(s==s1)
        System.out.println(o+" is a smith number");
        else
        System.out.println(o+" is not a smith number");
    }
}

