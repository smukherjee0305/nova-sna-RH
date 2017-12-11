### Download the openstack database ###
### Read the xhtml, html pages and convert into text formats ###

#    Created on 2017
#    Satyam Mukherjee <satyam.mukherjee@gmail.com>
#    As a Red Hat Research Fellow in Research Center for Open Digital Innovation (RCODI), Purdue University
# 	 Principal Investigator: Prof Sabine Brunswicker, RCODI
"""Codes to download html pages from gitweb."""
""" Codes to download zip folders of packages at different commit times."""
"""

Provides:

 - checkurl()
 - download_status_q_merged_pages_html()
 - download_subject_pages_html()
 - download_status_pages()
 - download_gitweb_pages()
 - extract_from_gitweb_commit_lines_code_info()
 - download_codes_github()

References:
 - selenium: http://selenium-python.readthedocs.io/
 - BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
 - urllib2: https://docs.python.org/2/library/urllib2.html
"""

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
			file = open('../../Data/00_data_from_git/status_q_merged_pages_html/'+str(k)+'.html', 'w')
			print >> file, src_openstack.encode('ascii', 'ignore'),
			driver.quit()

			# Give it some time. Be nice to the server
			sleep(randint(20,30))


def download_subject_pages_html(outfile, error_file) :
	'''
	Call the html files and write them in a table format
	'''
	globhtmlfiles = glob.glob('../../Data/00_data_from_git/status_q_merged_pages_html/*.html'); globhtmlfiles.sort()

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

		# Give it some time. Be nice to the server
		sleep(randint(25,35))

		src_openstack = driver.page_source

		file = open('../../Data/00_data_from_git/subject_pages_html/'+str(k)+'.html', 'w')
		print >> file, src_openstack.encode('ascii', 'ignore'),
		driver.quit()

		# Give it some time. Be nice to the server
		sleep(randint(20,30))



def download_gitweb_pages(n1, n2) :

	'''
	From the status pages get the gitweb href 
	and download each parent, committ gitweb pages 
	'''
	globhtmlfiles = glob.glob('../../Data/00_data_from_git/subject_pages_html/*.html'); globhtmlfiles.sort()

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
			file_c = '../../Data/00_data_from_git/gitweb_links_html_commits/'+str(indc)+'.xhtml'
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
			file_p = '../../Data/00_data_from_git/gitweb_links_html_commits/'+str(indp)+'.xhtml'
			filep = open(file_p, 'w')
			print >> filep, src_openstack_p.encode('ascii','ignore'),
			filep.close()
			driverp.quit()

			# Give it some time. Be nice to the server
			sleep(randint(5,25))

		except IndexError,e :
			continue
##############################################################################################################################
######      Get the code-hrefs links for every gitweb pages along with author name and commit lines in each code       #######
##############################################################################################################################

def extract_from_gitweb_commit_lines_code_info(f1, f2) :
    from bs4 import BeautifulSoup
    import glob

    globhtmlfiles = glob.glob('../../Data/00_data_from_git/gitweb_links_html_commits/*.xhtml'); globhtmlfiles.sort()
    
    #outf = open(str(f2), 'w'); 
    #print >> outf, 'code_init|code_line_start_range|code_final|code_line_end_range|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    #print >> outf, 'code_text|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    
    outf1 = open(str(f1), 'w'); outf2 = open(str(f2), 'w') 
    print >> outf1, 'lines_of_code_added|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'
    print >> outf2, 'lines_of_code_removed|code_init|code_final|commit_author|author_email|time_commit_author|commit_committer|committer_email|time_commit_committer'

    for htmlsource in globhtmlfiles :

        html_read = open(htmlsource,'r')
        page_source = BeautifulSoup(html_read, "html.parser")
        page_source.prettify

        try :
            list_source_codes = page_source('div',{"class":"diff chunk_header"}) 
            
            time_commit_author = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[0].text
            time_commit_committer = page_source('table', {'class':'object_header'})[0]('span',{'class':'datetime'})[1].text
        
            commit_author = page_source('tr')[0]('a')[0].text.encode('ascii', 'ignore')
            commit_committer = page_source('tr')[2]('a')[0].text.encode('ascii', 'ignore')
            
            commit_author_email = page_source('tr')[0]('a')[1].text
            commit_committer_email = page_source('tr')[2]('a')[1].text

            for k in page_source('div',{'class':'patch'}) :
 
                code_init = k('div',{"class":"diff chunk_header"})[0]('a')[0]['href']
                code_final = k('div',{"class":"diff chunk_header"})[0]('a')[1]['href']
                
                code_text_str = []; code_text_str_add = []; code_text_str_rem = []

                for s in k('div',{'class':'diff add'}) :
                    #if "index" not in str(s.text.encode('ascii', 'ignore')) and "diff --git" not in str(s.text.encode('ascii', 'ignore')) and "@@" not in str(s.text.encode('ascii', 'ignore')) and "---" not in str(s.text.encode('ascii', 'ignore')) and "+++" not in str(s.text.encode('ascii', 'ignore')):
                        if len(str(s.text.encode('ascii', 'ignore'))) > 0 :
                            code_text_str_add.append(str(s.text.encode('ascii', 'ignore')))

                #res_code_txt = " ".join(code_text_str)       
                print >> outf1, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( len(code_text_str_add), code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )


                for s in k('div',{'class':'diff rem'}) :
                    #if "index" not in str(s.text.encode('ascii', 'ignore')) and "diff --git" not in str(s.text.encode('ascii', 'ignore')) and "@@" not in str(s.text.encode('ascii', 'ignore')) and "---" not in str(s.text.encode('ascii', 'ignore')) and "+++" not in str(s.text.encode('ascii', 'ignore')):
                        if len(str(s.text.encode('ascii', 'ignore'))) > 0 :
                            code_text_str_rem.append(str(s.text.encode('ascii', 'ignore')))
      
                print >> outf2, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( len(code_text_str_rem), code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )


                #print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( res_code_txt, code_init, code_final, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )

            #for k in list_source_codes:
            #    code_init = k('a')[0]['href']
            #    code_line_start_range = k('a')[0].text
            #    code_final = k('a')[1]['href']
            #    code_line_end_range = k('a')[1].text
            #    print code_init, code_line_start_range, k, '\n'
                #print >> outf, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' % ( code_init, code_line_start_range, code_final, code_line_end_range, commit_author, commit_author_email, time_commit_author, commit_committer, commit_committer_email, time_commit_committer )

        except IndexError,e :
            continue


########################################################################
######  Now download the zip files from Nova archives website #######
########################################################################


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

	for commitid in commitlist : 
				print commitid
				try :
					## get the url for the zip file
					base_url = "https://github.com/openstack/nova/archive/"+str(commitid)+".zip"

					## request the file
					res = urllib2.urlopen(urllib2.Request(str(base_url)))
				
					## save the zip file
					wext = open('../../Data/00_data_from_git/github_archives/'+'nova-'+str(commitid)+".zip",'w')
					wext.write(res.read())
					wext.close()
				except urllib2.HTTPError, e:
					print e.code
					print e.msg

					continue
				# Give it some time. Be nice to the server
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

	f1 = sys.argv[1]
	download_codes_github(f1)