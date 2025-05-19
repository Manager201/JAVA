/*
Write a program which takes a string (in Capital letters) terminated by a full stop. Arrange the words of the input string in
ascending order according to their length and also print the words that begin with a vowel.
Example- Input:
TODAY IS A COMPUTER PRACTICAL.
Output:
A IS TODAY COMPUTER PRACTICAL.
Words that begin with a vowel: A, IS
 */
import java.util.*;
class sentenceo
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a sentence:");
        String str,w="",t,z="AEIOU",vowel="";
        str=sc.nextLine();
        int i,c=0,s,si,j;
        if(str.compareTo(str.toUpperCase())!=0)
        {
            System.out.println("Retry with Capital letters");
            System.exit(0);
        }
        if (str.charAt(str.length() - 1) != '.') 
        {
            System.out.println("Invalid Input");
            System.exit(0);
        }
        str=str+" ";
        //counting words in the sentence
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else{
                c++;
                w="";
            }
        }
        //creating an array for future for storing words
        String a[]=new String[c];
        c=0; //this counter will not be used for indexing the array within loop
        //entering words into the array
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else{
                a[c]=w;
                c++;//increasing index value for each and every word into array
                w="";
            }
        }
        //selection sort on the length of words and then replacing words after comparison
        for(i=0;i<c;i++)
        {
            s=a[i].length();
            si=i;
            for(j=i+1;j<c;j++)
            {
                if(a[j].length()<s)
                {
                    s=a[j].length();
                    si=j;
                }
            }
            t=a[i];
            a[i]=a[si];
            a[si]=t;
        }
        //final printing of array and finding vowel
        for(i=0;i<c;i++)
        {
        System.out.print(a[i]+" ");
        if(z.indexOf(a[i].substring(0,1))>=0)
        vowel=vowel+a[i]+", ";
        }
        System.out.println("\nWords that begin with a vowel: "+vowel.substring(0,vowel.length()-2));
    }
}
/*
terminal output :
Enter a sentence:
TODAY IS A COMPUTER PRACTICAL.
A IS TODAY COMPUTER PRACTICAL. 
Words that begin with a vowel: A, IS
 */