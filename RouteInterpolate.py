import os
import sys

def ReadTxt(txt):
	f=open(txt)
	content=f.readlines()
	f.close()
	return map(lambda line:line.strip('\n'),content)

def WriteTxt(content,path):
	f=open(path,'w')
	f.writelines(content)
	f.close()

def Interpret(line):
	# id,time(date hh:mm:ss),x,y
	params=line.split(',')
	tid=params[0]
	cal=params[1]

	date=cal.split(' ')[0]
	ymd=date.split('-')
	yy=int(ymd[0])
	mo=int(ymd[1])
	dd=int(ymd[2])

	time=cal.split(' ')[1]
	hms=time.split(':')
	hh=int(hms[0])
	mm=int(hms[1])
	ss=int(hms[2])

	x=float(params[2])
	y=float(params[3])

	record={'date':date,'time':time,\
			'dt':{'yy':yy,'mo':mo,'dd':dd,'hh':hh,'mm':mm,'ss':ss},\
			'x':x,'y':y}
	return record

def calcTime(start,end):
	# return seconds
	# time={'yy':yy,'mo':mo,'dd':dd,'hh':hh,'mm':mm,'ss':ss}
	import datetime
	d1=datetime.datetime(start['yy'], start['mo'], start['dd'],start['hh'],start['mm'],start['ss'])
	d2=datetime.datetime(end['yy'], end['mo'], end['dd'],end['hh'],end['mm'],end['ss'])
	# datetime.timedelta(seconds=1)
	return (d2-d1).seconds

def addTime(time,sec):
	import datetime
	# time={'yy':yy,'mo':mo,'dd':dd,'hh':hh,'mm':mm,'ss':ss}
	d1=datetime.datetime(time['yy'], time['mo'], time['dd'],time['hh'],time['mm'],time['ss'])
	d2=d1+datetime.timedelta(seconds=sec)
	return d2.strftime("%Y-%m-%d %H:%M:%S")

def InterpolatePoints(txt,save_dir):
	print txt
	basename,filename=os.path.split(txt)
	# print  basename,filename
	fname=filename.split('.')[0]
	result_path=os.path.join(save_dir,fname+'_1s.txt')

	content=ReadTxt(txt)

	last=Interpret(content[0])
	newline=[content[0]+'\n']

	for line in content[1:]:
		record=Interpret(line)

		if(last['date'] == record['date'] and \
				last['time']==record['time']):
			continue

		seconds=calcTime(last['dt'],record['dt'])
		ix=record['x']-last['x']
		iy=record['y']-last['y']
		for i in range(1,seconds):
			ntime=addTime(last['dt'],i)
			nx=i*ix/seconds+last['x']
			ny=i*iy/seconds+last['y']
			newline.append(','.join([fname,ntime,str(nx),str(ny)])+'\n')

		newline.append(line+'\n')
		last=record
	# return newline
	WriteTxt(newline,result_path)


if __name__=='__main__':
	# original data
	base='F:/data/taxi/'

	resdir='F:/data/taxi/points1s'
	os.mkdir(resdir)

	folder=map(lambda x:'0'+str(x),range(1,15))
	print folder

	for f in folder:
		txts=map(lambda s:base+f+'/'+s,os.listdir(base+f))
		map(lambda txt:InterpolatePoints(txt,resdir),txts)
		# F:/data/taxi/05/5905.txt

