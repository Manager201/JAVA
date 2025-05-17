/*
Given a square matrix a [ ] [ ] of order n. Input the value for n and the positive integers in the matrix and perform the following
operations:
1. Display the original matrix.
2. Print the row and column position of the smallest element of the matrix.
3. Sort the elements of the rows in the descending order and display the new matrix.
Example- Input:
n = 3
a [ ] [ ]
3 1 7
4 6 9
8 2 5
Output:
Original Matrix is:
3 1 7
4 6 9
8 2 5
The smallest element 1 is in row 1 and column 2
Sorted Matrix is:
7 3 1
9 6 4
8 5 2
 */
import java.util.*;
class smallest_elem
{
    static int k,i,j,n,row=0,column=0,q,r,s,si,t;
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter order 'n' for a square matrix: ");
        n=sc.nextInt();
        System.out.println("Enter elements of the matrix-");
        int a[][]=new int[n][n];
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
        smallest_element(a, n);
        sorted_matrix(a, n);

    }
    //original matirx : task 1
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
    //smallest element : task 2
    static void smallest_element(int a[][],int n)
    {
        k=a[0][0];
        for(i=0;i<n;i++)
        {
            for(j=0;j<n;j++)
            {
                if(a[i][j]<k)
                {
                    k=a[i][j];
                    row=i;
                    column=j;
                }
            }
        }
        System.out.println("The smallest element "+k+" is in row "+(row+1)+" and column "+(column+1));
    }
    //sorted matrix : task 3
    static void sorted_matrix(int a[][], int n)
    {
        int z[]=new int[n];
        System.out.println("Sorted Matrix is:");
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
                    if(z[r]>s)
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
            if(z[q]<10)
                System.out.print(z[q]+"  ");
                else
                System.out.print(z[q]+" ");
            System.out.println();
        }
    }
}
/*
terminal output :
Enter order 'n' for a square matrix: 4
Enter elements of the matrix-
8
45
1
-5
Retry with a positive number.

Enter order 'n' for a square matrix: 3
Enter elements of the matrix-
8
12
4
5
9
14
7
6
9 
8  12 4  
5  9  14 
7  6  9  
The smallest element 4 is in row 1 and column 3
Sorted Matrix is:
12 8  4  
14 9  5  
9  7  6  
 */