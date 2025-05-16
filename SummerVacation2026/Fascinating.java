/*
Write a program to input a number and check whether it is a Fascinating No. or not.
(Fascinating Numbers: Some numbers of 3 digits or more exhibit a very interesting property. The property is such that, when
the number is multiplied by 2 and 3, and both these products are concatenated with the original number, all digits from 1 to 9
are present exactly once, regardless of the number of zeroes.)
Example:
192x1=192
192x2=384
192x3=576
Concatenating the results: 192 384 576
 */
import java.util.*;
class fascinating
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.println("Enter a number of 3 digit or above");
        int n,i,j,digit,len,count=0,e=0;
        n=sc.nextInt();
        if(n<99)
        {
            System.out.println("The number is less than 3 digit");
            System.exit(0);
        }
        String str="",str2;
        for(i=1;i<=3;i++)
        {
            str=str+(n*i);
            if(i<3)
            str=str+" ";
        }
        str2=str.replace(" ", "");
        len=str2.length();
        int arr[]=new int[len];
        for(i=0; i<len; i++)
        {
        digit = Integer.parseInt(str2.substring(i, i + 1));
        arr[i] = digit;
        }
        for(i=1;i<=9;i++)
        {
            for(j=0;j<arr.length;j++)
            {
                if(i==arr[j])
                count++;
            }
            if(count>1)
            {
            System.out.println(n+ " is not a fascinating number.");
            e++;
            System.exit(0);
            }
            count=0;
        }
        if(e==0)
        System.out.println("Concatenating the results: "+str);
    }
}

/* 
sample outputs upto 10000 - 
192 - 192 384 576
219 - 219 438 657
273 - 273 546 819
327 - 327 654 981
 */ 