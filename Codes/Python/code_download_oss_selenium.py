### Download the openstack database ###

import sys, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urlparse import urlparse
from time import sleep
from random import randint
from  bs4 import BeautifulSoup
import urllib2, glob


in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()


def checkurl(url):
 	### check if the url exists or not
  try:
	f = urllib2.urlopen(urllib2.Request(url))
	deadLinkFound = False
  except:
	deadLinkFound = True

  return deadLinkFound

def download_status_q_merged_pages_html(s1, s2, bins) :

	### Code to download the merged pages from review.openstack.org

	for k in range(int(s1), int(s2)+1, int(bins)) :
			print k
			openstackurl = "https://review.openstack.org/#/q/status:merged,"+str(k)
			#openstackurl = "https://review.openstack.org/#/c/"+str(k)+"/"
		
			## load the webpage
			driver = webdriver.Firefox()
			driver.get(openstackurl)

			## wait for loading and time to save the html page
			sleep(randint(25,35))

			## get the source
			src_openstack = driver.page_source

			## save the html file
			file = open('../../../NewData_html/status_q_merged_pages_html/'+str(k)+'.html', 'w')
			print >> file, src_openstack.encode('ascii', 'ignore'),
			driver.quit()

			sleep(randint(20,30))

def download_status_new_html(f1) :
	### In this code I download those pages
	# which didn't get save due to slow Internet #

	data1 = open(f1, 'r') 
	for line in data1.readlines() :
			line = line.strip().split()
			k = line[10].split('./')[1].split('.html')[0]
			print k
			openstackurl = "https://review.openstack.org/#/q/status:merged,"+str(k)

			driver = webdriver.Firefox()
			driver.get(openstackurl)

			sleep(randint(25,35))

			src_openstack = driver.page_source

			file = open('../../../NewData_html/status_q_merged_pages_html/'+str(k)+'.html', 'w')
			print >> file, src_openstack.encode('ascii', 'ignore'),
			driver.quit()

			sleep(randint(20,30))

def download_subject_pages_html(outfile, error_file) :
	'''
	Call the html files and write them in a table format
	'''
	globhtmlfiles = glob.glob('../../../NewData_html/status_q_merged_pages_html/*.html'); globhtmlfiles.sort()

	f2 = open(outfile,'w')
	print >> f2, 'subject_href|subject_text|owner_href|owner_text|project_href|project_text|branch_href|branch_text'

	e2 = open(error_file,'w')

	for htmlsource in globhtmlfiles :
		print htmlsource
		try :
			try :
				html_read = open(htmlsource,'r')
				page_source = BeautifulSoup(html_read)

				list_source_pages = page_source('a',{'class':'gwt-InlineHyperlink'}) 
				data_chunks = [list_source_pages[x:x+5] for x in range(0, len(list_source_pages), 5)]

				for d in data_chunks :
					print >> f2, '%s|%s|%s|%s|%s|%s|%s|%s' % ( d[0]['href'], d[1].text, d[2]['href'], d[2]['title'], d[3]['href'], d[3].text, d[4]['href'], d[4].text )
			except KeyError,e :
				print >> e2, e
		except IndexError,e :
			continue

def download_status_pages(f_subject_file, p, m) :
	'''
	From the text file get the href and for each 
	branch package get the status pages
	'''
	fread = open(f_subject_file, 'r')
	n = int(m)
	for line in fread.readlines()[int(p)+1:n+1] :
		line = line.strip().split('|')
		statushref = str(line[0])

		base_url_status = statushref
		print base_url_status

		k = statushref.split('/')[-1]

		driver = webdriver.Firefox()
		driver.get(base_url_status)

		sleep(randint(25,35))

		src_openstack = driver.page_source

		file = open('../../../NewData_html/Nova/subject_pages_html/'+str(k)+'.html', 'w')
		print >> file, src_openstack.encode('ascii', 'ignore'),
		driver.quit()

		sleep(randint(20,30))



def download_gitweb_pages(n1, n2) :

	'''
	From the status pages get the gitweb href 
	and download each parent, committ gitweb pages 
	'''
	globhtmlfiles = glob.glob('../../../NewData_html/Nova/subject_pages_html/*.html'); globhtmlfiles.sort()

	for htmlsource in globhtmlfiles[int(n1):int(n2)] :

		html_read = open(htmlsource,'r')
		page_source = BeautifulSoup(html_read)

		list_source_committ = page_source('div',{'class':'com-google-gerrit-client-change-CommitBox_BinderImpl_GenCss_style-webLinkPanel'}) 
		list_source_parent = page_source('div',{'class':'com-google-gerrit-client-change-CommitBox_BinderImpl_GenCss_style-parentWebLink'}) 

		try :
			committ_href = list_source_committ[0]('a')[0]['href']	
			parent_href = list_source_parent[0]('a')[0]['href']

			print committ_href, parent_href


			pgnum = htmlsource.split('/')[6][:-5]

			indc = pgnum+'__'+committ_href.split(';h=')[1]; indp = pgnum+'__'+parent_href.split(';h=')[1]

			### download commit gitweb pages
			base_url_commit = "https://review.openstack.org/"+str(committ_href)
			
			driverc = webdriver.Firefox()
			driverc.get(base_url_commit)
			sleep(randint(20,30))

			src_openstack_c = driverc.page_source
			file_c = '../../../NewData_html/Nova/gitweb_links_html/commits/'+str(indc)+'.xhtml'
			filec = open(file_c, 'w')
			print >> filec, src_openstack_c.encode('ascii','ignore'),
			filec.close()
			driverc.quit()

			sleep(randint(5,25)) ## wait be patient


			### download parent gitweb pages
			base_url_parent = "https://review.openstack.org/"+str(parent_href)
			driverp = webdriver.Firefox()
			driverp.get(base_url_parent)
			sleep(randint(20,30))

			src_openstack_p = driverp.page_source
			file_p = '../../../NewData_html/Nova/gitweb_links_html/parents/'+str(indp)+'.xhtml'
			filep = open(file_p, 'w')
			print >> filep, src_openstack_p.encode('ascii','ignore'),
			filep.close()
			driverp.quit()


			#xc = urllib2.urlopen(str(base_url_commit))
			#xml_str_c = xc.read()

			#xp = urllib2.urlopen(str(base_url_parent))
			#xml_str_p = xp.read()


			sleep(randint(5,25))

		except IndexError,e :
			continue

def download_codes_raw(n1, n2) :
	'''
	From the gitweb pages get the actual codes
	'''
	#outf = open(str(f2), 'w'); 
	#print >> outf, 'code_git_link|code_text|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'

	globhtmlfiles = glob.glob('../../../NewData_html/Nova/gitweb_links_html/commits/*.xhtml')
	globhtmlfiles.sort()

	for htmlsource in globhtmlfiles[int(n1):int(n2)] :
		
		print htmlsource

		html_read = open(htmlsource,'r')
		page_source = BeautifulSoup(html_read, "html.parser")
		page_source.prettify
		list_source_codes = page_source('table',{"class":"diff_tree"}) 

		for k in list_source_codes[0]('tr') :
			code_git_link = k('a',{'class':'list'})[0]['href']


			code_text =  k('a',{'class':'list'})[0].text
			codelink = "https://review.openstack.org/"+str(code_git_link)
			
			code_git_link_split = code_git_link.split(';')
			


			code_blob_plain = code_git_link_split[0]+';'+'a=blob_plain'+';'+code_git_link_split[2]+';'+code_git_link_split[4]


			bloblink = "https://review.openstack.org/"+str(code_blob_plain)


			res = (urllib2.urlopen(urllib2.Request(str(bloblink))))
	
			filename = code_git_link_split[4]+'__'+code_git_link_split[2].replace('/','__').replace('=','__')
			wext = open('../../../NewData_html/Nova/full_codes/blob_plain/'+str(filename),'w')
			wext.write(res.read())
			wext.close()


			### get the html pages where the codes are mentioned ###
			#x = urllib2.urlopen(codelink)
			#xhtml_str = x.read()
			
			#outname = code_git_link_split[3]+'__'+code_git_link_split[4]

			#outf = open('../../../NewData_html/Nova/full_codes/html_pages/%s.html'%outname,'w')
			#print >> outf, xhtml_str,

			sleep(randint(10,20))

def download_codes_github(f1) :

#No luck with the gitweb_codes_raw function. Would take ages for their downloading
#Here is a shortcut. I saved the latest github clone of nova as of April 18 2016
#Then got the log file of all old gits using the command "git log > filename.txt"
#I use this to get commit id and then subsequently use the download zip options
##

	fread = open(f1, 'r')
	commitlist = []
	for line in fread.readlines() :
		line = line.strip()
		if " commit " not in line :
			if "commit " in line :
				
				line = line.split(' ')
				commitid = line[1]
				commitlist.append(commitid)

	for commitid in commitlist[40000:] : 
				print commitid
				try :
					## get the url for the zip file
					base_url = "https://github.com/openstack/nova/archive/"+str(commitid)+".zip"

					## request the file
					res = urllib2.urlopen(urllib2.Request(str(base_url)))
				
					## save the zip file
					wext = open('../../../NewData_html/Nova/github_archives/'+'nova-'+str(commitid)+".zip",'w')
					wext.write(res.read())
					wext.close()
				except urllib2.HTTPError, e:
					print e.code
					print e.msg

					continue

				sleep(randint(15,30))


if __name__ == "__main__" :

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#download_status_q_merged_pages_html(f1, f2, f3)

	#f1 = sys.argv[1]
	#download_status_new_html(f1)

	#f1 = sys.argv[1]; f2 = sys.argv[2]
	#download_subject_pages_html(f1, f2)

	#f1 = sys.argv[1]; f2 = sys.argv[2]; f3 = sys.argv[3]
	#download_status_pages(f1, f2, f3)
	
	#f1 = sys.argv[1]; f2 = sys.argv[2]
	#download_gitweb_pages(f1, f2)
	
	#f1 = sys.argv[1]; f2 = sys.argv[2]
	#download_codes_raw(f1, f2)

	f1 = sys.argv[1]
	download_codes_github(f1)