#!/usr/bin/env python
#-*- coding: UTF-8 -*-
'''Tools KeyWord for RF'''

from robot.api import logger
import re

__version__ = 'dcn.1.0.0'
__author__ = 'liuleic'
__copyright__ = 'Copyright 2014, DigitalChina Network'
__license__ = 'Apache License, Version 2.0'
__mail__ = 'liuleic@digitalchina.com'


class Tools(object):
    ''''''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
    def __init__(self):
        pass

    def incr_mac(self,mac,step=1,mask=6):
        '''
        KeyWord: Incr Mac

        args: 
            - mac:mac地址 如'00-01-01-01-01-01'
            - step:增长数量  默认1
            - mask:掩码，从掩码位置增长，默认6

        return: 增长后的mac地址

        examples:
        | Incr Mac | 00-01-01-01-01-01 | #结果00-01-01-01-01-02 |
        | Incr Mac | 00-01-01-01-01-01 | step=${2} | #结果00-01-01-01-01-03 |           
        | Incr Mac | 00-01-01-01-01-01 | mask=${3} | #结果00-01-02-01-01-01 |
        '''
        if mask > 6:
            logger.info('mask error: should less than 6')
            return
        maclist = mac.split('-')
        if len(maclist) != 6:
            logger.info('mac length error: should equal to 6')
            #print 'mac length error'
            return
        snum = ''
        for i in range(mask):
            snum = snum + maclist[i]
        d=int(snum,16)
        dnum = d + step
        l = '%0'+str(mask * 2)+'X'
        ss = l%dnum
        for i in range(mask):
            maclist[i] = ss[i*2:i*2+2]
        return '-'.join(maclist)    
    

    def incr_ip(self,ip,step=1,mask=32):
        '''
        KeyWord: Incr Ip

        args:
            - ip:ip地址 如'10.1.1.1'
            - step:增长数量  默认1
            - mask:掩码，从掩码位置增长，默认32,即默认从最后一位开始增长

        return: 增长后的ip地址

        examples:
        | Incr Ip | 10.1.1.1 | #结果10.1.1.2 |
        | Incr Ip | 10.1.1.1 | step=${2}  | #结果10.1.1.3 |            
        | Incr Ip | 10.1.1.1 | mask=${24} | #结果10.1.2.1 |
        '''
        iplist = ip.split('.')
        if len(iplist) != 4:
            logger.info('ip format error')
            #print 'ip format error'
            return
        shex = ''
        for svalue in iplist:
            h = int(svalue)
            if h > 0xff:
                logger.info('ip error')
                #print 'ip error'
                return
            shex += '%02X'%h
        mv = 32 - mask
        inc = int(shex,16) >> mv
        gv = inc + step
        mod = int(shex,16) & (2 ** mv - 1)
        resv = ((gv << mv) + mod) & (2 ** 32 - 1)
        reslist = [] 
        for i in range(4):
            reslist.insert(0,str(resv >> (i * 8) & (2 ** 8 - 1)))
        return '.'.join(reslist)


    def incr_ipv6(self,ipv6,step=1,mask=128):
        '''
        KeyWord: Incr Ipv6

        args: 
            - ipv6:ip地址 如'2000::1'
            - step:增长数量  默认1
            - mask:掩码，从掩码位置增长，默认128,即默认从最后一位开始增长

        return: 增长后的ipv6地址

        examples:
        | Incr Ipv6 | 2000::1 | #结果2000::2 |
        | Incr Ipv6 | 2000::1 | step=${2}  | #结果2000::3 |          
        | Incr Ipv6 | 2000::1 | mask=${64} | #结果2000::1:0:0:0:1 |
        '''
        ipv6list = ipv6.split(':')
        if len(ipv6list) == 1 or len(ipv6list) >8 :
            logger.info('ipv6 format error')
            #print 'ipv6 format error'
            return
        shex = ''
        for i in range(len(ipv6list)):
            if ipv6list[i] == '':
                for j in range(8-len(ipv6list)+1):
                    shex += '0000'
            else:
                h = int(ipv6list[i],16)
                if h > 0xffff:
                    logger.info('ipv6 error')
                    #print 'ipv6 error'
                    return
                shex += '%04X'%h
        mv = 128 - mask
        inc = int(shex,16) >> mv
        gv = inc + step
        mod = int(shex,16) & (2 ** mv - 1)
        resv = ((gv << mv) + mod) & (2 ** 128 - 1)
        reslist = []
        for i in range(8):
            #reslist.insert(0,str(resv >> (i * 16) & (2 ** 16 - 1)))
            reslist.insert(0,'%X'%(resv >> (i * 16) & (2 ** 16 - 1)))
        shortres = []
        shorttmp = []
        shend = 0
        for i in range(8):
            if reslist[i] == '0' and shend == 0:
                shorttmp.append(reslist[i])
            elif reslist[i] != '0' and shend == 0:
                if len(shorttmp) > 1:
                    shortres.append('')
                    shortres.append(reslist[i])
                    shend = 1
                elif len(shorttmp) == 1:
                    shortres.append('0')
                    shortres.append(reslist[i])
                    shorttmp = []
                else:
                    shortres.append(reslist[i])
            else:
                shortres.append(reslist[i])
        
        return ':'.join(shortres)


    def get_value_from_string(self,string,regexp):
        '''
        KeyWord: Get Value From String, 从匹配字符串中按照正则表达式找出子串
            
        args:
            - string: 匹配字符串
            - regexp: 正则表达式
            
        return:
            - None，未匹配成功
            - (group(1),group(2),...),匹配成功后的子串元组

        examples:
            | Get Value From String | $output | '.*?,\\s+address is (.*?),\s+' |
        '''
        if not string:
            return None
        if not regexp:
            logger.info('regexp is None,please check')
            return None
        research = re.compile(regexp)
        m = research.search(string)
        if m:
            g = m.groups()
            if len(g) == 1:
                return g[0]
            return g
        else:
            logger.info('not search %r in %s',(regexp,string))
            return None

    def find_all_from_string(self,string,regexp):
        '''
        KeyWord: Find All From String, 从匹配字符串中找出所有符合正则表达式的子串
            
        args:
            - string: 匹配字符串
            - regexp: 正则表达式
            
        return:
            - None，未匹配成功
            - (group(1),group(2),...),所有的子串元组

        examples:
            | Find All From String | $output | '.*?,\\s+address is (.*?),\s+' |
        '''
        if not regexp:
            logger.info('regexp is None,please check')
            return None
        research = re.compile(regexp)
        m = research.findall(string)
        if m:
            return m
        else:
            logger.info('not find %r in %s',(regexp,string))
            return None

    def is_match_from_string(self,string,regexp):
        '''
        KeyWord: Is Match From String, 正则表达式是否可以匹配

        args:
            - string: 匹配字符串
            - regexp: 正则表达式

        return:
            - False，未匹配成功
            - True,匹配成功

        examples:
            | Is Match From String | $output | '.*?,\\s+address is (.*?),\s+' |
        '''
        if not regexp:
            logger.info('regexp is None,please check')
            return None
        research = re.compile(regexp)
        m = research.search(string)
        if m:
            logger.info('match %r in %s',(regexp,string))
            return True
        else:
            logger.info('not match %r in %s',(regexp,string))
            return False

    def convert_macaddress_format(self,macstr,splitstr=':',joinstr='-',lower=True):
        '''
        '''
        if not hasattr(macstr,'split'):
            raise AssertionError('macstr should be str')
        macstr = macstr.strip()
        macstrList = macstr.split(splitstr)
        retMac = joinstr.join(macstrList)
        if lower:
            return retMac.lower()
        else:
            return retMac.upper()

    def is_none(self,robotVar):
        '''
        '''
        return False if robotVar else True

    def find_all_num_from_string(self,string,regexp):
        '''
        KeyWord: Find All From String, 从匹配字符串中找出所有符合正则表达式的子串的数目
            
        args:
            - string: 匹配字符串
            - regexp: 正则表达式
            
        return:
            - 符合匹配的数字

        examples:
            | Find All Num From String | $output | '.*?,\\s+address is (.*?),\s+' |
        '''
        if not regexp:
            logger.info('regexp is None,please check')
            return 0
        research = re.compile(regexp)
        m = research.findall(string)
        if m:
            return len(m)
        else:
            logger.info('not find %r in %s',(regexp,string))
            return 0
