class riddle2
{
    void main()
    {
        int x=3,y=7,d,e;
        d=(int)Math.pow(x,y);
        e=(int)Math.pow(y,x);
        if(d-e==1844)
        System.out.println(d+"-"+e+"="+(d-e)+" True");
        else 
        System.out.println("False");
    }
}