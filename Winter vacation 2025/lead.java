import java.util.*;
class lead
{
    public static void main(String[] args) 
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a=sc.nextInt();
            int d,e=0,o=0,b=a;
           while(a!=0)
           {
            d=a%10;
            if(d%2==0)
            e=e+d;
            else
            o=o+d;
           }
           if(e==o)
           System.out.println(b+" is a lead number");
           else 
           System.out.println(b+" is not a lead number");
    }
}