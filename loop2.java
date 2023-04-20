class loop2
{
    void main(int n)
    {
        
        double i,d=2,p=0;
        for(i=1;i<=20;i++)
        {
            p=p+n/d;
            d=d+3;
        }
        System.out.println(p);
    }
}