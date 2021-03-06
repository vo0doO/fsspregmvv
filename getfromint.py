#!/usr/bin/python
#coding: utf8
from regmvv import *
from lxml import etree
from dbfpy import dbf
import fdb
import sys
import logging
def main():
#Обработка параметров
 #print len (sys.argv)
 if len(sys.argv)<=1:
  print ("getfromint: нехватает параметров\nИспользование: getfromint ФАЙЛ_КОНФИГУРАЦИИ")
  sys.exit(2)
 #print sys.argv[1]
#Открытие файла конфигурации
 try:
  f=file(sys.argv[1])
 except Exception,e:
  #print e
  sys.exit(2)
#Парсим xml конфигурации
 cfg = etree.parse(f) 
 #cfg.add_namespace(regmvv)
 cfgroot=cfg.getroot()
#Ищем параметры системы
 systemcodepage=cfgroot.find('codepage').text
#Ищем параметры базы
 dbparams=cfgroot.find('database_params')
 username=dbparams.find('username').text
 password=dbparams.find('password').text
 hostname=dbparams.find('hostname').text
 concodepage=dbparams.find('connection_codepage').text
 codepage=dbparams.find('codepage').text
 database=dbparams.find('database').text
 try:
  port=dbparams.find('port').text
 except:
  print 'default port 3050'
  port='3050'
 
 #print username,password,hostname,concodepage,codepage
#Ищем параметры МВВ
 mvv=cfgroot.find('mvv')
 agent_code=mvv.find('agent_code').text
 dept_code=mvv.find('dept_code').text
 agreement_code=mvv.find('agreement_code').text
 pre=mvv.find('preprocessing')
 logpar=cfgroot.find('logging')
 log_path=logpar.find('log_path').text
 log_file=logpar.find('log_file2').text

 try:
  con = fdb.connect (host=hostname, database=database, user=username, password=password,charset=concodepage,port=port)
 except  Exception, e:
  print("Ошибка при открытии базы данных:\n"+str(e))
  sys.exit(2)
 cur = con.cursor()
 #print str(type(pre)),str(type(pre))<>"<type 'NoneType'>"
 if str(type(pre))<>"<type 'NoneType'>":
  print "PREPROCESS"
  ch=pre.findall('sql')
  #print ch[0].tag,ch[0].text
  for chh in ch:
   #print "CH",chh.text,chh.tag
   sq=chh.text.encode('UTF-8')
   print '!',sq
   #print sq,str(type(sq))
   sql2='update ext_request set ext_request.processed=2  where  '+sq
   try:
    cur.execute(sql2)
    print sql2
   except Exception, e:
    print sql2, str(e)
   con.commit()
   #preprocessing(cur,con,'UTF-8','CP1251',sq)
 ##f.close()
 con.close()
#Определяем тип и путь файла
 filepar=cfgroot.find('file')
 #print filepar
 filecodepage=filepar.find('codepage').text
 print 'CodePage',filecodepage
 output_path=filepar.find('output_path').text
 filetype=filepar.find('type').text
 print filetype
 filenum=filepar.find('numeric').text
 fileprefix=filepar.find('prefix').text
 #fileorgamd=filepar.find('orgamd').text
 #filedivamd=filepar.find('divamd').text
 #fileedotype=filepar.find('edotype').text
 #fileformat=filepar.find('format').text
 #Определение схемы файла должна быть ветка для типов файлов пока разбираем xml
 filiescheme=filepar.findall('scheme')[0]
 #создание root
 #print filiescheme.getchildren()[0].tag
 root2=filiescheme.getchildren()[0]
 #print "X", filetype
 cfgroot.find('file')
 if filetype=='xml':
  #print filenum
  if filenum=='sber':
   cntdbpar=filepar.find('counter_db')
   cntdb_username   =cntdbpar.find('username').text
   cntdb_password   =cntdbpar.find('password').text
   cntdb_hostname   =cntdbpar.find('hostname').text
   cntdb_concodepage=cntdbpar.find('connection_codepage').text
   cntdb_codepage   =cntdbpar.find('codepage').text
   try:
    cntdb_port   =cntdbpar.find('port').text
   except:
    cntdb_port='3050'
   cntdb_database   =cntdbpar.find('database').text
   filial=filepar.find('filial').text
   osp=filepar.find('osp').text
   #Определение заголовка
  print root2.tag
  if 'records' in root2.attrib.keys(): 
  #Если есть атрибут records |Контейнер запроса будет корень,
  #Заголовка нет
   zapros=root2
   #print zapros.tag
  else: #Иначе собираем заголовок, и ищем контейнер запросов
   ch=root2.getchildren()	
   reqq=[]
   int2str=[]
   for i in range(len(ch)):
    req=[]
    if ch[i].attrib<>{}:# Если есть атрибут
     if 'records' in ch[i].attrib.keys(): # И атрибут records
     #контейнер запроса будет текущий узел
      #print ch[i].attrib, ch[i].tag
      zapros=ch[i]
     break #выходим из цикла конец сбора заголовка
    req.append(ch[i].tag) #Собираем заголовок
    req.append('C')
    reqq.append(req)
    int2str.append(ch[i].text) #Сбор матрицы значений заголовка
   #print 'reqq',reqq,int2str[0]
   #print zapros.tag
  #Cбор Запроса и его матрицы значений
  ch=zapros.getchildren()[0]
  reqq2=[]
  int2str2=[]
  for i in range(len(ch)):
   req2=[]
   req2.append(ch[i].tag)
   #print ch[i].tag
   req2.append('C')
   reqq2.append(req2)
   int2str2.append(ch[i].text)
  #print reqq2,int2str2
 #Соединяемся с базой ОСП
  try:
   con = fdb.connect (host=hostname, database=database, user=username, password=password,charset=concodepage,port=port)
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur = con.cursor()
  if filenum=='sber':# Если сбербанк подключить базу данных для счетчика
   try:
    con2 = fdb.connect (host=cntdb_hostname, database=cntdb_database, user=cntdb_username, password=cntdb_password,charset=cntdb_concodepage,port=cntdb_port)
   except  Exception, e:
    print("Ошибка при открытии базы данных счетчика:\n"+str(e))
    sys.exit(2)
   cur2 = con2.cursor()

  root=etree.Element(root2.tag)
  #print agreement_code, dept_code
  packets=getnotprocessed(cur,systemcodepage,'CP1251',mvv_agent_code=agent_code,mvv_agreement_code=agreement_code,mvv_dept_code=dept_code)
  p=len(packets)
  #p=1
  inform(u'Найдено '+str(p) +u' пакетов для выгрузки.')
  rrr=0
  with Profiler() as p2:
   for pp in range(0,p):
    root=etree.Element(root2.tag)
    r=getrecords(cur,packets[pp][0])
    lr=len(r)
    rrr=rrr+lr
    #print "PP",pp,packets[pp][0],"LEN R",len(r)
    rr=r[0]
    #print 'ZP',root.tag,zapros.tag
    #Если корень равен запросу значит нету заголовка
    par={}
    if root.tag<>zapros.tag:
     xmladdrecord(root.tag,root,reqq,int2str,rr,systemcodepage,codepage,filecodepage,cur,par)
    #xml= etree.tostring(root, pretty_print=True, encoding=filecodepage, xml_declaration=True)
    #print xml
    #print "ROOT",root.tag,zapros.tag
    if root.tag<>zapros.tag:
     zp=etree.SubElement(root,zapros.tag)
    else:
     zp=root
    zpp=zapros.getchildren()[0]
    par={}
    if filenum=='sber':
     num=getsbnum (con2,cur2,rr[const['er_pack_date']])
     print 'SB',num
     filename=getsbfilename (num[1],num[0],filial,osp)
     print filename
     par['filename']=filename
    else:
     num= getnumfrompacknumber(cur,'UTF-8',codepage,agent_code,agreement_code,dept_code,rr[const['er_pack_date']],rr[const['er_pack_id']])
     filename=fileprefix+str(rr[const['er_osp_number']])+'_'+str(rr[const['er_pack_date']].strftime('%d_%m_%y'))+'_'+str(num)+'.xml'
    for rr in r:
    #rr=r[0]
     #print "ZP",zp.tag,'INT',int2str2,zpp.tag
     #print zpp.tag
     xmladdrecord(zpp.tag,zp,reqq2,int2str2,rr,systemcodepage,codepage,filecodepage,cur,par)
    xml= etree.tostring(root, pretty_print=True, encoding=filecodepage, xml_declaration=True)
    #print xml
    #print filename,num
    f2=open(output_path+filename,'w')
    inform(u'Выгружен файл: ' + filename + u', '+str(lr)+u' запросов. Осталось выгрузить '+ str(p-pp) +u' пакетов.')
    f2.write(xml)
    f2.close()
  inform(u'Выгружено: '+str(rrr)+ u' запросов. В '+str(p)+ u' пакетах') 
  #Убрать
  setprocessed(cur,con,'UTF-8',codepage,packets[pp][0])

 elif filetype=='xmlatrib' or filetype=='pfr':
  fileorgamd=filepar.find('orgamd').text
  filedivamd=filepar.find('divamd').text
  fileedotype=filepar.find('edotype').text
  fileformat=filepar.find('format').text

  #print 'XML',root2.attrib.keys(),root2.attrib.values()
  ch=root2.getchildren()
  reqq=[]
  int2str=[]
  #print root2.tag
  #Создание заголовка xml
#Соединяемся с базой ОСП
  try:
   con = fdb.connect (host=hostname, database=database, user=username, password=password,charset=concodepage,port=port)
  except  Exception, e:
   #print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur = con.cursor()
  root=etree.Element(root2.tag)
  rr=[]
  delta=datetime.timedelta(days=7)
  zapros=root2.getchildren()[0]
  #print zapros.attrib.keys(),zapros.attrib.values()
#Предварительная обработка 
#Определяем список необработанных пакетов
  packets=getnotprocessed(cur,systemcodepage,'CP1251',mvv_agent_code=agent_code,mvv_agreement_code=agreement_code,mvv_dept_code=dept_code)
  #print len(packets)
  #print str(type(agent_code)),str(type('Росреестр'))
  p=len(packets)
 #p=1
 #divname=getdivname(cur)
 #p=3
 #r=getrecords(cur,packets[0][0]) #!!!
 #rr=r[0]
 #root=setattribs(cur,'UTF-8','UTF-8',root,root2,rr,delta,1) 
  print p
  for pp in range(0,p):
   root=etree.Element(root2.tag)
   r=getrecords(cur,packets[pp][0])
   #print "PP",pp,packets[pp][0],"LEN R",len(r)
   rr=r[0]
   root=setattribs(cur,'UTF-8','UTF-8',root,root2,rr,delta,1,{'orgamd':fileorgamd,'divamd':filedivamd,'edotype':fileedotype})
   rr=[]
   for ri in range(len(r)):
    rr=r[ri]
   #print "LEN R",len(r)
    zp=etree.SubElement(root,zapros.tag)
    delta=datetime.timedelta(days=7)
    zp=setattribs(cur,'UTF-8','UTF-8',zp,zapros,rr,delta,ri+1,{})
    for ch in zapros.getchildren():
     sbch=etree.SubElement(zp,ch.tag)
     sbch=setattribs(cur,'UTF-8','UTF-8',sbch,ch,rr,delta,ri+1,{})
   xml= etree.tostring(root, pretty_print=True, encoding=filecodepage, xml_declaration=True)
   r=[]
  #print xml
#  xmladdrecord(root.tag,root,reqq,int2str,rr,systemcodepage,codepage,filecodepage)
#  root2=etree.SubElement(root,zapros.tag)
#  
#  xml= etree.tostring(root, pretty_print=True, encoding=filecodepage, xml_declaration=True)
   num= getnumfrompacknumber(cur,'UTF-8',codepage,agent_code,agreement_code,dept_code,rr[const['er_pack_date']],rr[const['er_pack_id']])
   nulstr='0'*100
   countn=fileformat.count('N')
   ff=fileformat
   ff=ff.replace('N'*countn,nulstr[0:countn-len(str(num))]+str(num))
   ff=ff.replace('Z'*fileformat.count('N'),fileprefix)
   ff=ff.replace('B'*fileformat.count('B'),nulstr[0:fileformat.count('B')-len((fileorgamd))]+fileorgamd)
   ff=ff.replace('C'*fileformat.count('C'),nulstr[0:fileformat.count('C')-len((filedivamd))]+filedivamd)
   ff=ff.replace('Z'*fileformat.count('Z'),fileprefix)
   ff=ff.replace('X'*(fileformat.count('X')-1),fileedotype)
   county=fileformat.count('Y')
   if county==2:
    ff=ff.replace('Y'*county,str(rr[const['er_pack_date']].strftime('%y')))
   else:
    ff=ff.replace('Y'*county,str(rr[const['er_pack_date']].strftime('%Y')))
   ff=ff.replace('D'*fileformat.count('D'),str(rr[const['er_pack_date']].strftime('%d')))
   
   ff=ff.replace('M'*(fileformat.count('M')-1),str(rr[const['er_pack_date']].strftime('%m')))
   ff=ff.replace('A'*fileformat.count('A'),getnumtodepartment(cur,concodepage,'UTF-8')[1])
   filename=ff
   #fileprefix+str(rr[const['er_osp_number']])+'_'+str(rr[const['er_pack_date']].strftime('%d_%m_%y'))+'_'1+str(num)+'.xml'
#  print filename,num
   f2=open(output_path+filename,'w')
   f2.write(xml)
   f2.close()
   setprocessed(cur,con,'UTF-8',codepage,packets[pp][0])
 elif filetype=='dbf':
  #print 'FS', filiescheme.tag
  #print 'root', root2.tag 
  ch=filiescheme.getchildren()
 #Соединяемся с базой ОСП
  try:
   con = fdb.connect (host=hostname, database=database, user=username, password=password,charset=concodepage,port=port)
  except  Exception, e:
   #print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur = con.cursor()
  #divname=getdivname(cur)
  reqdbfscheme=[]
  int2dbfscheme=[]
  for chh in ch:
   #Анализ аттрибутов
   spp=[]
   spp2=[]
   spp.append(chh.tag.replace(' ',''))
   spp.append(chh.attrib['field_type'])
   spp.append(int(chh.attrib['field_size']))
   if 'field_dec' in chh.attrib.keys():
    spp.append(int(chh.attrib['field_dec']))
   #Анализ текcта
   tt=chh.text
   tt=tt.replace(' ','')
   #print tt,  (',' in tt)
   if ',' in tt:
    #print 'YEAH'
    spp2.append(tt.split(','))
    #print spp2
   else:
    spp2.append(tt)
   #print chh.tag
   reqdbfscheme.append(spp) 
   int2dbfscheme.append(spp2)
  #print reqdbfscheme
  #print int2dbfscheme[10][0]
  #print str(type(int2dbfscheme[2][0]))
  packets=getnotprocessed(cur,systemcodepage,'CP1251',mvv_agent_code=agent_code,mvv_agreement_code=agreement_code,mvv_dept_code=dept_code)
  p=len(packets)
  if p>0:
   inform(u'Найдено '+str(p) +u' пакетов для выгрузки.')
   with Profiler() as p2:
    for i in range(0,p):
     pp=packets[i][0]
     #print pp
     r=getrecords(cur,pp)
     rr=r[0]
     num= getnumfrompacknumber(cur,'UTF-8',codepage,agent_code,agreement_code,dept_code,rr[const['er_pack_date']],rr[const['er_pack_id']])
     filename=fileprefix+str(rr[const['er_osp_number']])+'_'+str(rr[const['er_pack_date']].strftime('%d_%m_%y'))+'_'+str(num)+'.dbf'
     db = dbf.Dbf(output_path+filename, new=True)
     db.addField(*reqdbfscheme)
     inform(u'Готовим файл:'+filename+u' для выгрузки ' +str(len(r)) +u' записей.')
     for rr in r:
      rec = db.newRecord()
      dbfaddrecord(rec,reqdbfscheme,int2dbfscheme,rr,'UTF-8',codepage,filecodepage,cur)
      #print db
     db.close()
     #setprocessed(cur,con,'UTF-8',codepage,pp)
  else:
   inform(u"Нет пакетов для выгрузки")
# f.close()
 con.close()
 
   
if __name__ == "__main__":
    main()
