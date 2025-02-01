import java.util.*;

class Annualper {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int choice;

        do {
            System.out.println("\n===== Annual Percentage Menu =====");
            System.out.println("1. Subject-wise annual percentage");
            System.out.println("2. For single subject(Prediction Table)");
            System.out.println("EXIT: 0");
            System.out.println("Enter your choice:");
            choice = sc.nextInt();
            switch (choice) {
                case 1:
                    boolean validInput;
                    String[] subjects = {"Physics:", "Chemistry:", "Bio/Math:", "Comp/Hindi:", "Eng. Lit:", "Eng. Lang:"};
                    double[][] marks = new double[subjects.length][4]; // 3 for input marks and 1 for calculated passing marks
        
                    do {
                        validInput = true;
                        for (int i = 0; i < subjects.length; i++) {
                            System.out.println("\nEnter marks for " + subjects[i]);
                            System.out.print("Half Yearly (0-100): ");
                            marks[i][0] = sc.nextDouble();
                            System.out.print("UT 1 (0-25): ");
                            marks[i][1] = sc.nextDouble();
                            System.out.print("UT 2 (0-25): ");
                            marks[i][2] = sc.nextDouble();

                            if (marks[i][0] < 0 || marks[i][0] > 100 || marks[i][1] < 0 || marks[i][1] > 25 || marks[i][2] < 0 || marks[i][2] > 25) {
                                System.out.println("Invalid input. Please enter the marks within the specified ranges.");
                                validInput = false;
                                break;
                            }

                            double hf = marks[i][0] * 0.3;
                            double ut1 = marks[i][1] * 0.1;
                            double ut2 = marks[i][2] * 0.1;
                            marks[i][3] = (33.33 - (hf + ut1 + ut2)) / 0.5;
                        }
                    } while (!validInput);

                    System.out.println("\n===== Annual Percentage Report =====");
                    System.out.println("Subject\t\tHalf Yearly\tUT 1\t\tUT 2\t\tPassing Marks");
                    for (int i = 0; i < subjects.length; i++) {
                        System.out.printf("%-12s\t%.2f\t\t%.2f\t\t%.2f\t\t%.2f\n", subjects[i], marks[i][0], marks[i][1], marks[i][2], marks[i][3]);
                    }
                    break;
                case 2:
                    // Case for single subject prediction table
                    System.out.println("\nEnter marks for the subject:");
                    System.out.print("Half Yearly: ");
                    double hf = sc.nextDouble();
                    System.out.print("Unit Test 1: ");
                    double ut1 = sc.nextDouble();
                    System.out.print("Unit Test 2: ");
                    double ut2 = sc.nextDouble();

                    double hfWeighted = hf * 0.3;
                    double ut1Weighted = ut1 * 0.1;
                    double ut2Weighted = ut2 * 0.1;
                    double passingMarks = (33.33 - (hfWeighted + ut1Weighted + ut2Weighted)) / 0.5;

                    System.out.println("Passing Marks: " + String.format("%.2f", passingMarks));

                    // Displaying the prediction table
                    System.out.println("\nPrediction Table:");
                    System.out.println("Percentage Values | Marks Needed");
                    System.out.println("------------------|-------------");
                    
                    for (int percentage = 50; percentage <= 100; percentage += 10) {
                        double marksNeeded = (percentage - (hfWeighted + ut1Weighted + ut2Weighted)) / 0.5;
                        if (marksNeeded > 100) {
                            System.out.printf("%16d%% | Out of Bounds\n", percentage);
                            break;
                        } else {
                            System.out.printf("%16d%% | %13.2f\n", percentage, marksNeeded);
                        }
                    }
                    break;
                case 0:
                    System.out.println("Exiting...");
                    break;
                default:
                    System.out.println("Invalid choice. Please try again.");
            }
            System.out.println("Enter -1 to restart or 0 to exit:");
            choice = sc.nextInt();
        } while (choice == -1);
    }
}
