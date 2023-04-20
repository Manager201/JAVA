import java.util.*;
public class nloop_28
{
    public static void main(String[] args){
        int d, i, s=0,n;
        Scanner sc=new Scanner(System.in);
        for(i=1;i<=15;i++)
        {
            System.out.println(i+". Enter the number");
            n=sc.nextInt();
            
            int r=n;
            while(n!=0)
            {
                d=n%10;
            s=s*10+d;
            n=n/10;
        }
        
        if(s==r)
        System.out.println("Palindrone no."+r);
        else
        System.out.println("Not palindorne no."+r);
        s=0;
        }
        sc.close();
    }
}