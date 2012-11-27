import sys
from pyftpdlib import ftpserver
import os
import grp
import pwd
import lockfile
import daemon

"""
pyftpdlib permissions

Read permissions:
"e" = change directory (CWD command)
"l" = list files (LIST, NLST, STAT, MLSD, MLST commands)
"r" = retrieve file from the server (RETR command)
Write permissions
"a" = append data to an existing file (APPE command)
"d" = delete file or directory (DELE, RMD commands)
"f" = rename file or directory (RNFR, RNTO commands)
"m" = create directory (MKD command)
"w" = store a file to the server (STOR, STOU commands)
"""


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

os.environ["DJANGO_SETTINGS_MODULE"] = "atrinsic.settings"

from atrinsic.util.imports import *
from atrinsic.base.models import Organization

DAEMON_LOG = "/var/log/aqftpd.log"
DAEMON_WORK_DIR = "/mnt/nfs/adquotient/ftproot/"
DAEMON_PID = "/var/run/aqftpd.pid"
DAEMON_USER = "80concepts"
DAEMON_GROUP = "80concepts"

def get_org(username):
	organizations = Organization.objects.filter(company_name=username)
	if organizations.count() == 0:
		if username[0:3] == 'ATR':
			organizations = Organization.objects.filter(id=username.strip('ATR'))
			
	if organizations.count() == 0:
		return None
		
	return organizations[0]

class AQAuthorizer(ftpserver.DummyAuthorizer):	
	def validate_authentication(self, username, password):
		org = get_org(username)
		if org == None:
			return False
		
		for up in org.userprofile_set.all():
			if up.user.check_password(password):
			#	self.add_user(self, username, password, os.path.join(settings.LOCALFTP_ROOT,str(org.id)), perm='elrdw',msg_login="Login successful.", msg_quit="Goodbye."):	
				return True
		return False
		
	def get_home_dir(self, username):
		org = get_org(username)
		if org == None:
			return None
			
		if int(org.id) == 853:
			output = settings.LOCALFTP_ROOT
		else:
			output = os.path.join(settings.LOCALFTP_ROOT,str(org.id))
			if os.path.exists(output) == False:
				os.mkdir(output)
		return output

	def has_user(self, username):
		return True
	
	def r_perm(self, username, obj=None):
		return True

	def w_perm(self, username, obj=None):
		return True

	def get_perms(self, username):
		# TODO query user tables for perms
		return ("e","l","r","a","d","f","m","w")
				
	def has_perm(self, username, perm, path=None):
		if perm in ["l","r","d","w","e","m","f"]:
			return True
		return False

	def get_msg_login(self, username):
		return "Hello %s" % username

	def get_msg_quit(self, username):
		return "Goodbye %s" % username	


fh_log = open(DAEMON_LOG, "a", 0)

d_context = daemon.DaemonContext(
					working_directory=DAEMON_WORK_DIR,
					stdout=fh_log, 
					stderr=fh_log
			)

d_context.open()
			
auth = AQAuthorizer()

ftp_handler = ftpserver.FTPHandler
ftp_handler.authorizer = auth
ftp_handler.banner = "AQ FTPD 0.1"
ftp_handler.passive_ports = range(50000,60000)

address = ("0.0.0.0", settings.FTP_PORT)

ftpd = ftpserver.FTPServer(address, ftp_handler)
os.setegid(grp.getgrnam(DAEMON_GROUP).gr_gid)
os.seteuid(pwd.getpwnam(DAEMON_USER).pw_uid)
ftpd.serve_forever()
