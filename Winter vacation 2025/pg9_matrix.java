/* Program 9:
Write a program to declare a square matrix a [ ][ ] of order n x n, allow the user to input positive integers
into this matrix. Perform the following tasks:
a) Display the original matrix.
b) Sort the elements of each row in ascending order using any standard sorting technique and
rearrange them in the matrix. Display the rearranged matrix.
c) Display only the diagonal elements of the rearranged matrix with their sum.

Input: n = 4
8       5       3       17
6       12      9       8
19      5       16      3
4       6       14      9
Output = Original Matrix
8       5       3       17
6       12      9       8
19      5       16      3
4       6       14      9
Rearranged Matrix
3       5       8       17
6       8       9       12
3       5       16      19
4       6       9       14
Diagonal Elements
3                       17
        8       9
        5       16
4                       14
The sum of the diagonal elements = 76
 */
import java.util.*;
class pg9_matrix {
    static void sort(int a[], int n) {  
        int i, j, s, si, t;
        for (i = 0; i < n - 1; i++) {
            s = a[i];
            si = i;
            for (j = i + 1; j < n; j++) 
                if (a[j] < s) {
                    s = a[j];
                    si = j;
                }
            t = a[i];
            a[i] = a[si];
            a[si] = t;
        }
    }
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter order of matrix:");
        int n = sc.nextInt(), i, j, k,s=0;
        int a[][] = new int[n][n];
        System.out.println("Enter numbers in the array");
        for (i = 0; i < n; i++)
            for (j = 0; j < n; j++) {
                a[i][j] = sc.nextInt();
                if (a[i][j] < 0) {
                    System.out.println("You entered a -ve integer");
                    System.exit(0);
                }
            }

        System.out.println("Original Matrix");
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++)
                System.out.print(a[i][j] + "\t");
            System.out.println();
        }

        int m[] = new int[n];
        System.out.println("Rearranged Matrix");
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) 
                m[j] = a[i][j];
            sort(m, n);
            for (j = 0; j < n; j++)
                a[i][j] = m[j];
        }

        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++)
                System.out.print(a[i][j] + "\t");
            System.out.println();
        }

        System.out.println("Diagonal Elements");
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) 
                if (i + j == n - 1 || i == j) 
                    System.out.print(a[i][j] + "\t");
                else 
                    System.out.print("\t");
            System.out.println();
        }
        System.out.print("The sum of the diagonal elements = ");
        for (i = 0; i < n; i++) {
            for (j = 0; j < n; j++) 
            if (i + j == n - 1 || i == j) 
                s=s+a[i][j];
        }
        System.out.println(s);
    }
}
