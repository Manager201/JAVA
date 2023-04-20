import java.util.*;
class doloop2
{
    public static void main(String[] args)
    {
        int n,e=0,o=0,d;
        Scanner sc=new Scanner (System.in);
        do
        {
            System.out.println("Enter the number");
            n=sc.nextInt();
            while(n!=0)
            {
            d=n%2;
            if(n%2!=0&&n!=0)
            o++;
            else
            e++;
            n=n/10;
           
        }
        
        }
        while(n!=0);
        System.out.println("Odd: "+o);
        System.out.println("Even: "+e);
    }
    
}
