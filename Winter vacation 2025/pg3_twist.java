/* Program 3:
Write a program to input a number and check whether it is a Twist No. or not.

Input = 2345
Output = 2345 is a twist number
 */
import java.util.*;
class pg3_twist
{
    public static void main(String[] args) 
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a=sc.nextInt();
            String s1="",s2="";
            String a1=Integer.toString(a);   
            int l=a1.length();
             s1=s1+a1.charAt(0);
             s2=s2+a1.charAt(l-1);
             if(Integer.parseInt(s1)%2==0&&Integer.parseInt(s2)%2!=0||Integer.parseInt(s1)%2!=0&&Integer.parseInt(s2)%2==0)
            System.out.println(a+" is a twist number");
            else 
            System.out.println(a+" is not a twist number");
            
        } 
}
