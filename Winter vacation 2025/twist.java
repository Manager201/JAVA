import java.util.*;
class twist
{
    public static void main(String[] args) {
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number:");
            int a=sc.nextInt();
            String s1="",s2="";
            String a1=Integer.toString(a);   
            int l=a1.length(),i;
            for(i=0;i<l;i++)
            {
                char ch=a1.charAt(i);
                if(i%2==0)
                s1=s1+ch;
                else
                s2=s2+ch;
            }
            if(Integer.parseInt(s1)==Integer.parseInt(s2))
            System.out.println(a+" is a twist number");
            else 
            System.out.println(a+" is not a twist number");
            
        }
    }
}