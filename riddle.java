class riddle
{
    void main()
    {
        int x=2,y=11,d,e;
        d=(int)Math.pow(x,y);
        e=(int)Math.pow(y,x);
        if(d-e==1927)
        System.out.println(d+"-"+e+"="+(d-e)+" True");
        else 
        System.out.println("False");
    }
}