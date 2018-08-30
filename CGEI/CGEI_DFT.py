
from pylab import *
from PIL import Image,ImageFilter,ImageOps
import random
import os

M=64
S=1
set_printoptions(suppress=True,precision=3)
path='.\\cgei\\'
vlist=list()
# list number of files
lst=os.listdir(path)
L=len(lst)
for i in range(0,L):
	name=path+str(lst[i])
	print(name)
	img=Image.open(name)
	(W,H)=img.size
	X=matrix(reshape(img.getdata(),(H,W)))
	# calculate sum of elements
	sum=0.0
	for n in range(0,W):
		for m in range(0,H):
			sum=sum+X[m,n]
	# calculate center point
	xc=0.0
	yc=0.0
	for n in range(0,W):
		for m in range(0,H):
			p=X[m,n]/float(sum)
			xc=xc+p*n
			yc=yc+p*m
	xc=int(xc)
	yc=int(yc)
	X[yc,xc]=25
	# scan angles 0..359
	vec=zeros(360,float)
	for n in range(0,360):
		a=(2.0*math.acos(-1.0)/360.0)*n
		c=math.cos(a)
		s=math.sin(a)
		xi=xc
		yi=yc
		r=1.0
		while (int(xi)>=0 and int(xi)<W) and (int(yi)>=0 and int(yi)<H):
			v=X[int(yi),int(xi)]/float(sum)
			vec[n]=vec[n]+v
			xi=xi+r*c
			yi=yi+r*s
	#plot(arange(0,360),vec,'b')
	#show()
	#vec=abs(fft(vec))
	vec=fft(vec)
	vec/=vec[0]
	vec=vec[S:S+M]
	vlist.append([lst[i],vec])
md=0
CM=matrix(zeros((L,L),float))
for i in range(0,L):
	vec1=(vlist[i])[1]
	for j in range(0,L):
		vec2=(vlist[j])[1]
		d=norm(vec1-vec2)
		CM[i,j]=d
		if (d>md):
			md=d
for i in range(0,L):
	for j in range(0,L):
		CM[i,j]=1.0-CM[i,j]/md
# test of classification 1-NN
nc=0
for i in range(0,L):
	if (i%4==0):
		mini=0
		minv=1.0
		for j in range(0,L):
			if (i!=j):
				if ((1.0-CM[i,j])<minv):
					minv=(1.0-CM[i,j])
					mini=j
		print(str(i)+' -> '+str(mini)),
		if (mini>=i+1 and mini<=i+3):
			nc+=1
			print('*'),
		print
print('class. accuracy='+str(100.0*nc/(L/4.0))+' %')
imshow(CM)
show()