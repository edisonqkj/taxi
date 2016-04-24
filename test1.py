import os
import sys

def ReadTxt(txt):
	f=open(txt)
	content=f.readlines()
	f.close()
	return map(lambda line:line.strip('\n'),content)
	# return content

def WriteTxt(content,path):
	#print len(data[0])
	#print str(len(data))
	# add head
	# content=[unicode('ncols         '+str(int(head[0]))+'\n'),\
	# 		 unicode('nrows         '+str(int(head[1]))+'\n'),\
	# 		 unicode('xllcorner     '+str(head[2])+'\n'),\
	# 		 unicode('yllcorner     '+str(head[3])+'\n'),\
	# 		 unicode('cellsize      '+str(head[4])+'\n'),\
	# 		 unicode('NODATA_value  '+str(head[5])+'\n')]
	# # add data
	# content.extend(map(lambda x:' '.join(map(lambda y:unicode(str(y)),x))+' \n',data))
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

	# already processed
	if os.path.exists(result_path):
		return

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

def RunningState(txt,save_dir):
	print txt
	basename,filename=os.path.split(txt)
	# print  basename,filename
	fname=filename.split('.')[0]
	# result_path=basename+'/'+fname+'state.txt'
	result_path=os.path.join(save_dir,fname+'_state.txt')

	content=ReadTxt(txt)
	states={'run':[],'stop':[],'over':[]}
	run_route=[]
	stop_route=[]

	state=-1
	newline=[]
	for line in content:
		record=Interpret(line)


		if(state==-1):#len(route)==0):
			run_route.append(record)
			stop_route.append(record)
			state=1
			# last1=record
		else:

			if(state==-1 or state==1):
				last=run_route[-1]
			else:
				last=stop_route[-1]

			# duplicate record
			if(last['date'] == record['date'] and \
				last['time']==record['time']):
				continue

			ix=abs(record['x']-last['x'])
			iy=abs(record['y']-last['y'])
			# print ix,iy
			if(ix!=0 or iy!=0):
				if(state==0):
					states['stop'].append(stop_route)
					stop_route=[]
					run_route=[last]
				# else:
				run_route.append(record)
				state=1#'run'
			else:
				if(state==1):
					states['run'].append(run_route)
					run_route=[]
					stop_route=[last]
				# else:
				stop_route.append(record)
				state=0#'stop'
			# last1=record
		# print 'run='+str(len(run_route)),'num_run='+str(len(states['run'])),'num_stop='+str(len(states['stop']))
		newline.append(line+','+str(state)+'\n')

	# print len(states['run']),len(states['stop'])
	# print newline
	WriteTxt(newline,result_path)

	runnum=map(len,states['run'])
	stopnum=map(len,states['stop'])

	# print runnum
	# print stopnum

	run_path=os.path.join(save_dir,fname+'_run.txt')
	stop_path=os.path.join(save_dir,fname+'_stop.txt')

	StateTime(fname,states['run'],run_path)
	StateTime(fname,states['stop'],stop_path)

def StateTime(cid,states,path):
	lines=[]
	# id,time(date hh:mm:ss),x,y
	for state in states:
		time_interval=calcTime(state[0]['dt'],state[-1]['dt'])
		lines.append(','.join([cid,\
							  state[0]['date']+' '+ state[0]['time'],
							  str(state[0]['x']),str(state[0]['y']),\
							  str(time_interval)]\
							  )+'\n')
		# lines.append(','.join([cid,\
		# 					  state[-1]['date']+' '+ state[-1]['time'],\
		# 					  str(state[-1]['x']),str(state[-1]['y'])])+'\n')
		lines.append('\n')
	WriteTxt(lines,path)

def Txt2Json(txt):

	basename,filename=os.path.split(txt)
	# print  basename,filename
	fname=filename.split('.')[0]
	result_path=basename+'/'+fname+'.json'
	print result_path
	content=ReadTxt(txt)
	res_content={"type":"FeatureCollection","features":[]}
	for line in content:
		# id,time(date hh:mm:ss),x,y
		# print line
		params=line.split(',')
		tid=params[0]
		cal=params[1]
		date=cal.split(' ')[0]
		time=cal.split(' ')[1]
		x=float(params[2])
		y=float(params[3])
		coor=[x,y]

		geo={"type":"Point","coordinates":coor}
		prop={"id":tid,"date":date,"time":time}
		feature={"type":"Feature","geometry":geo,"properties":prop}
		res_content["features"].append(feature)
	import json
	jsoncontent=json.dumps(res_content)
	# print jsoncontent[:200]
	WriteTxt([jsoncontent],result_path)


if __name__=='__main__':
	base='F:/data/taxi/'
	resdir='F:/data/taxi/points1s'
	statedir='F:/data/taxi/states'
	# os.mkdir(resdir)
	os.mkdir(statedir)

	folder=map(lambda x:'0'+str(x),range(1,15))
	print folder

	newlines=[]
	for f in folder[:1]:
		txts=map(lambda s:base+f+'/'+s,os.listdir(base+f))
		# print txts
		# map(Txt2Json,txts)
		# RunningState(txts[0])
		map(lambda txt:RunningState(txt,statedir),txts[:1])
		# map(lambda txt:InterpolatePoints(txt,resdir),txts)

