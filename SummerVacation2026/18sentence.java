/*
Write a program to input a sentence which may be terminated by either ‘.’, ‘?’ or ‘!’ only. The words may be separated by
more than one blank space and are in UPPER CASE.
Perform the following tasks:
a) Find the number of words beginning and ending with a vowel.
b) Place the words which begin and end with a vowel at the beginning, followed by the remaining words as they occur
in the sentence.
Test your program with the sample date and some random data:
Example 1: Input: YOU MUST AIM TO BE A BETTER PERSON TOMORROW THAN YOU ARE TODAY.
Output: Number of words beginning and ending with a vowel = 2
A ARE YOU MUST AIMTO BE BETTER PERSON TOMORROW THAN YOU TODAY
Example 2: Input: HOW ARE YOU#
Output: Invalid Input
 */
import java.util.*;
class sentences
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a sentence terminated by either ‘.’, ‘?’ or ‘!’: ");
        String str,z="AEIOU",w="",str2="",str3="";
        int i,v=0;
        str=sc.nextLine();
        if(str.compareTo(str.toUpperCase())!=0)
        {
            System.out.println("Retry with UpperCase characters");
            System.exit(0);
        }
        char end=str.charAt(str.length() - 1);
        if (end != '.' && end != '?' && end != '!') 
        {
            System.out.println("Invalid Input");
            System.exit(0);
        }
        str=str+" ";
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else
            {
                if (z.indexOf(w.charAt(0)) >= 0 && z.indexOf(w.charAt(w.length() - 1)) >= 0)
                {
                v++;
                str2 = str2 + w + " ";
                }
                else
                str3=str3+w+" ";
                w="";
            }
        }
        System.out.println("Number of words beginning and ending with a vowel = "+v);
        System.out.println(str2+str3);
    }
}
/*
terminal output :
Enter a sentence terminated by either ‘.’, ‘?’ or ‘!’: 
HOW ARE YOU///
Invalid Input

Enter a sentence terminated by either ‘.’, ‘?’ or ‘!’: 
HOW ARE YOU!
Number of words beginning and ending with a vowel = 1
ARE HOW YOU! 

Enter a sentence terminated by either ‘.’, ‘?’ or ‘!’: 
YOU MUST AIM TO BE A BETTER PERSON TOMORROW THAN YOU ARE TODAY.
Number of words beginning and ending with a vowel = 2
A ARE YOU MUST AIM TO BE BETTER PERSON TOMORROW THAN YOU TODAY. 
 */