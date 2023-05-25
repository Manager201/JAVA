import java.util.*;
class amicable
{
    public static void main(String[] args)
    {
     Scanner sc=new Scanner(System.in);
     int a,b,y=0,i,j,z=0;
     System.out.println("Enter a number");
     a=sc.nextInt();
     System.out.println("Enter another number");
     b=sc.nextInt();
     for(i=1;i<a;i++)
     {
        if(a%i==0)
        y=y+i;
     }
     for(j=1;j<b;j++)
     {
        if(b%j==0)
        z=z+j;
     }
     if(a==z&&b==y)
     System.out.println("Amicable number");
     else
     System.out.println("it is not an amicable number");
    }
}