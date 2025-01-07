/* Program 1:
Write a program to input a number and check whether it is a Cyclo No. or not.

Input = 3453
Output = 3453 is a cyclo number
 */
import java.util.*;
class pg1_cyclo
{
    public static void main(String[] args) 
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a=sc.nextInt();
            String a1=Integer.toString(a);
            int l=a1.length();
            if(a1.charAt(0)==a1.charAt(l-1))
            System.out.println(a1+" is a cyclo number");
            else
            System.out.println(a1+" not a cyclo number");
        }
    }