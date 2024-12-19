import java.util.*;
class swtchloop1
{
    void main()
    {
        Scanner sc= new Scanner (System.in);
        int ch;
        System.out.println("Enter1: Spy number");
        System.out.println("Enter2: Palindrone number");
        ch=sc.nextInt();
        sc.close();
        switch(ch)
        {
            case 1:

                int i,d,a=0,p=1,n;
                for(i=1;i<=15;i++)
                {
                    System.out.println("Enter" +i+" number");
                    n=sc.nextInt();
                    int m=n;
                    while(n!=0)
                    {
                        d=n%10;
                        a=a+d;
                        p=p*d;
                        n=n/10;
                    }
                    if(a==p)
                        System.out.println("It is a spy number: "+m);
                    else
                        System.out.println("It is not spy number: "+m);
                    a=0;
                    p=1;
                }

                break;
            case 2:
                int s=0;
                for(i=1;i<=10;i++)
                {
                    System.out.println("Enter a number: ");
                    n=sc.nextInt();
                    int j=n;
                    while(n!=0)
                    {
                        d=n%10;
                        s=s*10+d;
                        n=n/10;
                    }
                    if(s==j)
                        System.out.println("Palindrone: "+j);
                    else
                        System.out.println("Not Palindrone: "+j);
                        s=0;
                }
                break;
            default:
                System.out.println("Wrong choice");

        }
    }
}