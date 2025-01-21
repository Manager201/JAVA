/* Program 11:
Design a program to accept a day number (between 1 and 366), year (in 4 digits) from the user to
generate and display and corresponding date. Also accept another number 'n' from the user to compute
and display the past date corresponding to ‘n’ days before the generated date. Display an error message if
the value of the day number, year and n are not within the limit or not according to the condition specified.

Input - 
Day Number = 108
Year = 2006
Date before (n) = 18
Output - 
18th Apr 2006
Date before 18 days = 31st Mar 2006

Input -
Day Number = 50
Year = 2005
Date before (n) = 52
Output -
19th Feb 2005
Date before 52 days does not lie in the same year.

Input -
Day Number = 366
Year = 2009
Date before (n) = 52
Output = 
Invalid Day Number!
 */
import java.util.*;
class pg11_date
 
{
    int[] m = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    String[] mn = { "0", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec" };

    public String check(int dn, int y) 
    {
        if (y % 4 == 0)
            m[2] = 29;

        int s = 0, d = 0;
        String mon = "", date = "";
        for (int i = 1; i < m.length; i++) 
        {
            s =s+ m[i];
            if (s >= dn) 
            {
                mon = mn[i];
                d = dn - (s - m[i]);
                break;
            }
        }

        switch (d % 10) 
        {
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

    public static void main(String[] args) 
    {
        Scanner sc = new Scanner(System.in);

        System.out.println("Day Number = ");
        int dn = sc.nextInt();
        if(dn>366||dn<1)
        {
            System.out.println("Invalid Date");
            System.exit(0);
        }
        System.out.println("Year = ");
        int y = sc.nextInt();

        if (y % 4 != 0 && dn == 366) 
        {
            System.out.println("Invalid Day Number!");
            System.exit(0);
        }

        System.out.println("Date before (n) = ");
        int n = sc.nextInt();

        if (y < 1000 || y > 9999) 
        {
            System.out.println("Invalid year");
            System.exit(0);
        }       
        if (n < 0) 
        {
            System.out.println("Invalid date");
            System.exit(0);
        }

        pg11_date obj = new pg11_date();
        String out1 = obj.check(dn, y);
        System.out.println(out1);

        int newdn = dn - n;
        if (n > dn) 
        {
            System.out.println("Date before " + n + " days does not lie in the same year.");
            System.exit(0);
        }
        else
        {
        String out2 = obj.check(newdn, y);
        System.out.println("Date before " + n + " days = " + out2);
        }
    }
}
