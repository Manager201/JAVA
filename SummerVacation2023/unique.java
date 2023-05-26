import java.util.*;

class unique {
    public static void main(String[] args) {
        int n, c = 0, d;
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a number");
        n = sc.nextInt();
        int x = n;
        while (n != 0) {
            d = n % 10;
            n = n / 10;
            x = n;
            while (x != 0) {
                if (x % 10 == d)
                    c++;
                x = x / 10;
            }

        }
        if (c == 0)
            System.out.println("Unique Number");
        else
            System.out.println("Not a Unique number");
    }
}