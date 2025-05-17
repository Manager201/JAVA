/*
Write a program to declare a matrix a[ ][ ] of order r x c, where r is the number of rows and c is the number of columns. Input
positive integers into this matrix. Perform the following tasks:
a) Create another matrix b[ ][ ] to store mirror image of the inputted matrix.
b) Display the input and mirror image matrix.
Example: Input: r=3, c=4
4 16 12 7
8 2 14 5
6 1 3 9
Output:
Original Matrix
4 16 12 7
8 2 14 5
6 1 3 9
- - - - - - - - - - - - - - - - - - - - -
Mirror Image Matrix
6 1 3 9
8 2 14 5
4 16 12 7
 */
import java.util.*;
class mirror_img
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int r,c,i,j;
        System.out.print("Enter value of row for an array : ");
        r=sc.nextInt();
        System.out.print("Enter value of column for an array : ");
        c=sc.nextInt();
        int a[][]=new int[r][c];
        System.out.println("Enter elements of the array -");
        for(i=0;i<r;i++)
        {
            for(j=0;j<c;j++)
            {
                a[i][j]=sc.nextInt();
                if(a[i][j]<0)
                {
                    System.out.println("Retry with a positive number.");
                    System.exit(0);
                }
            }
        }
        original_matrix(a, r, c);
        mirror_matrix(a, r, c);
        
    }
    static void original_matrix(int a[][],int r,int c)
    {
        int i,j;
        System.out.println("Original Matrix: ");
        for(i=0;i<r;i++)
        {
            for(j=0;j<c;j++)
            {
                if(a[i][j]<10)
                System.out.print(" "+a[i][j]+" ");
                else
                System.out.print(a[i][j]+" ");
            }
            System.out.println();
        }
    }
    static void mirror_matrix(int a[][],int r,int c)
    {
        int k,i,j;
        int b[][]=new int[r][c];
        k=0;
        for(i=r-1;i>=0;i--)
        {
            for(j=0;j<c;j++)
            {
                b[k][j]=a[i][j];
            }
            k++;
        }
        System.out.println("- - - - - - - - - - - - - - - - - - - - -\nMirror Image Matrix");
        for(i=0;i<r;i++)
        {
            for(j=0;j<c;j++)
            {
                if(b[i][j]<10)
                System.out.print(" "+b[i][j]+" ");
                else
                System.out.print(b[i][j]+" ");
            }
            System.out.println();
        }
    }
}
/*
terminal output :
Original Matrix: 
 4 16 12  7 
 8  2 14  5 
 6  1  3  9 
- - - - - - - - - - - - - - - - - - - - -
Mirror Image Matrix
 6  1  3  9 
 8  2 14  5 
 4 16 12  7  
 */