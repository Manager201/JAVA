import java.util.*;

class prog11 {
    int[] m = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    String[] mn = { "0", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec" };

    public String check(int dn, int y) {
        if (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0))
            m[2] = 29;

        int s = 0, d = 0;
        String mon = "", date = "";
        for (int i = 1; i < m.length; i++) {
            s += m[i];
            if (s >= dn) {
                mon = mn[i];
                d = dn - (s - m[i]);
                break;
            }
        }

        switch (d % 10) {
            case 1:
                if (d == 11)
                    date = d + "th";
                else
                    date = d + "st";
                break;
            case 2:
                if (d == 12)
                    date = d + "th";
                else
                    date = d + "nd";
                break;
            case 3:
                if (d == 13)
                    date = d + "th";
                else
                    date = d + "rd";
                break;
            default:
                date = d + "th";
        }

        return date + " " + mon + " " + y;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Day Number = ");
        int dn = sc.nextInt();
        System.out.println("Year = ");
        int y = sc.nextInt();

        if (y % 4 != 0 && dn == 366) {
            System.out.println("Invalid Day Number!");
            System.exit(0);
        }

        System.out.println("Date before (n) = ");
        int n = sc.nextInt();

        if (y < 1000 || y > 9999) {
            System.out.println("Invalid year");
            System.exit(0);
        }
        if (n > dn) {
            System.out.println("Date before " + n + " days does not lie in the same year.");
            System.exit(0);
        }
        if (n < 1 || n > 366) {
            System.out.println("Invalid date");
            System.exit(0);
        }

        prog11 obj = new prog11();
        String out1 = obj.check(dn, y);
        System.out.println(out1);

        int newdn = dn - n;
        String out2 = obj.check(newdn, y);
        System.out.println("Date before " + n + " days = " + out2);
    }
}
