with open("./Data/empcenterlist.txt") as f:
    centers = f.readlines()
centers =  [center for center in centers]
centers1 = [centers[i] for i in xrange(len(centers)) if i%3 == 0]
centers2 = [centers[i] for i in xrange(len(centers)) if i%3 == 1]
centers3 = [centers[i] for i in xrange(len(centers)) if i%3 == 2]
with open("./Data/empcenterlist1.txt", "w") as f:
    [f.write(x) for x in centers1]
with open("./Data/empcenterlist2.txt", "w") as f:
    [f.write(x) for x in centers2]
with open("./Data/empcenterlist3.txt", "w") as f:
    [f.write(x) for x in centers3]
