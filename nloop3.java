import java.util.*;
class nloop3
{
    public static void main(String[] args)
    {
        Scanner sc= new Scanner(System.in);
        int i,d,n,e=0,o=0;
        for(i=1;i<=5;i++){
        System.out.println("Enter "+i+" number");
        n=sc.nextInt();
        while(n!=0)
        {
            d=n%10;
            if(n%2==0)
            e++;
            else
            o++;
            n=n/10;
        }
        System.out.println("Even: "+e);
        System.out.println("Odd: "+o);
        n=0;
        o=0;
        }
    sc.close();
    }
}