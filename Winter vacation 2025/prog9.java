import java.util.*;
class prog9 {
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
        System.out.println("Enter order of matrix");
        int n = sc.nextInt(), i, j, k;
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
    }
}
