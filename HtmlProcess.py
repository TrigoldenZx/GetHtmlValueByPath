#-*- coding:utf-8 -*-
from HTMLParser import HTMLParser
import re

class HTMLProcess(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tags=[]
        self.taglistcnt=0
        self.ret=[]
        
    def feed(self,tags,data):
        ret = -1
        self.tags=[] #reset tag lists
        self.taglistcnt=0
        self.ret=[]
        ret = self.set_tags(tags)
        if ret > 0:
            HTMLParser.feed(self,data)
        return ret
    
    def set_tags(self,tagstr):
        ret = -1
        if isinstance(tagstr,unicode):
            ret = 0
            if tagstr.endswith(u';',0,1): #filte the first char is ','
                tagstr=tagstr[1:]

            subtaglist = tagstr.split(u';')#get the node paths
            cnt = len(subtaglist)
            
            for i in range(0,cnt):
                if subtaglist[i].endswith(r'/',0,1):#filte the first char is '/'
                    subtaglist[i] = subtaglist[i][1:]
                tags = []
                getflag = [False]
                temp = subtaglist[i].split(r'/')
                for tag in temp:
                    tagflag = [tag.split(r'(')[0],False,self.getTgtAttrs(tag)]
                    tags.append(tagflag)
                self.tags.append((len(tags),tags,getflag))
                self.ret.append('')
                self.taglistcnt +=1
        return self.taglistcnt    

    def getTgtAttrs(self,attrstr):
        m = re.search('\(.+\)',attrstr)
        ret = {}
        if m is not None:
            matchstr = m.group()
            attrs = ''.join(list(matchstr))
            attrs = attrs[1:len(attrs)-1].split(',') #del the '(' and ')'
            for el in attrs:
                m = re.search('^@.+=',el)
                if m is not None:
                    str2 = ''.join(list(m.group()))
                    str2 = str2[1:len(str2)-1]
                    str3 = el[len(str2)+2:]
                    str3 = str(eval(str3))#trim the ' or "
                    ret.update({str2:str3})
        return ret
    
    def handle_decl(self, decl):
        HTMLParser.handle_decl(self, decl)            
                
    def handle_starttag(self, tag, attrs):
        HTMLParser.handle_starttag(self, tag, attrs)
        for el in self.tags:
            cnt = el[0]
            cur_cnt = 0
            for n in el[1]:
                if n[1]==False:#has not got the tag in list
                    if tag == n[0]:#get the target node
                        attrdict = dict(attrs)
                        bhit = True
                        for at in n[2]:
                            if(attrdict.has_key(at)):
                                if (n[2][at] == attrdict[at]):
                                    continue
                                else:
                                    bhit = False
                                    break
                            else:
                                bhit = False
                                break
                        n[1]=bhit
                        if bhit:cur_cnt+=1 #all the attrs are hitted 
                    break
                else:
                    cur_cnt+=1

            el[2][0] = (cur_cnt == cnt)#all target node start tag has been got,set flag to get data

            
                 
    def handle_data(self, data):
        HTMLParser.handle_data(self, data)
        for i in range(0,self.taglistcnt):
            if self.tags[i][2][0]:
                self.ret[i]+='%s'%data
                for el in self.tags[i][1]:#reset the get flag
                    el[1]=False
                self.tags[i][2][0] = False 
    def handle_endtag(self, tag):
        HTMLParser.handle_endtag(self, tag)

    def handle_startendtag(self, tag, attrs):
        HTMLParser.handle_startendtag(self, tag, attrs)
        
    def handle_comment(self, data):
        HTMLParser.handle_comment(self, data)

    def close(self):
        HTMLParser.close(self)

def test():
    
    data = u'''<li class="sk">
   
	<h1>
        
    </h1></li>
<li class='dn on' data-dn='todayT'>
<h1>14日 周二</h1>
<h2>白天</h2>
<big class="jpg80 d01"></big>
<p class="wea" title="多云">多云</p>
<p class="tem">
<span>20</span><i>°C</i>
</p>
<p class="win"><span class="N" title="北风">4-5级</span></p>
<p class="sunUp">
日出 05:34
</p>
<div class="slid"></div>
</li>
'''
    
    demo = HTMLProcess()
    demo.feed(u''';li(@class="dn on",@data-dn='todayT')/h1;/h2''',data)
    demo.close()
    for el in demo.ret:
        print el

if __name__ == '__main__':
    test()
