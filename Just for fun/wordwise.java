import java.util.*;
class wordwise
{
   String str;
    wordwise()
    {
        str="";
    }
    void readsent()
    {
        Scanner sc=new Scanner (System.in);
        System.out.println("Enter a sentence");
        str=sc.nextLine();
    }
    int freq_vowel(String w)
    {
        int i,l=w.length(),c=0;
        String z="AEIOUaeiou";
        for(i=0;i<l;i++)
        {
            char ch=w.charAt(i);
            if(z.indexOf(ch)>=0)
            c++;
        }
        return c;
    }
    void arrange()
    {
        str=str+" ";
        int i=0,l=str.length();
        String e="";
        for(i=0;i<l;i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
            e=e+ch;
            else {
                int f=freq_vowel(e);
            System.out.println(e+"\t"+f);
            e="";
            }
        }
    }
    public static void main(String[] args) {
        wordwise ob=new wordwise();
        ob.readsent();
        ob.arrange();
    }
}