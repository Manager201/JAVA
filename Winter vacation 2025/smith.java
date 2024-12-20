import java.util.*;
class smith
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number:");
        int n=sc.nextInt();
        int o=n,m=n,i=2,d,s=0,s1=0,b,c=0;
        while(n!=0)
        {
            d=n%10;
            c++;
            s=s+d;
            n=n/10;
        }
        while(m!=1)
        {
            if(m%1==0)
            {
                b=1;
                while(b!=0)
                {
                    d=b%10;
                    s1=s1+d;
                    b=b/10;
                }
                m=m/i;
            }
            else
            i++;
        }
        if(s==s1)
        System.out.println(o+" is a smith number");
        else
        System.out.println(o+" is not a smith number");
    }
}

/**
 import java.util.*;

class smith {
    static int sumof(int m) {
        int d, s = 0;
        while (m != 0) {
            d = m % 10;
            s = s + d;
            m = m / 10;
        }
        return s;
    }

    static int isprime(int n) {
        int s = 0;
        for (int i = 2; i <= n; i++) {
            while (n % i == 0) {
                s = s + sumof(i);
                n = n / i;
            }
        }
        return s;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a number:");
        int a, i, c = 0;
        a = sc.nextInt();
        for (i = 1; i <= a; i++) {
            if (a % i == 0) {
                c++;
            }
        }
        if (c == 2) {
            System.out.println(a + " is not a Smith number");
        } else {
            if (sumof(a) == isprime(a))
                System.out.println(a + " is a Smith number.");
            else
                System.out.println(a + " is not a Smith number.");
        }
    }
}

 */