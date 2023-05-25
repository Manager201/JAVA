import java.util.*;
class lead{
    public static void main(String[] args)
    {
        Scanner sc=new Scanner (System.in);
        System.out.println("Enter a number");
        int n=sc.nextInt();
        int d,e=0,o=0;
        while(n!=0)
        {
            d=n%10;
            if(d%2==0)
            e=e+d;
            else
            o=o+d;
            n=n/10;
        }
        if(e==o)
        System.out.println("Lead Number");
        else
        System.out.println("It is not a lead Number");
}
}
