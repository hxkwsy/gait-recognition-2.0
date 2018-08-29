
from pylab import *;
from PIL import Image,ImageFilter,ImageOps;
import random;
import os;

#######################################################################################################	
# Generates matrix of DCT-II
#
def dctII(n):

	u=zeros((n,n),float64);
	v=1.0/sqrt(2.0);
	for i in range(0,n):
		for j in range(0,n):
			u[i][j]=v*math.sqrt(2.0/n)*cos(pi/n*i*(j+0.5));
		v=1.0;
	return matrix(u);	

M=10; #16
S=0;
set_printoptions(suppress=True,precision=3);
path='.\\cgei\\';
vlist=list();
# list number of files
lst=os.listdir(path);
L=len(lst);
for i in range(0,L):
	name=path+str(lst[i]);
	print(name);
	img=Image.open(name);
	(W,H)=img.size;
	X=matrix(reshape(img.getdata(),(H,W)));
	U1=matrix(dctII(H));
	U2=matrix(dctII(W));
	# horizontal/vertical histograms in DCT domain
	# sh=zeros(W,float);
	# sv=zeros(H,float);
	# for n in range(0,W):
		# sh[n]=sum(X[:,n]);
	# sh/=float(H);
	# sh=(array((U2*matrix(sh).T).T)[0])[0:M];
	# for m in range(0,H):
		# sv[m]=sum(X[m,:]);
	# sv/=float(W);
	# sv=(array((U1*matrix(sv).T).T)[0])[0:M];
	# vec=zeros(2*M,float);
	# vec[0:M]=sh;
	# vec[M:2*M]=sv;
	# DCT domain coefficients
	Y=U1*X*U2.T;
	vec=reshape(Y[S:S+M,S:S+M],M*M);
	vlist.append([lst[i],vec]);
md=0;
CM=matrix(zeros((L,L),float));
for i in range(0,L):
	vec1=(vlist[i])[1];
	for j in range(0,L):
		vec2=(vlist[j])[1];
		d=norm(vec1-vec2);
		CM[i,j]=d;
		if (d>md):
			md=d;
for i in range(0,L):
	for j in range(0,L):
		CM[i,j]=1.0-CM[i,j]/md;
# test of classification 1-NN
nc=0;
for i in range(0,L):
	if (i%4==0):
		mini=0;
		minv=1.0;
		for j in range(0,L):
			if (i!=j):
				if ((1.0-CM[i,j])<minv):
					minv=(1.0-CM[i,j]);
					mini=j;
		if (mini>=i+1 and mini<=i+3):
			nc+=1;
		print(str(i)+' -> '+str(mini));
print('class. accuracy='+str(100.0*nc/(L/4.0))+' %');
imshow(CM);
show();