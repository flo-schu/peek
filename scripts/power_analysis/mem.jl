1+1
a=2


function myfunc(args)
    println("y = $args")
    return nothing
    # return args^2
end

myfunc(3)

a = [1,2,3,4,5]
arr = [1 2; 3 4]
println(arr)

# hübsches feature :)
print(a)

f(x,y) = x^2 + y^3

for i = a
    global x = myfunc(i)
end

gloai=0
while i < 10
    print(i)
    i += 1
end

print(x)

a = 1:10
