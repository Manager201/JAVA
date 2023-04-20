import java.util.*;
class forloop1 
{
    public static void main(String[] args)
    {
        Scanner sc= new Scanner(System.in);
        int l,i,h,f,c,n,m;
        System.out.println("Enter 1: LCM");
        System.out.println("Enter 1: HCF");
        n=sc.nextInt();
        switch(n)
        {
            case 1:
                System.out.println("Enter two numbers");
                l=sc.nextInt();
                c=sc.nextInt();
                for(i=1;i<=l*c;i++)
                {
                    if(i%l==0&&i%c==0)
                        System.out.println("LCM: "+i);
                    break;
                }
                break;
            case 2:
                System.out.println("Enter two numbers");
                h=sc.nextInt();
                f=sc.nextInt();
                m=(int)Math.pow(h,f);
                for(i=m;i>1;i--)
                {
                    if(h%i==0&&f%i==0)
                        System.out.println("HCF: "+i);
                    break;
                }
                break;
            default:
                System.out.println("Wrong Choice");

        }

    }
}