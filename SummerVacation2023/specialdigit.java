import java.util.*;

class specialdigit {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a number");
        int n = sc.nextInt();
        int s = 0, p = 1, d, m = n;
        if(n>=10&&n<=99) 
        {
            while (n != 0) 
            {
                d = n % 10;
                s = s + d;
                p = p * d;
                n = n / 10;
            }
            if (s + p == m)
                System.out.println("Special 2-digit number");
            else
                System.out.println("It is not a Special 2-digit number");
        } else
            System.out.println("It is not a 2-digit number");
    }
}
