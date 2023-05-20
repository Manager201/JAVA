import java.util.*;
class expanded
{
    public static void main(String[] args)
    {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number");
        int n=sc.nextInt();
        int  d,s,c=0,p,m=n;
        while(m!=0){
            p=m%10;
            c++;
            m=m/10;
        }
        c--;
        while(c!=0)
    {
        
        d=n%(int)Math.pow(10,c);
        s=n-d;
        n=d;
        System.out.print(s+"+");
        c--;
        
    }
    System.out.print(n);

    }
    }
