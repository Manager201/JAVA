import java.util.*;
class hi
{
    public static void main(String[] args) 
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a=sc.nextInt();
            String a1=Integer.toString(a);
            int l=a1.length(),c=0;
            if(a1.charAt(0)==a1.charAt(l-1))
            c++;
            if(c==1)
            System.out.println(a1+" is a cyclo number");
            else
            System.out.println(a1+" not a cyclo number");
        }
    }