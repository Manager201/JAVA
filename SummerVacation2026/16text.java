/*
Write a program to accept a line of text consisting of the letters, comma and white space characters. Print the words of the
text in the following format:
Example- Input:
Emotions, controlled and directed to work, is character, By Swami Vivekananda
Output:
Vivekananda Swami By character is work to directed and controlled Emotions
 */
import java.util.*;
class text
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a sentence:");
        String str,str2="",w="";
        int i;
        str=sc.nextLine();
        str=str.replace(",","");
        str=str+" ";
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else
            {
            str2=w+" "+str2;
            w="";
            }
        }
        System.out.println(str2);
    }
}
/*
terminal output :
Enter a sentence:
Java, programming language, is fun and powerful
powerful and fun is language programming Java
 */