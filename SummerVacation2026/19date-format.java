/*
Write a program to input a date in the string format dd/ mm/ yyyy and print the date in the following format:
Example- 1. Input:
Date: 14/ 5/ 2024
Output:
Date: 14th/ May/ 2024
2. Input:
Date: 15/ 13/ 2024
Output:
Invalid Date!!!
 */
import java.util.*;
class date
{
        static int[] m = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
        static String[] mn = { "0", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec" };
        static String date,month,year;
        static int d=0,mon=0,y=0;
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Date: ");
        String n="";
        n=sc.nextLine();
        if(vailidity(n)==false)
        {
        System.out.println("Invalid Date!!!");
        System.exit(0);
        }
        print();
    }
    static boolean vailidity(String a)
    {
        a=a.replace('/', ' ');
        a=a.replace(" ", "");
        if(a.length()==7)
        {
        d=Integer.parseInt(a.substring(0,2));
        mon=Integer.parseInt(a.substring(2,3));
        y=Integer.parseInt(a.substring(3));
        }
        else if(a.length()==8)
        {
        d=Integer.parseInt(a.substring(0,2));
        mon=Integer.parseInt(a.substring(2,4));
        y=Integer.parseInt(a.substring(4));
        }
        else 
        {
            System.out.println("Invalid Date!!!");
            System.exit(0);
        }
        date=Integer.toString(d);
        month=Integer.toString(mon);
        year=Integer.toString(y);
        if(mon<=0||mon>12||d<=0||y<1000||y>9999)
        return false;
        if(y%4==0)
        m[2]=29;
        return true;
    }
    static void print()
    {
        switch(d%10)
        {
            case 1:
            if(d==11)
                date=date+"th/";
            else
                date=date+"st/";
            break;
            case 2:
            if(d==12)
                date=date+"th/";
            else
                date=date+"nd/";
            break;
            case 3:
            if(d==13)
                date=date+"th/";
            else
                date=date+"rd/";
            break;
            default:
            date=date+"th/";
        }
        System.out.println(date+" "+mn[mon]+"/ "+year);
    }
}
/*
terminal output :
Date: 19/ 19/ 2019
Invalid Date!!!

Date: 29/ 2/ 2024
29th/ Feb/ 2024

Date: 16/11/2024
16th/ Nov/ 2024
 */