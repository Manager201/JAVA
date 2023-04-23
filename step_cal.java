import java.util.*;

class step_cal {

    public static void main(String[] args) {
        int n, f; // f is for calculatinf fare of taxi
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter no. of kms travelled");
        // accepting number of kms travelled
        n = sc.nextInt();
        // if its upto 3 kms
        if (n <= 3)
            f = n * 50;
        // next 5kms
        else if (n > 3 && n <= 8) // next 12kms
            f = 3 * 50 + (n - 3) * 20;
        // next 20kms
        else if (n > 8 && n < 20)
            f = 3 * 50 + 5 * 20 + (n - 8) * 18;
        // above 20kms
        else
            f = 3 * 50 + 5 * 20 + 12 * 18 + (n - 20) * 15;
        System.out.println("Fare = " + f);
    }
}
