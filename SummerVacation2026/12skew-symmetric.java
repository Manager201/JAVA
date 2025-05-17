/*
Write a program to declare a matrix a[ ][ ] of order r x c, where r is the number of rows and c is the number of columns. Input
positive integers into this matrix. Perform the following tasks:
a) Display the original matrix
b) Check if the given matrix is Skew Symmetric or not. A square matrix is said to be Skew Symmetric if the element of
the ith row and jth column is equal to the negative value of the jth row and ith column.
c) Find the sum of the elements of left diagonal, sum of the elements of right diagonal and sum of border elements of
the matrix and display them.
Example: 1) Input: r=3, c=4
Output: Not a square matrix
2) Input: r=4, c=4
0 -1 -5 -3
1  0 6  9
5 -6 0 -2
3 -9 2  0
Output:
Original Matrix
0 -1 -5 -3
1  0  6  9
5 -6  0 -2
3 -9  2  0
The Given Matrix is Skew Symmetric.
The sum of the left diagonal = 0
The sum of the right diagonal = 0
The sum of the border elements = 0

 */
import java.util.*;
class skew_matrix
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int r,c,i,j;
        System.out.print("Enter value of row for an array : ");
        r=sc.nextInt();
        System.out.print("Enter value of column for an array : ");
        c=sc.nextInt();
        if(r!=c)
        {
            System.out.println("Not a square matrix");
            System.exit(0);
        }
        int a[][]=new int[r][c];
        System.out.println("Enter elements of the array -");
        for(j=0;j<r;j++)
        {
            for(i=0;i<c;i++)
            {
                a[j][i]=sc.nextInt();
            }
        }
        System.out.println("Original Matrix: ");
        for(j=0;j<r;j++)
        {
            for(i=0;i<c;i++)
            {
                if(a[j][i]>=0)
                System.out.print(" "+a[j][i]+" ");
                else
                System.out.print(a[j][i]+" ");
            }
            System.out.println();
        }
        if(skew_symmetic(a, r, c))
        System.out.println("The Given Matrix is Skew Symmetric.");
        else
        System.out.println("The Given Matrix is not a Skew Symmetric.");
        calculate(a, r, c);
    }
    static boolean skew_symmetic(int a[][],int r,int c)
    {
        int j,i;
        for(j=0;j<r;j++)
        {
            i=j;
            while(i<c)
            {
                if(a[j][i]!=-(a[i][j]))
                    return false;
                i++;
            }
        }
        return true;
    }
    static void calculate(int a[][],int r,int c)
    {
        int i,j,ld=0,rd=0,be=0;
        //Sum of left diagonal 
        for(j=0;j<r;j++)
        {
            for(i=0;i<c;i++)
            {
                if(i==j)
                ld=ld+a[j][i];
            }
        }
        System.out.println("The sum of the left diagonal = "+ld);
        //Sum of right diagonal 
        for(j=0;j<r;j++)
        {
            for(i=0;i<c;i++)
            {
                if(i+j==r-1)
                rd=rd+a[j][i];
            }
        }
        System.out.println("The sum of the right diagonal = "+rd);
        //Sum of border elements
        for(j=0;j<r;j++)
        {
            for(i=0;i<c;i++)
            {
                if(j==0||j==3||i==0||i==3)
                be=be+a[j][i];
            }
        }
        System.out.println("The sum of the border elements = "+be);
    }
}
/*
terminal output :
Enter value of row for an array : 3
Enter value of column for an array : 3
Enter elements of the array -
0
2
-3
-2
0
5
3
-5
0
Original Matrix: 
 0  2 -3 
-2  0  5 
 3 -5  0 
The Given Matrix is Skew Symmetric.
The sum of the left diagonal = 0
The sum of the right diagonal = 0
The sum of the border elements = 0
 */