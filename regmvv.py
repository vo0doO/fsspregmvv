#!/usr/bin/python 
#coding: utf8
const={'er_ext_request_id':0,'er_debtor_inn':1,'er_debtor_kpp':2,'er_req_date':3,'er_pack_date':4,'er_debtor_birthday':5,'er_debtor_ogrn':6,'er_ip_sum':7,'er_processed':8,'er_ip_num':9,'er_req_number':10,'er_mvv_agent_code':11,'er_debtor_document':12,'er_mvv_agreement_code':13,'er_mvv_agent_dept_code':14,'er_pack_number':15,'er_req_id':16,'er_pack_id':17,'er_h_spi':18, 'er_fio_spi':19,'er_osp_number':20,'er_debtor_name':21,'er_debtor_address':22,'er_debtor_birthplace':23,'er_entity_type':24,'er_spi_id':25,'er_ip_id':26,'er_ip_risedate':27,'id_type_name':28,'id_number':29,'id_date':30,'req_outgoing_number':31,'id_subject_type':32,'req_metaobjectname':33,'ip_rest_deptsum':34,
'eih_id':0,'eih_pack_number':1,'eih_proceed':2,'eih_agent_code':3,'eih_agent_dept_code':4,'eih_agreement_code':5,'eih_external_key':6,'eih_metaobjectname':7,'eih_date_import':8,'eih_source_barcode':9}
ansfields ={'01':['ser_doc','num_doc','date_doc','issue_organ','rr_type_doc'],'11':['kadastr_n','inv_n_nedv','s_nedv','adres_nedv','nfloor','startdate','share','purpose','enddate'],'08':['deb_state'],'56':['naimorg','adresj','adresf'],'09':['bic_bank','currency_code','acc','bank_name','summa','dept_code','summa_info']}
numstr=('0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y','Z')
cln=', '
getdivnamesql="select osp.div_fullname_title from osp"
getsbnumsql="select counter from sbcount where sbcount.req_date="
currency_type={'EUR':'978','USD':'840','RUB':'810','GBP':'826','RUR':'810'}
import datetime
import hashlib
import logging
import timeit
import time
#import xml.etree.ElementTree as etree
from lxml import etree
def getdivname (cur):
 cur.execute(getdivnamesql)
 osp=cur.fetchall()
 #divname=osp[0][0]
 return osp[0][0]
def preprocessing(cur,con,systcp,dbcp,sql):
 #sql2=('update ext_request set ext_request.processed=2  where  '+str(sql)).decode(systcp).encode(dbcp)
 sql2='update ext_request set ext_request.processed=2  where  '+sql
 try:
  cur.execute(sql2)
 except Exception, e:
  print sql2, str(e)
 con.commit()
 return

def getnotprocessed(cur,systcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code):
 #print str(type(mvv_agent_code))
# if str(type(mvv_agent_code))=="<type 'unicode'>":
#  mvv_agent_code=mvv_agent_code.encode(dbcp)
# else:
#  mvv_agent_code=mvv_agent_code.decode(systcp).encode(dbcp)
#
# if str(type(mvv_agreement_code))=="<type 'unicode'>":
#  mvv_agreement_code=mvv_agreement_code.encode(dbcp)
# else:
#  mvv_agreement_code=mvv_agreement_code.decode(systcp).encode(dbcp)
#
# if str(type(mvv_agent_code))=="<type 'unicode'>":
#  mvv_dept_code=mvv_dept_code.encode(dbcp)
# else:
#  mvv_dept_code=mvv_dept_code.decode(systcp).encode(dbcp)

 sql2="select ext_request.pack_id  from ext_request where mvv_agent_code='" + mvv_agent_code +  "' and mvv_agreement_code='"+ mvv_agreement_code +"' and mvv_agent_dept_code='"+mvv_dept_code+"'  and ext_request.processed = 0 group by pack_id"
 #print "SQL=",sql2
 try:
  cur.execute(sql2)
 except Exception ,e:
  print sql2,e
 pack=cur.fetchall() #множества пакетов
 return pack
def getnumfrompacknumber(cur,systcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,packdate,packnum):
 sql2="select ext_request.pack_id  from ext_request where mvv_agent_code='" + mvv_agent_code +  "' and mvv_agreement_code='"+ mvv_agreement_code +"'  and ext_request.pack_date='"+str(packdate.strftime('%d.%m.%y'))+"'  group by pack_id" 
 cur.execute(sql2)
 num=-1
 pp=cur.fetchall()
 #print 'sql2=',sql2,'len=',len(pp),packnum,'num=',num
 if len (pp)==1:
  if pp[0][0]==packnum:
   num=1
 elif len(pp)>1:
  for ii in range (0,len(pp)):
   #print packnum,pp[ii][0]
   if pp[ii][0]==packnum:
    #print packnum,pp[ii][0],'ii=',ii
    num=ii+1
 #print 'ii=',ii,'num=',num
 return num
def getrecords(cur,packet):
 sql="select * from ext_request where ext_request.pack_id="+str(packet) +" and ext_request.processed = 0"
 cur.execute(sql)
 pack=cur.fetchall()
 return pack
def convtotype(rowdbf,dbvalue,dbcp,dbfcp):
 #Проверяем длину типа N 0
 if rowdbf[1]=='N':
  if len(rowdbf)==3:#if rowdbf[3]==0:   #целое проверка длины
   if len(str(dbvalue))>rowdbf[2]:
    val=int(str(dbvalue)[len(str(dbvalue))-rowdbf[2]:len(str(dbvalue))])
   else:
    val=float(dbvalue)
  elif str(type(dbvalue))=="<type 'NoneType'>":
   val=0 
  else:
   val=dbvalue
#int( str(dbvalue)[len(str(dbvalue)-rowdbf[2]:len(str(dbvalue)))])
 elif rowdbf[1]=='C':
  if  str(type(dbvalue))=="<type 'datetime.date'>":
   try:
    val=str(dbvalue.strftime("%d.%m.%Y"))
   except:
    val=''
  elif str(type(dbvalue))=="<type 'int'>":
   val=str(dbvalue)
  elif str(type(dbvalue))=="<type 'long'>":
   val=str(dbvalue)
  elif str(type(dbvalue))=="<class 'decimal.Decimal'>":
   val=str(dbvalue)
  elif str(type(dbvalue))=="<type 'NoneType'>":
   val=''
  elif str(type(dbvalue))=="<type 'unicode'>":
   if dbfcp=="UTF-8":
    val=dbvalue
   elif dbfcp=="CP866":
    val=dbvalue.replace(unichr(0xab),chr(0x22))
    val=val.replace(unichr(0xbb),chr(0x22))
    val=val.encode(dbfcp)#BUG FIX
   else:
    print type(dbvalue),dbfcp
    val=dbvalue.encode(dbfcp)
  else:
   try:
    val =(dbvalue).encode(dbfcp)
   except:
    print type(dbvalue)
    val='' 
 elif rowdbf[1]=='D':
  val=(dbvalue).strftime('%Y%m%d')
 return val
#def getfizur()
def dbfaddrecord(rec,dbfscheme,dbscheme,dbvalues,dbsystcp,dbcp,dbfcp,cur):
 fizur=(dbvalues[const['er_entity_type']] in (95,2))
 if fizur:
  fizurnum=1
 else:
  fizurnum=2
 #ii=range(0,12) #ЧТо за нах
 #range(0,3)
 ii=range(0,len(dbfscheme))
 j=0
 #print fizurnum
 #print str(type(dbscheme[0][0]))
 for i in ii:
  if str(type(dbscheme[i][0]))=="<type 'list'>":
   v=dbscheme[i][0][fizurnum-1]
  else:
   print dbscheme[i][0]
   v=dbscheme[i][0]
  if v in const.keys():
   #print v,dbvalues[const[v]]
   #print dbfscheme[i],str(type(dbvalues[const[v]])),dbvalues[const[v]]
   rec[dbfscheme[i][0]]=convtotype(dbfscheme[i], dbvalues[const[v]],dbcp,dbfcp)
  # dbvalues[const[v]]
  else:
   #print v,'false'
   if v=='divname':
    divname=getdivname(cur)
    rec[dbfscheme[i][0]]=convtotype(dbfscheme[i], divname,dbcp,dbfcp)
   elif  v=='fizur':
    rec[dbfscheme[i][0]]=convtotype(dbfscheme[i], str(fizurnum),dbcp,dbfcp)
 rec.store()
 return rec
def getsbfilename (packdate,num,filial,client):
# rDDMFFFF.NXX
# FFFF=8585 X=61
 m=int((packdate).strftime('%m'))
 d=(packdate).strftime('%d')
 filename='r'+d+numstr[m]+filial+'.'+numstr[num]+client 
 return filename
def getsbnum (con,cur,packdate):
 dd=packdate
 dstr=str((dd).strftime('%d.%m.%y'))
 print dstr
 cur.execute(getsbnumsql+"'"+(dstr)+"'")
 cnt=cur.fetchall()
 if len (cnt)<>0:
  if int(cnt[0][0])>=34:
   print "C>=34"
   dd=datetime.date.today()
   dstr=str(dd.strftime('%d.%m.%y'))
   cur.execute(getsbnumsql+"'"+(dstr)+"'")
   cnt=cur.fetchall()

 if len (cnt)==0:
  print "cnt =0"
  cur.execute("INSERT INTO SBCOUNT (COUNTER, REQ_DATE)  VALUES (0, '"+dstr+"')")
  cur.execute(getsbnumsql+"'"+str(dstr)+"'")
  #cur.execute("COMMIT WORK")
  con.commit();
  cur.execute(getsbnumsql+"'"+(dstr)+"'")
  cnt=cur.fetchall()
 if int(cnt[0][0])<34:
  num=int(cnt[0][0])+1
  cur.execute("UPDATE SBCOUNT set COUNTER="+str(num) +"  WHERE REQ_DATE='"+dstr+"'")
  print "UPDATE SBCOUNT set COUNTER="+str(num) +" WHERE REQ_DATE='"+dstr+"'",num
  con.commit() 
 else:
  num=-1
 cur.execute(getsbnumsql+"'"+str(dstr)+"'")
 cnt=cur.fetchall()
 if num>0:
  num=int (cnt[0][0])
 return num,dd
def setprocessed(cur,con,systcp,dbcp,packet):
 sql2='update ext_request set ext_request.processed=1  where  ext_request.pack_id='+str(packet)
 try:
  cur.execute(sql2.decode(systcp).encode(dbcp))
 except Exception, e:
  print sql2, str(e) 
 con.commit()
 return 
def xmladdrecordold(elname,root,xmlscheme,dbscheme,dbvalues,dbsystcp,dbcp,dbfcp):
 if root.tag==elname:
  zapros=root
 else:
  zapros=etree.SubElement(root,elname)
 #el=etree.SubElement(zapros,xmlscheme[0][0])
 #i=0
 #j=1
 #for i in range(0,3):
 # el=etree.SubElement(zapros,xmlscheme[i][0])
 # dbv=convtotype(xmlscheme[i],dbvalues[dbscheme[i]],dbcp,dbfcp)
 # dbvalue=dbvalues[dbscheme[i]]
 # print  len(str(dbvalue)),str(type(dbvalue))
 # el.text=dbv
 fizur=(dbvalues[const['er_entity_type']] in (95,2))
 if fizur:
  fizurnum=1
 else:
  fizurnum=2
 #ii=range(0,6)
 #range(0,3)
 ii=range(0,len(xmlscheme))
 j=0
 for i in ii:
  if str(type(dbscheme[i]))=="<type 'tuple'>":
   j=fizurnum
  else:
   j=0
  if j==0:
   #print str(type(dbscheme[i])),xmlscheme[i][0],xmlscheme[i][1]
#,str(type(dbvalues[dbscheme[i]]))
   if str(type(dbscheme[i]))=="<type 'unicode'>":
    el=etree.SubElement(zapros,xmlscheme[i][0])
    #el.text=str(dbscheme[i].encode(dbfcp))
    #print el.text
   elif str(type(dbscheme[i]))=="<type 'str'>" :
    if  dbscheme[i]=='fizur':
     el=etree.SubElement(zapros,xmlscheme[i][0])
     el.text=str(fizurnum)
    else:
     el=etree.SubElement(zapros,xmlscheme[i][0])
     el.text=dbscheme[i].decode('UTF-8')
   else:
     el=etree.SubElement(zapros,xmlscheme[i][0])
     el.text=convtotype(xmlscheme[i],dbvalues[dbscheme[i]],dbcp,'UTF-8').decode('UTF-8')
     #print convtotype(xmlscheme[i],dbvalues[dbscheme[i]],dbcp,dbfcp)
  else:
   #print str(type(dbscheme[i][j-1])),xmlscheme[i][1]
   if str(type(dbscheme[i][j-1]))=="<type 'unicode'>":
     print "UN"
     el=etree.SubElement(zapros,xmlscheme[i][0])
     #bug
     el.text=dbscheme[i][j-1].decode(dbsystcp).encode(dbfcp)
   elif str(type(dbscheme[i][j-1]))=="<type 'str'>" and dbscheme[i][j-1]=='fizur':
     el=etree.SubElement(zapros,xmlscheme[i][0])
     el.text=str(fizurnum)
   else:
     el=etree.SubElement(zapros,xmlscheme[i][0])
     el.text=convtotype(xmlscheme[i],dbvalues[dbscheme[i][j-1]],dbcp,dbfcp).decode('UTF-8')
 return root
def strtoconst(str):
 return
def xmladdrecord(elname,root,xmlscheme,dbscheme,dbvalues,dbsystcp,dbcp,dbfcp,cur,par):
 #print 'XMLs',root.tag, elname
 if root.tag==elname:
  zapros=root
 else:
  zapros=etree.SubElement(root,elname)
 fizur=(dbvalues[const['er_entity_type']] in (95,2))
 debt=dbvalues[const['er_debtor_name']].split(' ')
 lastname= debt[0]
 try:
  firstname= debt[1] 
 except:
  firstname=''
 try:
  secondname= debt[2]
 except:
  secondname=''
 if fizur:
  fizurnum=1
 else:
  fizurnum=2
 for i in range(0,len(xmlscheme)):
  if str(type(dbscheme[i]))=="<type 'tuple'>":
   j=fizurnum
  else:
   j=0
  if j==0:
   passport=getpassport(cur,dbvalues[const['er_ip_id']])
   #print 'PW',passport
   #print dbscheme[i], dbscheme[i] in const.keys()
   if dbscheme[i] in const.keys():
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=convtotype(xmlscheme[i],dbvalues[const[dbscheme[i]]],dbcp,'UTF-8')
    #.decode(dbsystcp)
   elif dbscheme[i]=='lastname':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=lastname
   elif dbscheme[i]=='firstname':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=firstname
   elif dbscheme[i]=='secondname':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=secondname
   elif dbscheme[i]=='er_req_time':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    reqid=dbvalues[const['er_req_id']]
    cur.execute('select document.create_date from document where id='+str(reqid))
    r=cur.fetchall()
    dt=r[0][0]
    #print dt,dt.strftime('%H:%M')
    el.text=dt.strftime('%H:%M')
   #'er_req_time'
   elif dbscheme[i]=='ser_doc':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=passport[0]
   elif dbscheme[i]=='num_doc':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=passport[1]
   elif dbscheme[i]=='date_doc':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    #print  str(type(passport[2])) 
    if str(type(passport[2]))=="<type 'datetime.date'>":
     el.text=passport[2].strftime('%d.%m.%Y')
    else:
     el.text=''
   elif dbscheme[i]=='issue_organ': 
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=passport[3]
   elif dbscheme[i]=='er_debtor_birthyear':            
    el=etree.SubElement(zapros,xmlscheme[i][0])
    dt=dbvalues[const['er_debtor_birthday']]
    if str(type(dt))=="<type 'datetime.date'>":
     el.text=dt.strftime('%Y')
    else:
     el.text=''
   elif dbscheme[i]=='ignore':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=''
   elif dbscheme[i]=='filename':
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=par['filename']
   elif ';' in dbscheme[i]:
    #print 'split', ';' in dbscheme[i]
    st=dbscheme[i].split(';')
    #print st[1]
    st2=''
    for k in range(len(st)): 
     if st[k] in const.keys():
      st2=st2+convtotype(['tp','C'],dbvalues[const[st[i]]],dbcp,dbfcp).decode(dbsystcp)
     
     else:
      st2=st2+st[k]
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=st2#.decode(dbsystcp)
   else:
    el=etree.SubElement(zapros,xmlscheme[i][0])
    el.text=dbscheme[i]

def getanswertype(ansfields,ansnodes):
 #Если данных нет возвращаем []
 #Если есть данные возвращаем список полей которые есть
 ans=[]
 for i in range(len(ansfields)):
  nd=ansnodes.find(ansfields[i][0])
  if str(type(nd)) =="<type 'lxml.etree._Element'>":
   ans.append([nd.tag,ansfields[i][1],ansfields[i][2]])
   #print ans 
 return ans
  #in consts.keys() 
def getipid (cur,systcp,dbcp,req_id):
 #print "getip:",req_id
 try:
  rid=int(req_id)
 except:
  ipid=-1
 else:
  sq="select ext_request.ip_id from ext_request where ext_request.req_id='"+req_id+"'"
 #print sq
 try:
  cur.execute(sq)
 except Exception,e:
  print "err"
 #cur.execute(sq)
 else: 
  r=cur.fetchall()
 #print "getip len r",len(r)
 try:
  ipid=r[0][0]
 except:
   ipid=-1
 return ipid
def getgenerator(cur,gen):
 sq="SELECT GEN_ID("+gen+", 1) FROM RDB$DATABASE"
 try:
  cur.execute(sq)
 except:
  print "err"
 cur.execute(sq)
 r=cur.fetchall()
 try:
  g=r[0][0]
 except:
  g=-1
 return g
def quoted(a):
 st="'"+a+"'"
 return st
def getidnum(cur,dbsystcp,dbcp,ipid):
 sq="select doc_ip.id_no from doc_ip  where doc_ip.id="+str(ipid)
 cur.execute(sq)
 r=cur.fetchall()
 try:
  rr=r[0][0]
 except:
  rr=0
 return rr

def setnegative(cur,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,packid):
 sqltemp=[]
 #print type
 meta="EXT_RESPONSE"
 id=getgenerator(cur, "SEQ_DOCUMENT") #"SEQ_EXT_INPUT_HEADER") #"SEQ_DOCUMENT")
 #cur.execute('select max(id) from ext_input_header ')
 #er=cur.fetchall()
 #max=er[0][0]
 #if id<max:
 # cur.execute('ALTER SEQUENCE SEQ_EXT_INPUT_HEADER RESTART WITH '+str(max))
 # con.commit()
 # informwarn(u'Сбит генератор SEQ_DOCUMENT. Исправляю значение.'+str(max)+','+str(id))
 # id=getgenerator(cur,"SEQ_EXT_INPUT_HEADER")
 ipid=getipid (cur,dbsystcp,dbcp,req_id)
 #packid=getgenerator(cur,"DX_PACK")
 hsh=hashlib.md5()
 hsh.update(str(id))
 extkey=hsh.hexdigest()
 sq="INSERT INTO EXT_INPUT_HEADER (ID, PACK_NUMBER, PROCEED, AGENT_CODE, AGENT_DEPT_CODE, AGENT_AGREEMENT_CODE, EXTERNAL_KEY, METAOBJECTNAME, DATE_IMPORT, SOURCE_BARCODE) VALUES ("+str(id)+cln+str(packid)+cln+"0"+cln+ quoted(mvv_agent_code)+cln+ quoted(mvv_dept_code)+cln+quoted(mvv_agreement_code)+cln+quoted(extkey)+cln+quoted(meta)+cln+quoted(dt)+cln+" NULL)" 
 #print str(type(sq)),sq
 cur.execute(("select * from ext_request where req_id="+req_id).decode('CP1251'))
 er=cur.fetchall();
 datastr=str("Нет сведений").decode('UTF8')
 idnum=convtotype(['','C'], getidnum(cur,dbsystcp,dbcp,ipid),'UTF-8','UTF-8')
 ent_name=convtotype(['','C'],er[0][const["er_debtor_name"]],'UTF-8','UTF-8')
 ent_bdt=convtotype(['','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8')
 #print "END",ent_bdt
 #print "ENT",str(type(ent_bdt)), len(ent_bdt)
 if len(ent_bdt)<>0:
  ent_by=quoted(ent_bdt.split('.')[2])
  ent_bdt=quoted(ent_bdt)
 else:
  ent_bdt='Null'
  ent_by ='Null'
 ent_inn=convtotype(['','C'],er[0][const["er_debtor_inn"]],'UTF-8','UTF-8')
 req_num=convtotype(['','C'],er[0][const["er_req_number"]],'UTF-8','UTF-8')
 ipnum=convtotype(['','C'],er[0][const["er_ip_num"]],'UTF-8','UTF-8')
 #convtotype(['','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8')
 #print str(type(ent_name))
 #print ent_bdt,ent_by
 sq2="INSERT INTO EXT_RESPONSE (ID, RESPONSE_DATE, ENTITY_NAME, ENTITY_BIRTHYEAR, ENTITY_BIRTHDATE, ENTITY_INN, ID_NUM, IP_NUM, REQUEST_NUM, REQUEST_ID, DATA_STR, ANSWER_TYPE) VALUES ("+str(id)+cln+quoted(dt)+cln+quoted(ent_name)+cln+(ent_by)+cln+(ent_bdt)+cln+quoted(ent_inn)+cln+quoted(idnum)+cln+ quoted(ipnum)+cln+quoted(req_num)+cln+str(req_id)+cln+quoted(datastr)+cln+quoted('02')+")"
 #print 'SQ2',sq2
 #cur.execute(sq)
 #cur.execute(sq2)
 #print timeit.Timer("""
 #con.commit() 
 #""").repeat(1)
 sqltemp.append(sq)
 sqltemp.append(sq2)
 return sqltemp
def setpositive(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,ans,a,packid):
 sqltemp=[]
 #print "LEN ANS:",len(ans),"I AM IN",req_id
 #packid=getgenerator(cur,"DX_PACK")
 for aa in range(len(ans)):
  #print ans[aa][1],aa
  #print 'ANS LEN',len(ans[aa][2].keys())
  doc=a.find(ans[aa][0])
  if ans[aa][1]=='01':
   id=getgenerator(cur,"SEQ_DOCUMENT")
   ipid=getipid (cur,dbsystcp,dbcp,req_id)
   #print "IPID",ipid
  #packid=getgenerator(cur,"DX_PACK")
   hsh=hashlib.md5()
   hsh.update(str(id))
   extkey=hsh.hexdigest()
   #print extkey,ipid
   docs={}
   for dd in ans[aa][2].keys():
    docs[dd]=getxmlvalue(dd,ans[aa],doc)
   #print "DOCS",docs
   docs=gettypedoc(cur,'UTF-8','CP1251',docs)
   #print docs, not ('Null' in docs.values()), not ('' in docs.values())
   if ('Null' in docs.values()):
    informwarn(u"Данные о паспорте не полные, пропускаются. "+str(req_id))
   elif ('' in docs.values()):
    informwarn(u"Данные о паспорте не полные, пропускаются. "+str(req_id))
    #print "Негативная"
    #sqq=setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,'02',id,packid,extkey,"Данные с ошибкой")
    #for sqt in sqq:
    # sqltemp.append(sqt)
   else:
    sqq=setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,'01',id,packid,extkey,"Есть сведения") 
    for sqt in sqq:
     sqltemp.append(sqt)
    
    cur.execute(("select * from ext_request where req_id="+req_id).decode('CP1251'))
    er=cur.fetchall()
    #print len(er)
    #datastr="Есть сведения"
    idnum=convtotype([' ','C'], getidnum(cur,dbsystcp,dbcp,ipid),'UTF-8','UTF-8')
    ent_name=convtotype([' ','C'],er[0][const["er_debtor_name"]],'UTF-8','UTF-8')
    #print str(type((ent_name)))
    ent_bdt=(convtotype([' ','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8'))
    if len(ent_bdt)<>0:
     ent_by=quoted(ent_bdt.split('.')[2])
     ent_bdt=quoted(ent_bdt)
    else:
     ent_bdt='Null'
     ent_by='Null'
    
    ent_inn=convtotype([' ','C'],er[0][const["er_debtor_inn"]],'UTF-8','UTF-8')
    req_num=convtotype([' ','C'],er[0][const["er_req_number"]],'UTF-8','UTF-8')
    ipnum=convtotype([' ','C'],er[0][const["er_ip_num"]],'UTF-8','UTF-8')
    id=getgenerator(cur,"EXT_INFORMATION")
    hsh.update(str(id))
    svextkey=hsh.hexdigest()
    sq3="INSERT INTO EXT_INFORMATION (ID, ACT_DATE, KIND_DATA_TYPE, ENTITY_NAME, EXTERNAL_KEY, ENTITY_BIRTHDATE, ENTITY_BIRTHYEAR, PROCEED, DOCUMENT_KEY, ENTITY_INN) VALUES ("+str(id)+cln+quoted(dt)+cln+quoted(ans[aa][1])+cln+quoted(ent_name)+cln+quoted(svextkey)+cln+(ent_bdt)+cln+(ent_by)+cln+quoted('0')+cln+quoted(extkey)+cln+quoted(ent_inn)+")"
    #print "SQ3=",sq3,ans[aa][2].keys()
    doc=a.find(ans[aa][0])
    #docs={}
    #for dd in ans[aa][2].keys():
    # docs[dd]=getxmlvalue(dd,ans[aa],doc)
    #docs=gettypedoc(cur,'UTF-8','CP1251',docs)
    #print docs
    #print "Паспорт номер:",docs['ser_doc']," ",docs['num_doc']," ",docs['date_doc'],docs['issue_organ']
    sq4="INSERT INTO EXT_IDENTIFICATION_DATA (ID, NUM_DOC, DATE_DOC, CODE_DEP, SER_DOC, FIO_DOC, STR_ADDR, ISSUED_DOC,type_doc_code) VALUES ("+str(id)+cln+quoted(docs['num_doc'])+cln+quoted(docs['date_doc'])+cln+"NULL"+cln+quoted(docs['ser_doc'])+cln+quoted(ent_name)+cln+"NULL,"+quoted(docs['issue_organ'])+cln+quoted(docs['type_doc'])+")"
    #print "SQ4 ID=",sq4
    cur.execute(sq3)
    #.decode('UTF-8').encode('CP1251'))
    #con.commit()
    cur.execute(sq4)
    #.decode('UTF-8').encode('CP1251'))
    #con.commit()
    sqltemp.append(sq3)
    sqltemp.append(sq4)
  if ans[aa][1]=='11':
   rights=a.find(ans[aa][0])
   right=rights.findall(ans[aa][2]['right'])
   #Проверка присутствует ли дата ликвидации
   #right[]
   #print 'LEN RIGTH',len(right)
   for rr in right:
    id=getgenerator(cur,"SEQ_DOCUMENT")
    ipid=getipid (cur,dbsystcp,dbcp,req_id)
    #print "IPID",ipid
    #print 'RR TAG',rr.tag,etree.tostring(rr)
    hsh=hashlib.md5()
    hsh.update(str(id))
    extkey=hsh.hexdigest()
    #print extkey,ipid
    #datastr='Есть сведения,'+rightv['nfloor'])
    #sqq=setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,ans[aa][1],id,packid,extkey,"Есть сведения") 
    #for sqt in sqq:
    # sqltemp.append(sqt)
    cur.execute(("select * from ext_request where req_id="+req_id).decode('CP1251'))
    er=cur.fetchall()
    print "Поиск", len(er)
    #print len(er)
    #datastr="Есть сведения"
    idnum=convtotype([' ','C'], getidnum(cur,dbsystcp,dbcp,ipid),'UTF-8','UTF-8')
    ent_name=convtotype([' ','C'],er[0][const["er_debtor_name"]],'UTF-8','UTF-8')
    #print str(type((ent_name)))
    ent_bdt=(convtotype([' ','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8'))
    print "ERR", len(ent_bdt),ent_bdt
    if len(ent_bdt)<>0:
     ent_by=quoted(ent_bdt.split('.')[2])
     ent_bdt=quoted(ent_bdt)
    else:
     ent_by='Null'
     ent_bdt='Null'
    ent_inn=convtotype([' ','C'],er[0][const["er_debtor_inn"]],'UTF-8','UTF-8')
    req_num=convtotype([' ','C'],er[0][const["er_req_number"]],'UTF-8','UTF-8')
    ipnum=convtotype([' ','C'],er[0][const["er_ip_num"]],'UTF-8','UTF-8')
    id=getgenerator(cur,"EXT_INFORMATION")
    hsh.update(str(id))
    svextkey=hsh.hexdigest()
    sq3="INSERT INTO EXT_INFORMATION (ID, ACT_DATE, KIND_DATA_TYPE, ENTITY_NAME, EXTERNAL_KEY, ENTITY_BIRTHDATE, ENTITY_BIRTHYEAR, PROCEED, DOCUMENT_KEY, ENTITY_INN) VALUES ("+str(id)+cln+quoted(dt)+cln+quoted(ans[aa][1])+cln+quoted(ent_name)+cln+quoted(svextkey)+cln+(ent_bdt)+cln+(ent_by)+cln+quoted('0')+cln+quoted(extkey)+cln+quoted(ent_inn)+")"
    #print "SQ3=",sq3
    #print 'ANS3',ans[aa][2].keys()
    #print 'ANS3',ans[aa][2].values()
    #ans[aa][2].values()

    #id=getgenerator(cur,"SEQ_DOCUMENT")
    #sq3="INSERT INTO EXT_INFORMATION (ID, ACT_DATE, KIND_DATA_TYPE, ENTITY_NAME, EXTERNAL_KEY,ENTITY_BIRTHDATE, ENTITY_BIRTHYEAR, PROCEED, DOCUMENT_KEY, ENTITY_INN) VALUES  ("+str(id)+cln+quoted(dt)+cln+quoted(ans[aa][1])+cln+quoted(ent_name)+cln+str(ipid)+cln+quoted(ent_bdt)+cln+quoted(ent_by)+cln+quoted('0')+cln+str(rid)+cln+quoted(ent_inn)+")"
    #print sq3
    rightv={}
    for dd in ans[aa][2].keys():
     #print "DD",dd,getxmlvalue(dd,ans[aa],rr),ans[aa][2].values()
     rightv[dd]=getxmlvalue(dd,ans[aa],rr)
    #print rightv
    #Вставка response
    #print str(type (rightv['purpose']))
    datastr='Есть сведения. Тип: '+rightv['purpose'].encode('UTF-8')+'; Доля: '+rightv['share'].encode('UTF-8')+'; Дата рег.: '+rightv['startdate'].encode('UTF-8') 
    #print str(type(datastr)),datastr
    #for rrr in rightv.keys():
    # datastr=datastr+rightv[rrr].decode('UTF-8')+cln
    #print "END", len (rightv['enddate'])
    #print "END", rightv['enddate']
    if not ('enddate' in rightv.keys()):
     #print extkey ans[aa][1]
     sqq=setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,'01',id,packid,extkey,datastr)
     for sqt in sqq:
      sqltemp.append(sqt)
     #print "XFFFF",rightv['nfloor']
     #print rightv.keys()
     #rightv['nfloor']=Null
     #rightv['floor']=Null #rightv['nfloor'].split('/')[0][0:3]
     #print "FLOOR",rightv['floor'],rightv['nfloor']
     #print rightv['kadastr_n'],rightv['inv_n_nedv'],rightv['s_nedv'],rightv['nfloor'],rightv['adres_nedv']
     sq4="INSERT INTO EXT_SVED_NEDV_DATA (ID, KADASTR_N, ADRES_NEDV, S_NEDV, FLOOR, LITER_N, INV_N_NEDV, NFLOOR, NAIM_NEDV) VALUES ("+str(id)+cln+quoted(rightv['kadastr_n'])+cln+quoted(rightv['adres_nedv'])+cln+rightv['s_nedv']+cln+"Null"+cln+"NULL"+cln+quoted(rightv['inv_n_nedv'])+cln+"Null"+cln+quoted(rightv['purpose'])+")"
     sqltemp.append(sq3)
     sqltemp.append(sq4)
    else:
     informwarn (u'Данные с ошибкой, сведения о ранее принадлежавшей недвижимости '+str(req_id))
     #sqq=setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,'02',id,packid,extkey,"Данные с ошибкой, сведения о ранее принадлежавшей недвижимости")
     #for sqt in sqq:
     # sqltemp.append(sqt)
     #print "SQ4",sq4
    #cur.execute(sq3)
#.decode('UTF-8').encode('CP1251'))
    #con.commit()
    #cur.execute(sq4)
    #sqltemp.append(sq3,sq4)
#.encode('CP1251'))
    #con.commit()
     
 #Заполняем датумы
#cur.execute(sq)
#.decode('UTF-8').encode(dbcp))
#cur.execute(sq2.decode('UTF-8').encode('CP1251'))
#.decode('UTF-8').encode(dbcp))
#con.commit()
   
 return sqltemp
def getxmlvalue(name,ans,a):
 #Проверка есть ли длинный путь
 nd=ans[2][name]
 #print len(nd.split(':')),
 ndd=nd.split(":")
 #print "NDD",ndd,a.tag
 nn=a
 #nn.tag
 for n in ndd:
  nn=nn.find(n)
  #print 'NN', nn.text
  #print nn.tag,nn.text
  try:
   val=convtotype([' ','C'],nn.text,'UTF-8','UTF-8')
  except:
   val=''
 return val
def setresponse(cur,con,dbsystcp,dbcp,mvv_agent_code,mvv_agreement_code,mvv_dept_code,req_id,dt,anst,id,packid,extkey,datastr): 
 sqltemp=[]
 meta="EXT_RESPONSE"
 #id=getgenerator(cur,"SEQ_DOCUMENT")
 ipid=getipid (cur,dbsystcp,dbcp,req_id)
 #packid=getgenerator(cur,"DX_PACK")
 #hsh=hashlib.md5()
 #hsh.update(str(id))
 #extkey=hsh.hexdigest()
 sq="INSERT INTO EXT_INPUT_HEADER (ID, PACK_NUMBER, PROCEED, AGENT_CODE, AGENT_DEPT_CODE, AGENT_AGREEMENT_CODE, EXTERNAL_KEY, METAOBJECTNAME, DATE_IMPORT, SOURCE_BARCODE) VALUES ("+str(id)+cln+str(packid)+cln+"0"+cln+ quoted(mvv_agent_code)+cln+ quoted(mvv_dept_code)+cln+quoted(mvv_agreement_code)+cln+quoted(extkey)+cln+quoted(meta)+cln+quoted(dt)+cln+" NULL)" 
 #print str(sq)
 cur.execute(("select * from ext_request where req_id="+req_id).decode('CP1251'))
 er=cur.fetchall();
 #print "LEN ER:",len(er)
 #datastr="Есть сведения"
 idnum=convtotype([' ','C'], getidnum(cur,dbsystcp,dbcp,ipid),'UTF-8','UTF-8')
 ent_name=convtotype([' ','C'],er[0][const["er_debtor_name"]],'UTF-8','UTF-8')
 #print str(type((ent_name)))
 ent_bdt=convtotype([' ','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8')
 if len(ent_bdt)<>0:
  ent_by=ent_bdt.split('.')[2]
  ent_bdt=quoted(ent_bdt)
 else:
  ent_by ='Null'
  ent_bdt='Null'
 ent_inn=convtotype([' ','C'],er[0][const["er_debtor_inn"]],'UTF-8','UTF-8')
 req_num=convtotype([' ','C'],er[0][const["er_req_number"]],'UTF-8','UTF-8')
 ipnum=convtotype([' ','C'],er[0][const["er_ip_num"]],'UTF-8','UTF-8')
 #convtotype(['','C'],er[0][const["er_debtor_birthday"]],'UTF-8','UTF-8')
 #print str(type(ent_name))
 #rid=id
 #print str(type(datastr))
 #sq "DATA",quoted(datastr)
 #sq2="DATA"+quoted(datastr)
 #print str(id)
 #sq2=''
 dtstr=datastr.decode('UTF-8')
 if anst<>'Null':
  sq2="INSERT INTO EXT_RESPONSE (ID, RESPONSE_DATE, ENTITY_NAME, ENTITY_BIRTHYEAR, ENTITY_BIRTHDATE, ENTITY_INN, ID_NUM, IP_NUM, REQUEST_NUM, REQUEST_ID, DATA_STR, ANSWER_TYPE) VALUES ("+str(id) +cln+quoted(dt)+cln+quoted(ent_name)+cln+(ent_by)+cln+(ent_bdt)+cln+quoted(ent_inn)+cln+quoted(idnum)+cln+ quoted(ipnum)+cln+quoted(req_num)+cln+ (req_id)+cln+quoted(dtstr)+cln+quoted(anst)+")"
 else:
  sq2="INSERT INTO EXT_RESPONSE (ID, RESPONSE_DATE, ENTITY_NAME, ENTITY_BIRTHYEAR, ENTITY_BIRTHDATE, ENTITY_INN, ID_NUM, IP_NUM, REQUEST_NUM, REQUEST_ID, DATA_STR, ANSWER_TYPE) VALUES  ("+str(id) +cln+quoted(dt)+cln+quoted(ent_name)+cln+(ent_by)+cln+(ent_bdt)+cln+quoted(ent_inn)+cln+quoted(idnum)+cln+ quoted(ipnum)+cln+quoted(req_num)+cln+ (req_id)+cln+quoted(dtstr)+cln+"Null)"
 sqltemp.append(sq)
 sqltemp.append(sq2)
 #logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'./regmvv.log')
 #print "SQL1=",sq
 #print "SQL2=",sq2
 #logging.debug(sq)
 #logging.debug(sq2)
 #cur.execute(sq)
 #con.commit()
 #cur.execute(sq2)
#.decode('UTF-8').encode('CP1251'))
 #con.commit()
 
 return sqltemp
def gettypedoc(cur,dbsystcp,dbcp,docs):
 if 'rr_type_doc' in docs:
  rr=docs['rr_type_doc']
  cur.execute('select directory_types.dirt_code from directory_types where directory_types.dirt_code_rosreestr='+quoted(rr))
  r=cur.fetchall() 
  #print r[0][0]
  print docs.keys(),len(r),rr
  if len(r)>0:
   docs['type_doc']=convtotype([' ','C'],r[0][0],'UTF-8','UTF-8')
 return docs
def setattribs(cur,dbcp,dbfcp,xml,xmlscheme,rr,delta,num,param):
 fizur=(rr[const['er_entity_type']] in (95,2))
 if fizur:
  fizurnum=1
 else:
  fizurnum=2
 nn=getnumtodepartment (cur,dbcp,dbfcp)
 numto=nn[0]
 numdepartment=nn[1]
 id=rr[const['er_ip_id']]
 #print "RR",rr
 sq='select * from document where id=(select document.parent_id from document where id='+str(id)+')'
 #print sq
 cur.execute(sq)
 docs=cur.fetchall()
 #print "DOCS",docs
 if len(docs) >0 :
  documentclassid=convtotype(['tp','C'],docs[0][0],'UTF-8','UTF-8')
 else: 
  documentclassid=u'1' 
 for kk in xmlscheme.attrib.keys():
  if xmlscheme.attrib[kk] in const:
   #print kk,str(type(rr[const[zapros.attrib[kk]]]))
   xml.attrib[kk]=convtotype(['tp','C'],rr[const[xmlscheme.attrib[kk]]],'UTF-8','UTF-8')
  elif xmlscheme.attrib[kk]=='num':
   xml.attrib[kk]=convtotype(['tp','C'],num,'UTF-8','UTF-8')
  elif xmlscheme.attrib[kk]=='ansdate':
   xml.attrib[kk]=str (rr[const['er_req_date']]+delta)
  elif xmlscheme.attrib[kk]=='tonum':
   xml.attrib[kk]=(numto)
  elif xmlscheme.attrib[kk]=='departmentnum':
   xml.attrib[kk]=(numdepartment)
  elif xmlscheme.attrib[kk]=='documentclassid':
   xml.attrib[kk]=(documentclassid)
  elif xmlscheme.attrib[kk]=='fizur':
   xml.attrib[kk]=convtotype(['tp','C'],fizurnum,'UTF-8','UTF-8')
  elif xmlscheme.attrib[kk]=='orgamd':
   xml.attrib[kk]=param['orgamd']
  elif xmlscheme.attrib[kk]=='divamd':
   xml.attrib[kk]=param['divamd']
  elif xmlscheme.attrib[kk]=='edotype':
   xml.attrib[kk]=param['edotype']
  elif xmlscheme.attrib[kk]=='ip_rest_debtsum':
   xml.attrib[kk]=getrestdeptsum(cur,dbcp,dbfcp,id)
  elif kk== 'records':
   pass
  else:
   xml.attrib[kk]=xmlscheme.attrib[kk]
 return xml
def getnumtodepartment (cur,dbcp,dbfcp):
 cur.execute('select osp.territory,osp.department  from osp')
 rr=cur.fetchall()
 numto=convtotype(['tp','C'],rr[0][0],'UTF-8','UTF-8')
 numdepartment=numto+'0'+convtotype(['tp','C'],rr[0][1],'UTF-8','UTF-8')
 return numto, numdepartment
def getid(cur,dbcp,dbfcp,id):
 sql='select * from document where id=(select document.parent_id from document where id='
 sql=sql+str(id)
 cur.execute(sql)
 r=cur.fetchall()
 return r
def getrestdeptsum(cur,dbcp,dbfcp,id):
 sql='select doc_ip_doc.ip_rest_debtsum from doc_ip_doc where  id='
 sql=sql+str(id)
 cur.execute(sql)
 r=cur.fetchall()
 if len(r)>0:
  rr=str(r[0][0])
 else:
  rr=''
 return rr
def inform(st):
 logging.info(st)
 print st
 return
def informwarn(st):
 logging.warning(st)
 print st
 return
def informerr(st):
 logging.error(st)
 print st
 return
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print "Elapsed time:",time.time() - self._startTime # {:.3f} sec".format(time.time() - self._startTime)
        st="Elapsed time:"+str(time.time() - self._startTime) # {:.3f} sec".format(time.time() - self._startTime)
        logging.info(st)
def getpassport(cur,ipid):
 sql='select doc_ip_doc.id_dbtr_id_serial, doc_ip_doc.id_dbtr_id_number, doc_ip_doc.id_dbtr_id_date,doc_ip_doc.id_dbtr_id_office from doc_ip_doc where id='+str(ipid)
 #print sql
 cur.execute(sql)
 r=cur.fetchall()
 #print "LEN=",len(r)
 if len(r)<>0:
  serial=r[0][0]
  number=r[0][1] 
  date=r[0][2]
  issue=r[0][3]
 else:
  serial=''
  number=''
  date=''
  issue=''
 return serial,number,date,issue
#def setlogging()
# logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'./regmvv.log')  
# return
#def main():
#if __name__ == "__main__":
#    main()
#type_doc_code
