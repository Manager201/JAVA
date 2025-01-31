import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class AttendanceManager {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int choice;

        do {
            System.out.println("\n===== Attendance Manager Menu =====");
            System.out.println("1. Calculate Cumulative Attendance from Old Percentage [if days attended is unknown]");
            System.out.println("2. Calculate Cumulative Attendance from Days Attended");
            System.out.println("3. Enter Attendance for Multiple Months");
            System.out.println("4. What if I miss ___ days?");
            System.out.println("5. What if I go for ___ days?");
            System.out.println("6. Attendance Percentage Range (Prediction Table, Target Tracker)");
            System.out.println("7. Graphical Representations (Risk Zones, Progress Bar)");
            System.out.println("0. Exit");
            System.out.print("Enter your choice: ");
            choice = scanner.nextInt();

            switch (choice) {
                case 1:
                    calculateFromOldPercentage(scanner);
                    break;
                case 2:
                    calculateFromDaysAttended(scanner);
                    break;
                case 3:
                    enterAttendanceFromChosenMonth(scanner);
                    break;
                case 4:
                    simulateMissingDays(scanner);
                    break;
                case 5:
                    simulateAdditionalDays(scanner);
                    break;
                case 6:
                    displayPredictionTable(scanner);
                    break;
                case 7:
                    showGraphicalRepresentations(scanner);
                    break;
                case 0:
                    System.out.println("Exiting the program. Goodbye!");
                    break;
                default:
                    System.out.println("Invalid choice. Please select a valid option.");
            }
            System.out.println("Enter -1 to restart");
            if(scanner.nextInt()==-1)
            choice=-1;
        } while (choice == -1);

        scanner.close();
    }

    // Menu 1: Calculate cumulative attendance from old percentage
    private static void calculateFromOldPercentage(Scanner scanner) {
        System.out.print("\nEnter the old percentage: ");
        double oldPercentage = scanner.nextDouble();
        System.out.print("Enter the total working days till date (X): ");
        int totalWorkingDays = scanner.nextInt();
        System.out.print("Enter the total working days in future months: ");
        int currentMonthDays = scanner.nextInt();
        System.out.print("Enter the days attended: ");
        int currentMonthAttended = scanner.nextInt();

        double totalAttended = (oldPercentage / 100) * totalWorkingDays + currentMonthAttended;
        double newTotalWorkingDays = totalWorkingDays + currentMonthDays;
        double newPercentage = (totalAttended / newTotalWorkingDays) * 100;

        System.out.printf("New Attendance Percentage: %.2f%%\n", newPercentage);
        checkAttendanceRequirement(newPercentage, newTotalWorkingDays, totalAttended);
    }

    // Menu 2: Calculate cumulative attendance from days attended
    private static void calculateFromDaysAttended(Scanner scanner) {
        System.out.print("\nEnter total working days till now: ");
        int previousWorkingDays = scanner.nextInt();
        System.out.print("Enter days attended till now: ");
        int previousAttendedDays = scanner.nextInt();
        System.out.print("Enter total working days in future months: ");
        int currentMonthDays = scanner.nextInt();
        System.out.print("Enter days attended in those months: ");
        int currentMonthAttended = scanner.nextInt();

        double totalWorkingDays = previousWorkingDays + currentMonthDays;
        double totalAttended = previousAttendedDays + currentMonthAttended;
        double newPercentage = (totalAttended / totalWorkingDays) * 100;

        System.out.printf("New Attendance Percentage: %.2f%%\n", newPercentage);
        checkAttendanceRequirement(newPercentage, totalWorkingDays, totalAttended);
    }

    // Menu 3: Enter attendance for multiple months
    private static void enterAttendanceFromChosenMonth(Scanner scanner) {
        System.out.println("\nEnter total working days for multiple months. Type -1 to stop.");
        int totalWorkingDays = 0;
        int totalAttendedDays = 0;

        while (true) {
            System.out.print("Enter working days (or -1 to stop): ");
            int workingDays = scanner.nextInt();
            if (workingDays == -1)
                break;

            System.out.print("Enter attended days: ");
            int attendedDays = scanner.nextInt();

            totalWorkingDays += workingDays;
            totalAttendedDays += attendedDays;

            double percentage = (double) totalAttendedDays / totalWorkingDays * 100;
            System.out.printf("Cumulative Attendance: %.2f%%\n", percentage);
        }
    }

    // Feature 4: What if I miss ___ days?
    private static void simulateMissingDays(Scanner scanner) {
        System.out.print("\nEnter total working days so far: ");
        int totalDays = scanner.nextInt();
        System.out.print("Enter days attended so far: ");
        int attendedDays = scanner.nextInt();
        // Check if days attended are not more than total days
        if (attendedDays > totalDays) {
            System.out.println("Error: Days attended cannot be more than total working days.");
            return;
        }
        System.out.print("Enter the number of days you might miss: ");
        int daysMissed = scanner.nextInt();

        int newTotalDays = totalDays + daysMissed;
        double newPercentage = (double) attendedDays / newTotalDays * 100;

        System.out.printf("If you miss %d more days, your new attendance percentage will be: %.2f%%\n", daysMissed,
                newPercentage);
    }

    // Feature 5: What if I go for ___ days?
    private static void simulateAdditionalDays(Scanner scanner) {
        System.out.print("\nEnter total working days so far: ");
        int totalDays = scanner.nextInt();
        System.out.print("Enter days attended so far: ");
        int attendedDays = scanner.nextInt();
        // Check if days attended are not more than total days
        if (attendedDays > totalDays) {
            System.out.println("Error: Days attended cannot be more than total working days.");
            return;
        }
        System.out.print("Enter the number of additional days you plan to attend: ");
        int additionalDays = scanner.nextInt();

        int newTotalDays = totalDays + additionalDays;
        int newAttendedDays = attendedDays + additionalDays;
        double newPercentage = (double) newAttendedDays / newTotalDays * 100;

        System.out.printf("If you attend %d more days, your new attendance percentage will be: %.2f%%\n",
                additionalDays, newPercentage);
    }

    // Feature 6: Attendance Percentage Range and Attendance Trend
    private static void displayPredictionTable(Scanner scanner) {
        System.out.print("\nEnter total working days so far: ");
        int totalDays = scanner.nextInt();
        System.out.print("Enter days attended so far: ");
        int attendedDays = scanner.nextInt();
        // Check if days attended are not more than total days
        if (attendedDays > totalDays) {
            System.out.println("Error: Days attended cannot be more than total working days.");
            return;
        }
        System.out.println("\nDays Added | Attendance Percentage");
        System.out.println("-----------|----------------------");

        // Calculate the initial percentage
        double initialPercentage = (double) attendedDays / totalDays * 100;

        // Print the first entry with the initial percentage
        System.out.printf("%10d | %20.2f%%\n", 1, initialPercentage);

        // Store the days and percentages for the trend
        List<Integer> daysList = new ArrayList<>();
        List<Double> percentageList = new ArrayList<>();

        // Initialize the previous percentage
        double previousPercentage = initialPercentage;

        // Loop through up to 10 more ranges or until percentage exceeds 100%
        for (int i = 1; i <= 10 && previousPercentage < 100; i++) {
            int daysAdded = i * 6; // Add 6 days incrementally
            int newTotalDays = totalDays + daysAdded;
            int newAttendedDays = attendedDays + daysAdded;
            double newPercentage = (double) newAttendedDays / newTotalDays * 100;

            // Add only significant percentage changes to the table
            if (Math.abs(newPercentage - previousPercentage) >= 0.5) { // Avoid duplicates
                System.out.printf("%10d | %20.2f%%\n", daysAdded, newPercentage);
                previousPercentage = newPercentage;

                // Store values for trend visualization
                daysList.add(daysAdded);
                percentageList.add(newPercentage);

                // Stop early if attendance exceeds or equals 100%
                if (newPercentage >= 100) {
                    break;
                }
            }
        }

        // Print Attendance Trend with alternating characters for clarity
        System.out.println("\nAttendance Trend:");
        char[] graphSymbols = { '*', '#' }; // Alternate between these characters
        int lastPrintedPercentage = -1; // Track the last printed percentage to avoid duplicates
        for (int i = 0; i < daysList.size(); i++) {
            int day = daysList.get(i);
            int roundedPercentage = (int) Math.round(percentageList.get(i));

            // Skip printing if the rounded percentage hasn't changed
            if (roundedPercentage == lastPrintedPercentage) {
                continue;
            }

            lastPrintedPercentage = roundedPercentage; // Update the last printed percentage
            int barLength = (int) ((roundedPercentage / 100.0) * 50); // Scale graph proportionally
            char symbol = graphSymbols[i % 2]; // Alternate symbols for better differentiation

            // Print the trend
            System.out.printf("Day %2d: %s %3d%%\n", day, String.valueOf(symbol).repeat(barLength), roundedPercentage);
        }
        // Target Tracker
        double daysNeeded = Math.ceil((0.75 * totalDays - attendedDays) / 0.25);
        System.out.printf("\nDays needed to reach 75%%: %.0f days\n", daysNeeded);
    }

    // Feature 7: Graphical Representations
    private static void showGraphicalRepresentations(Scanner scanner) {
        System.out.print("\nEnter total working days so far: ");
        int totalDays = scanner.nextInt();
        System.out.print("Enter days attended so far: ");
        int attendedDays = scanner.nextInt();
        // Check if days attended are not more than total days
        if (attendedDays > totalDays) {
            System.out.println("Error: Days attended cannot be more than total working days.");
            return;
        }
        double percentage = (double) attendedDays / totalDays * 100;

        // Risk Zone Visualization with Color
        if (percentage >= 75) {
            // Safe in Green
            System.out.println("\033[32mRisk Zone: SAFE (Above 75%)\033[0m"); // Green color for Safe
        } else if (percentage >= 65) {
            // Warning in Yellow
            System.out.println("\033[33mRisk Zone: WARNING (65% to 75%)\033[0m"); // Yellow color for Warning
        } else {
            // Danger in Red
            System.out.println("\033[31mRisk Zone: DANGER (Below 65%)\033[0m"); // Red color for Danger
        }

        // Progress Bar
        double targetPercentage = 75.0; // Default target percentage for the cap
        double maxTarget = 100.0; // Maximum limit for progress bar (if above 75%)

        // Determine the target for progress (75 if below 75, else 100)
        double finalTarget = (percentage > 75) ? maxTarget : targetPercentage;

        // Progress calculation based on the final target (75 or 100)
        int progress = (int) (Math.min(percentage, finalTarget) / 2); // Scale progress
        int targetProgress = (int) (finalTarget / 2); // Scale target for 50 blocks

        // Determine the color for progress bar blocks based on percentage
        String progressColor;
        if (percentage < 65) {
            progressColor = "\033[31m"; // Red for below 65%
        } else if (percentage >= 65 && percentage <= 75) {
            progressColor = "\033[33m"; // Yellow for between 65% and 75%
        } else {
            progressColor = "\033[32m"; // Green for above 75%
        }

        // Print progress bar with the color and limit (either 75% or 100%)
        System.out.print("Progress Bar: [");
        for (int i = 0; i < 50; i++) {
            if (i < progress) {
                System.out.print(progressColor + "█");
            } else {
                System.out.print("\033[0m-"); // Default color for empty spaces
            }
        }

        // Reset to default color after progress bar
        System.out.print("\033[0m");

        // Print percentage and target (either 75.00% or 100.00%)
        System.out.printf("] %.2f%%/%.2f%%\n", percentage, finalTarget);
    }

    // Attendance Requirement Check
    private static void checkAttendanceRequirement(double percentage, double totalWorkingDays, double totalAttended) {
        if (percentage < 75) {
            double requiredDays = Math.ceil(0.75 * totalWorkingDays - totalAttended);
            System.out.printf("Your attendance is below 75%%. Attend at least %.0f more days to reach 75%%.\n",
                    requiredDays);
        }
    }
}
