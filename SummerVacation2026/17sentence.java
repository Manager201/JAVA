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
class sentenceoi
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a sentence:");
        String str,w="";
        int i,k=0,l=0;
        str=sc.nextLine();
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else
            {
            k++;
            w="";
            }
        }
        k++;
        String arr[]=new String[k];
        for(i=0;i<str.length();i++)
        {
            char ch=str.charAt(i);
            if(ch!=' ')
                w=w+ch;
            else
            {
            arr[l]=w;
            w="";
            l++;
            }
        }
        int len[]=new int[k];
        int sort_len[]=new int[k];
        for(i=0;i<k-1;i++)
        {
            len[i]=arr[i].length();
            sort_len[i]=len[i];
        }
        int s,si,t,j;
        for(i=0;i<k-1;i++)
        {
            s=sort_len[i];
            si=i;
            {
                for(j=i+1;j<k;j++)
                {
                    if(sort_len[j]<s)
                    {
                        s=sort_len[j];
                        si=j;
                    }
                }
                t=sort_len[i];
                sort_len[i]=sort_len[si];
                sort_len[si]=t;
            }
        }
        String str2="";
        for(i=0;i<arr.length;i++)
        {
            str2=str2+arr[index(i, len, sort_len)];
        }
        System.out.println(str2);
    }
    static int index(int a,int len[],int sort_len[])
    {
        int i,ind=0;
        for(i=0;i<len.length;i++)
        if(len[i]==(sort_len[a]))
        ind=i;
        return ind;
    }
}