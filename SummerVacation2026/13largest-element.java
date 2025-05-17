/*
Given a square matrix a [ ] [ ] of order n. Input the value for n and the positive integers in the matrix and perform the following
operations:
1. Display the original matrix.
2. Print the row and column position of the largest element of the matrix.
3. Print the row and column position of the second largest element of the matrix.
4. Sort the elements of the rows in the ascending order and display the new matrix.
Example- Input: n = 3
a [ ] [ ]
5 8 3
7 4 6
9 1 2
Output:
5 8 3
7 4 6
9 1 2
The largest element 9 is in row 3 and column 1
The second largest element 8 is in row 1 and column 2
Sorted list:
3 5 8
4 6 7
1 2 9
 */
import java.util.*;
class largest_elem
{
    static int k,i,j,n,row=0,column=0,q,r,s,si,t;
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter order 'n' for a square matrix: ");
        n=sc.nextInt();
        System.out.println("Enter elements of the matrix-");
        int a[][]=new int[n][n];
        int b[][]=new int[n][n];
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                a[i][j]=sc.nextInt();
                if(a[i][j]<0)
                {
                    System.out.println("Retry with a positive number.");
                    System.exit(0);
                }
            }
        }
        original_matrix(a, n);
        sorted_matrix(a, b, n);
        largest_element(a, n);
        System.out.println("The largest element "+k+" is in row "+(row+1)+" and column "+(column+1));
        second_largest(a, n);
        System.out.println("The second largest element "+k+" is in row "+(row+1)+" and column "+(column+1));
        System.out.println("Sorted list:");
        original_matrix(b, n);
    }
    //original matrix : task 1
    static void original_matrix(int a[][],int n)
    {
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                if(a[i][j]<10)
                System.out.print(a[i][j]+"  ");
                else
                System.out.print(a[i][j]+" ");
            }
            System.out.println();
        }
    }
    //largest element : task 2
    static void largest_element(int a[][],int n)
    {
        k=a[0][0];
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                if(a[i][j]>k)
                {
                    k=a[i][j];
                    row=i;
                    column=j;
                }
            }
        }
    }
    //second largest element : task 3
    static void second_largest(int a[][],int n)
    {
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                if(a[i][j]==k)
                a[i][j]=0;
            }
        }
        largest_element(a, n);
    }
   //sorted row of matrix :task 4
    static void sorted_matrix(int a[][], int b[][], int n)
    {
        int z[]=new int[n];
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                z[j]=a[i][j];
            }
            for(q=0;q<n-1;q++)
            {
                s=z[q];
                si=q;
                for(r=q+1;r<n;r++)
                {
                    if(z[r]<s)
                    {
                        s=z[r];
                        si=r;
                    }
                }
                t=z[q];
                z[q]=z[si];
                z[si]=t;
            }
            for(q=0;q<n;q++)
                b[i][q]=z[q];
        }
    }
}
/*
terminal output :
Enter order 'n' for a square matrix: 4
Enter elements of the matrix-
5
48
6
-8
Retry with a positive number.

Enter order 'n' for a square matrix: 3
Enter elements of the matrix-
12
8
9
4
16
7
3
9
1
12 8  9  
4  16 7  
3  9  1  
The largest element 16 is in row 2 and column 2
The second largest element 12 is in row 2 and column 2
Sorted list:
8  9  12 
4  7  16 
1  3  9  
 */