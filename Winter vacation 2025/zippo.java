import java.util.*;
class zippo
{
    public static void main(String[] args) {
        {
            Scanner sc=new Scanner(System.in);
            System.out.println("Enter a number");
            int a=sc.nextInt();
            String s="",s1="",s2="";
            char ch,ch1,ch2;
            String a1=Integer.toString(a);   
            int l=a1.length(),i;
            for(i=1;i<l-1;i++)
            {
                ch=a1.charAt(i);
                s=s+ch;
            }
            ch1=a1.charAt(0);
            s1=s1+ch1;
            ch2=a1.charAt(l-1);
            s2=s2+ch2;
            if(Integer.parseInt(s)==0&&Integer.parseInt(s1)!=0&&Integer.parseInt(s2)!=0)
            System.out.println(a+" is a zippo number");
            else
            System.out.println(a+" is not a zippo number");
        }
    }
}