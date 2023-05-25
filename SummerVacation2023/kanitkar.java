import java.util.*;
class kanitkar
{
    public static void main(String[] args)
    {
        int n,s=0,d,j,x,r=0;
        Scanner sc=new Scanner(System.in); 
        System.out.println("Enter a  number");
        n=sc.nextInt();
        int m=n;
        while(n!=0)
        {
            d=n%10;
            s=s+d;
            n=n/10;
        }
        j=m*m;
        while(j!=0)
        {
            x=j%10;
            r=r+x;
            j=j/10;
        }
        if(s==r) 
        System.out.println("Kanitkar number");
        else
        System.out.println("It is not a kanitkar number");
    }
}
