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
                case 0:
                    System.out.println("Exiting the program. Goodbye!");
                    break;
                default:
                    System.out.println("Invalid choice. Please select a valid option.");
            }
        } while (choice != 0);

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

        // Validate the input for working days and attended days
        if (currentMonthDays < 1 || currentMonthAttended < 0 || currentMonthAttended > currentMonthDays) {
            System.out.println("Invalid input: attended days cannot exceed working days in the month.");
            return;
        }

        // For cumulative working days
        if (totalWorkingDays + currentMonthDays > 366) { // To prevent excessive working days
            System.out.println("Invalid input: total working days up to this month cannot exceed 366 days.");
            return;
        }

        System.out.println("Total working days up to this month: " + (totalWorkingDays + currentMonthDays));

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

        // Validate the input for working days and attended days
        if (currentMonthDays < 1 || currentMonthAttended < 0 || currentMonthAttended > currentMonthDays) {
            System.out.println("Invalid input: attended days cannot exceed working days in the month.");
            return;
        }

        // For cumulative working days
        if (previousWorkingDays + currentMonthDays > 366) { // To prevent excessive working days
            System.out.println("Invalid input: total working days up to this month cannot exceed 366 days.");
            return;
        }

        System.out.println("Total working days up to this month: " + (previousWorkingDays + currentMonthDays));

        double totalWorkingDays = previousWorkingDays + currentMonthDays;
        double totalAttended = previousAttendedDays + currentMonthAttended;
        double newPercentage = (totalAttended / totalWorkingDays) * 100;

        System.out.printf("New Attendance Percentage: %.2f%%\n", newPercentage);

        checkAttendanceRequirement(newPercentage, totalWorkingDays, totalAttended);
    }

    // Menu 3: Enter attendance for multiple months with starting month choice
    private static void enterAttendanceFromChosenMonth(Scanner scanner) {
        System.out.println("\nChoose the starting month:");
        System.out.println("a) January\nb) February\nc) March\nd) April\ne) May\nf) June");
        System.out.println("g) July\nh) August\ni) September\nj) October\nk) November\nl) December");
        System.out.print("Enter your choice (a-l): ");
        char monthChoice = scanner.next().charAt(0);

        String startingMonth = getMonthFromChoice(monthChoice);
        if (startingMonth == null) {
            System.out.println("Invalid choice. Returning to main menu.");
            return;
        }

        String month = startingMonth;
        int totalWorkingDays = 0;
        int totalAttendedDays = 0;
        int newYearIndicator = 0;

        System.out.println("\nEnter attendance data for months. Type 'stop' to end.");

        while (true) {
            System.out.printf("\nEnter total working days in %s%s: ", month, (newYearIndicator > 0 ? "*" : ""));
            String input = scanner.next();
            if (input.equalsIgnoreCase("stop")) break;

            int workingDays = Integer.parseInt(input);
            System.out.printf("Enter total days attended in %s%s: ", month, (newYearIndicator > 0 ? "*" : ""));
            int attendedDays = scanner.nextInt();

            // Validate the input for working days and attended days
            if (workingDays < 1 || attendedDays < 0 || attendedDays > workingDays) {
                System.out.println("Invalid input: attended days cannot exceed working days in the month.");
                continue;
            }

            totalWorkingDays += workingDays;
            totalAttendedDays += attendedDays;

            // Calculate cumulative attendance
            double cumulativePercentage = (double) totalAttendedDays / totalWorkingDays * 100;
            System.out.printf("Cumulative Attendance till %s: %.2f%%\n", month, cumulativePercentage);

            // Check attendance requirement
            checkAttendanceRequirement(cumulativePercentage, totalWorkingDays, totalAttendedDays);

            // Move to the next month
            month = getNextMonth(month);
            if (month.equals("January")) newYearIndicator++; // Mark new year
        }

        System.out.println("Attendance entry stopped.");
    }

    // Get month name based on user's choice
    private static String getMonthFromChoice(char choice) {
        switch (choice) {
            case 'a': return "January";
            case 'b': return "February";
            case 'c': return "March";
            case 'd': return "April";
            case 'e': return "May";
            case 'f': return "June";
            case 'g': return "July";
            case 'h': return "August";
            case 'i': return "September";
            case 'j': return "October";
            case 'k': return "November";
            case 'l': return "December";
            default: return null;
        }
    }

    // Get the next month name
    private static String getNextMonth(String currentMonth) {
        switch (currentMonth) {
            case "January": return "February";
            case "February": return "March";
            case "March": return "April";
            case "April": return "May";
            case "May": return "June";
            case "June": return "July";
            case "July": return "August";
            case "August": return "September";
            case "September": return "October";
            case "October": return "November";
            case "November": return "December";
            case "December": return "January";
            default: return "January"; // Fallback to January
        }
    }

    // Check if attendance is below 75% and calculate days needed to reach 76%
    private static void checkAttendanceRequirement(double percentage, double totalWorkingDays, double totalAttended) {
        if (percentage < 75.0) {
            double requiredDays = Math.ceil(0.76 * totalWorkingDays - totalAttended);
            System.out.printf("Your attendance is below 75%%. Attend at least %.0f more days to reach 76%%.\n", requiredDays);
        }
    }
}
