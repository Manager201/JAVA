class loop1{
    public static void main(int n)
    {
        int i,a=0, b=1 ,c;
        for(i=1 ; i<=n ; i++){
            c=a+b;
            System.out.println(a+"");
            a=b;
            b=c;
        }
    }
}