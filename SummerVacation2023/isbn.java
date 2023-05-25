class isbn
{
    void main(int n)
    {
        int r=1,d,x,s=0,i,c=0;
        while(n!=0)
        {
        d=n%10;
        r=r*10+d;
        c++;
        n=n/10;
    }
    if(c!=10)
    System.out.println("Illegal ISBN");
    for(i=1;i<=10;i++)
    {
        x=r%10;
        s=s+i*x;
        x=x/10;
    }
    if(s%11==0)
    System.out.println("Legal ISBN");
    else 
    System.out.println("Illegal ISBN");
    }
}