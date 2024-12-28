import java.io.*;
import java.util.*;
class student
{
    public static void main(String[] args) throws Exception {
        Scanner sc=new Scanner(System.in);
        FileWriter fw=new FileWriter("Student.text");
        BufferedWriter bw=new BufferedWriter(fw);
        PrintWriter pw=new PrintWriter(bw);
        for(int i=1;i<=2;i++)
        {
            System.out.println("Enter a roll no.");
            int r=sc.nextInt();
            System.out.println("Enter name");
            String n=sc.next();
            System.out.println("Enter per%");
            double p=sc.nextDouble();
            pw.println(r+"\t"+n+"\t"+p);
        }
        pw.close();
    }
}