/*
Write a program to check whether the array is in sorted order or not.
Example- Input: a [ ] = {1, 2, 4, 7, 10, 12, 13} Yes, Ascending Order
Input: a [ ] = {13, 10, 7, 4} Yes, Descending Order
Input: a [ ] = {6, 9, 2, 5, 8} Not sorted
 */
import java.util.*;
class sort_array
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter the size of an array : ");
        int size,i;
        String array="";
        size=sc.nextInt();
        int arr[]=new int[size];
        System.out.println("Enter array elements:");
        for(i=0;i<size;i++)
        {
            arr[i]=sc.nextInt();
        }
        array=array+"{";
        for(i=0;i<size;i++)
        {
            array=array+arr[i]+", ";
        }
        System.out.println(array.substring(0,array.length()-2)+"} "+sort(arr));

    }
    static String sort(int a[])
    {
        int i,desc=0,asc=0;
        for(i=0;i<a.length-1;i++)
        if(a[i]>=a[i+1]==false)
        {
            if(a[i]<=a[i+1])
            {
              asc++;
            }
        }
        else 
        desc++;
        if(asc>0&&desc>0)
        return "Not sorted";
        if(asc>0&&desc==0)
        return "Yes, Ascending Order";
        else
        return "Yes, Descending Order";
    }
}