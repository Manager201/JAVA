import java.util.*;
class wordwise1 
{
String str;
    wordwise1() 
    {
        str = ""; 
    }

    void readsent() 
    {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a sentence:");
        str = sc.nextLine();
    }

    
    int freq_vowel(String w) 
    {
        int c = 0;
        for (int i = 0; i < w.length(); i++) 
        {
            char ch = Character.toLowerCase(w.charAt(i));
            if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') 
                c++;
            
        }
        return c;
    }

 void arrange() 
    {
        str=str+" ";
        System.out.println("Word\t\tVowel Frequency");
        System.out.println("-------------------------------");
        int i,l = str.length();
        String w="";
        for(i=0;i<l;i++)
        {
            char ch = str.charAt(i);
            if(ch!=' ')
            w=w+ch;
            else{
            System.out.println(w+"\t\t" +freq_vowel(w));
            w="";
        }
            
        }
    }
    public static void main(String[] args) 
    {
        wordwise1 obj = new wordwise1(); 
        obj.readsent();                
        obj.arrange();                
    }
}
