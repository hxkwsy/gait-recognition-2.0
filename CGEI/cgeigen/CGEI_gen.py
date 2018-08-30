
from pylab import *
import random
import sys
import os
import cv2

set_printoptions(suppress=True,precision=3)
N=352
M=240
L=75
T=10
F=10
args=copy(sys.argv)
path=str(args[1])
ftxt=str(args[2])
W=int(args[3])
H=int(args[4])
# list number of files
lst=os.listdir(path)
slst=list()
for i in range(1,len(lst)+1):
	print('# '+str(i))
	txt='{0:03d}'.format(i)
	name=path+'\\'+ftxt+'-'+txt+'.png'
	img=cv2.imread(name,0)
	X=matrix(reshape(img,(M,N)))
	#
	hh=zeros(N,float)
	hv=zeros(M,float)
	for j in range(0,N):
		hh[j]=sum(X[:,j])/255.0
	for j in range(0,M):
		hv[j]=sum(X[j,:])/255.0
	# find x limits
	#print(hh)
	minx=0
	maxx=0
	for j in range(0,N):
		if (hh[j]>T):
			minx=j-F
			break
	for j in range(0,N):
		if (hh[N-j-1]>T):
			maxx=N-j-1+F
			break
	# find y limits
	miny=0
	maxy=0
	for j in range(0,M):
		if (hv[j]>T):
			miny=j-F
			break
	for j in range(0,M):
		if (hv[M-j-1]>T):
			maxy=M-j-1+F
			break
	if (minx<0):
		minx=0
	if (maxx>N-1):
		maxx=N-1
	if (miny<0):
		miny=0
	if (miny>M-1):
		miny=M-1
	print('minx='+str(minx)+' maxx='+str(maxx))
	print('miny='+str(miny)+' maxy='+str(maxy))
	# central point
	xc=0.0
	yc=0.0
	num=0
	for n in range(minx,maxx+1):
		for m in range(miny,maxy+1):
			if (X[m,n]>0):
				xc=xc+n
				yc=yc+m
				num=num+1
	xc=int(xc/float(num))
	yc=int(yc/float(num))
	Y=copy(X[miny:maxy+1,minx:maxx+1])
	slst.append([Y,[xc-minx,yc-miny]])
	print('xc='+str(xc-minx)+' yc='+str(yc-miny))
# find width and height
width=0
height=0
lx=0
rx=0
ty=0
by=0
for i in range(0,len(slst)):
	t=slst[i]
	X=copy(t[0])
	[h,w]=shape(X)
	[xc,yc]=t[1]
	if (xc>lx):
		lx=xc
	if (w-xc>rx):
		rx=w-xc
	if (yc>ty):
		ty=yc
	if (h-yc>by):
		by=h-yc
	if (w>width):
		width=w
	if (h>height):
		height=h
width=lx+rx
height=ty+by
print(' width='+str(width))
print('height='+str(height))
# create GEI image
#width=106
#height=184
xxc=lx+(width-(rx+lx))/2
yyc=ty+(height-(by+ty))/2
print('xxc='+str(xxc))
print('yyc='+str(yyc))
GEI=zeros((height,width),float)
for i in range(0,len(slst)):
	t=slst[i]
	X=copy(t[0])
	X=cv2.Canny(X,100,200)
	[h,w]=shape(X)
	[xc,yc]=t[1]
	for n in range(0,w):
		for m in range(0,h):
			i1=(xxc-xc)+n
			i2=(yyc-yc)+m
			GEI[i2,i1]=GEI[i2,i1]+X[m,n]
mval=0
for i in range(0,width):
	for j in range(0,height):
		if (GEI[j,i]>mval):
			mval=GEI[j,i]
X=zeros((height,width),uint8)
for i in range(0,width):
	for j in range(0,height):
		b=int(255.0*GEI[j,i]/mval)
		if (b<0):
			b=0
		if (b>255):
			b=255
		X[j,i]=uint8(b)
img=cv2.resize(X,(W,H))
name='cgei_'+ftxt+'.bmp'
cv2.imwrite(name,img)
# for n in range(xxc-2,xxc+3):
	# GEI[yyc,n]=128
# for m in range(yyc-2,yyc+3):
	# GEI[m,xxc]=128
# imshow(GEI,cmap='gray')
# # show()
	
