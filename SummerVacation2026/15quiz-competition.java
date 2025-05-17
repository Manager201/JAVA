/*
The result of a quiz competition is to be prepared as follows:
The quiz has five questions with four multiple choices (A, B, C, D) with each question carrying 1 mark for the correct answer.
Design a program to input the number of participants n such that n must be greater than 3 and less than 11. Create a double
dimensional array of size (nx5) to store the answers of each participant row-wise. Calculate the marks for each participant by
matching the correct answer stored in a single dimensional array of size 5. Display the scores for each participant and also
the participant having the highest score.
Example:1) Input: n = 4
Participant 1 A C C B D
Participant 2 B C A A C
Participant 3 B C B A A
Participant 4 C C D D B
Key : A C D B B
Output: Scores:
Participant 1 = 3
Participant 2 = 1
Participant 3 = 1
Participant 4= 3
Highest score: Participant 1
Participant 4
2) Input: n = 13
Output: Input size is out of range.
 */
import java.util.*;
class quiz_competition
{
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        System.out.print("Enter the number of participants: ");
        int n,i,j,count=0,l;
        n=sc.nextInt();
        sc.nextLine();
        if(n<3||n>11)
        {
            System.out.println("Input size is out of range.");
            System.exit(0);
        }
        char arr[][]=new char[n][5];
        char key[]={'A', 'C', 'D', 'B', 'B'};
        int score[]=new int[n];
        for(i = 0; i < n; i++) 
        {
            System.out.print("Participant " + (i + 1) + "  ");
            for(j = 0; j < 5; j++) 
                    arr[i][j] = sc.next().charAt(0);
        }
        System.out.println("Scores:");
        for(i=0;i<n;i++)
        {
            for(j=0;j<n+1;j++)
            {
                if(key[j]==arr[i][j])
                count++;
            }
            score[i]=count;
            System.out.println("Participant "+(i+1)+" = "+count);
            count=0;
        }
        System.out.println("Highest score:");
        l=score[0];
        for(i=0;i<n;i++)
        {
            if(l<=score[i])
            System.out.println("Participant "+(i+1));
        }
    }
}
/*
Terminal output :
Enter the number of participants: 4
Participant 1: A C C B D
Participant 2: B C A A C
Participant 3: B C B A A
Participant 4: C C D D B
Scores:
Participant 1 = 3
Participant 2 = 1
Participant 3 = 1
Participant 4 = 3
Highest score:
Participant 1
Participant 4
 */