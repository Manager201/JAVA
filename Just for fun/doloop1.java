import java.util.*;
class doloop1
{
    public static void main(String[] args)
    {
        int n,e=0,o=0;
        Scanner sc=new Scanner (System.in);
        do
        {
            System.out.println("Enter the number");
            n=sc.nextInt();
            if(n%2!=0&&n!=0)
            o++;
            else
            e++;
        }
        while(n!=0);
        System.out.println("Odd: "+o);
        System.out.println("Even: "+e);
        sc.close();
    }
    
}
