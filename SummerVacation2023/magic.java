import java.util.*;
class magic
{
    public static void main(String[] args)
    {
        Scanner sc=new Scanner (System.in);
        int n,s=0,d;
        System.out.println("Enter a number");
        n=sc.nextInt();
        while(n!=0)
        {
            d=n%10;
            s=s+d;
            n=n/10;
        }
        if(s==1||s==10)
        System.out.println("Magic number");
            else
            System.out.println("It is not a magic number");
            
    }
}