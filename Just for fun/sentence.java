import java.util.*;

class Progr {
    int f1, len;
    String str, str1;

    public static void main(String args[]) {
        Progr obj = new Progr();
        obj.accept();
        int k=obj.validifier();

        if (k==-2) {
            System.out.println("INVALID INPUT");
        } else {
            if (obj.f1 == obj.len - 1) {
                System.out.println("INVALID INPUT");
                return;
            }
            obj.str1 = obj.str.substring(obj.f1 + 1).trim();  
            obj.len = obj.str1.length();

            if (obj.str1.length() > 1 &&
                (obj.str1.endsWith("?") || obj.str1.endsWith(".") || obj.str1.endsWith("!"))) 
                    obj.display();
            else 
                System.out.println("INVALID INPUT");
            
        }
        obj.frequency();
    }

    void accept() {
        Scanner sc = new Scanner(System.in);
        System.out.println("Enter a sentence:");
        str = sc.nextLine().trim();  
        len = str.length();
        str=str.toUpperCase();
    }

    int validifier() {
        f1 = str.indexOf("."); 
        int f2 = str.indexOf("?");
        int f3 = str.indexOf("!");
    
        if (f1 == -1 || (f2 != -1 && f2 < f1)) // i dont know exact logic here, helped by chatgpt
            f1 = f2;
        if (f1 == -1 || (f3 != -1 && f3 < f1)) 
            f1 = f3;
    
        if (f1 == -1)
            return -2;
        else
            return f1;
    }
    
    
    
    
    
    void frequency() {
        String w = "", str2 = str + " ";
        int c, cc = 0;
        str2 = str2.replace("?", "").replace(".", "").replace("!", ""); //helped by chatgpt
    
        int len = str2.length();  
        for (int i = 0; i < len; i++) {
            char ch = str2.charAt(i);
            if (ch != ' ') {
                w = w + ch;  
            } else {
                c = 1;
                int i1 = str2.indexOf(w, i + w.length());  
                while (i1 != -1) {
                    c++;
                    i1 = str2.indexOf(w, i1 + w.length());
                }
                if (c > 1) {
                    if (cc == 0) System.out.println("COMMON WORDS\tFREQUENCY");
                    System.out.println(w + "\t\t" + c);
                    cc++;
                }
                w = "";  
            }
        }
    
        if (cc == 0)
            System.out.println("NO COMMON WORDS");
    }
    
    
    

    void display() {
        System.out.println("\n"+str.substring(0, f1+1).trim()); //trim function helped by chatgpt
        System.out.println(str.substring(f1 + 1).trim());  
    }
}
