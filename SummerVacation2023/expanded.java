import java.util.*;
class expanded
{
    public static void main(String[] args)
    {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number");
        int n=sc.nextInt();
        int c=0,p,m=n;
        while(n!=0){
            p=n%10;
            c++;
            n=n/10;
        }
        c--;
        int d,s;
        while(c!=0)
    {
        
        d=m%(int)Math.pow(10,c);
        s=m-d;
        m=d;
        System.out.print(s+"+");
        c--;
        
    }
    System.out.print(m);

    }
    }
