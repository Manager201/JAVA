import java.util.Scanner;

public class TimeAddition {
    public static void main(String[] args) {
        // Store times as a string array
        String[] times = {"3:34:28", "3:33:52", "3:29:16", "3:36:32", "3:40:00", 
                          "3:10:28", "3:23:16", "3:24:32", "1:41:28"};
        
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter 1 to display a cumulative sum or 2 to enter a range:");
        int choice = sc.nextInt();
        
        if (choice == 1) {
            System.out.println("Enter a number (1 to 9):");
            int num = sc.nextInt();
            
            if (num < 1 || num > 9) {
                System.out.println("Invalid input! Enter a number between 1 and 9.");
            } else {
                // Cumulative sum from index 0 to num-1
                String result = addTimes(times, 0, num - 1);
                System.out.println("Total time: " + result);
            }
            
        } else if (choice == 2) {
            System.out.println("Enter the start index (1 to 9):");
            int start = sc.nextInt();
            System.out.println("Enter the end index (1 to 9):");
            int end = sc.nextInt();
            
            if (start < 1 || start > 9 || end < 1 || end > 9 || start > end) {
                System.out.println("Invalid range! Enter numbers between 1 and 9 where start <= end.");
            } else {
                // Sum only between the given range
                String result = addTimes(times, start - 1, end - 1);
                System.out.println("Total time: " + result);
            }
        } else {
            System.out.println("Invalid choice! Enter 1 or 2.");
        }
        
        sc.close();
    }
    
    public static String addTimes(String[] times, int start, int end) {
        int totalHours = 0, totalMinutes = 0, totalSeconds = 0;
        
        for (int i = start; i <= end; i++) {
            String[] parts = times[i].split(":");
            totalHours += Integer.parseInt(parts[0]);
            totalMinutes += Integer.parseInt(parts[1]);
            totalSeconds += Integer.parseInt(parts[2]);
        }

        // Adjust overflow
        totalMinutes += totalSeconds / 60;
        totalSeconds %= 60;
        totalHours += totalMinutes / 60;
        totalMinutes %= 60;

        // Format the output as HH:MM:SS with leading zeros where needed
        return String.format("%d:%02d:%02d", totalHours, totalMinutes, totalSeconds);
    }
}
