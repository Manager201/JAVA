/* Program 10:
Write a program to input a sentence which may be terminated by either ‘.’ Or ‘?’. The words are
separated by one blank space and are in Upper Case. Form another sentence where length of first word
should be 1, length of second word should be 2 and so on. The last word will contain remaining letters.

Input = A MORNING WALK IS A BLESSING FOR THE WHOLE DAY.
Output = A MO RNI NGWA LKISA BLESSI NGFORTH EWHOLEDA Y.
 */
import java.util.*;
class pg10_sentence 
{
    public static void main(String[] args) 
    {
        String str = "", s = "", s1 = "";
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a sentence");
        str = sc.nextLine();
        if (str.endsWith(".") || str.endsWith("?")) 
        {
            s = str.replace(" ", "");
            int k = 0, j = 1, i=1, l = s.length();
            while(j <= l) 
            {
                k = k + i; 
                if (k > l) 
                { 
                    k = l;
                }
                while (j <= k) 
                { 
                    s1 = s1 + s.charAt(j - 1);
                    j++;
                }
                if (j <= l) 
                    s1 = s1 + " ";
                i++;
            }
            System.out.println(s1);
        } 
        else 
            System.out.println("The sentence must end with '.' or '?'.");
    }
}
