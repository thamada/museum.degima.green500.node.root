<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method = "text" />
<xsl:template match="apache/serveroptions" xml:space="preserve"> 
##
## Server-Pool Size Regulation (MPM specific)
## 

# prefork MPM
# StartServers: number of server processes to start
# MinSpareServers: minimum number of server processes which are kept spare
# MaxSpareServers: maximum number of server processes which are kept spare
# MaxClients: maximum number of server processes allowed to start
# MaxRequestsPerChild: maximum number of requests a server process serves
&lt;IfModule prefork.c>
StartServers <xsl:value-of select="StartServers/@VALUE"/>
MinSpareServers <xsl:value-of select="MinSpareServers/@VALUE"/>
MaxSpareServers <xsl:value-of select="MaxSpareServers/@VALUE"/>
MaxClients <xsl:value-of select="MaxClients/@VALUE"/>
MaxRequestsPerChild <xsl:value-of select="MaxRequestsPerChild/@VALUE"/>
&lt;/IfModule>

#
# Listen: Allows you to bind Apache to specific IP addresses and/or
# ports, in addition to the default. See also the &lt;VirtualHost>
# directive.
#
# Change this to Listen on specific IP addresses as shown below to 
# prevent Apache from glomming onto all bound IP addresses (0.0.0.0)
#
#Listen 12.34.56.78:80
<xsl:for-each select="listener/Listen">Listen <xsl:value-of select="@VALUE" />
</xsl:for-each>

#
# ServerAdmin: Your address, where problems with the server should be
# e-mailed.  This address appears on some server-generated pages, such
# as error documents.  e.g. admin@your-domain.com
#
ServerAdmin <xsl:value-of select="ServerAdmin/@VALUE"/>

#
# ServerName gives the name and port that the server uses to identify itself.
# This can often be determined automatically, but we recommend you specify
# it explicitly to prevent problems during startup.
#
# If this is not set to valid DNS name for your host, server-generated
# redirections will not work.  See also the UseCanonicalName directive.
#
# If your host doesn't have a registered DNS name, enter its IP address here.
# You will have to access it by its address anyway, and this will make 
# redirections work in a sensible way.
#
ServerName <xsl:value-of select="ServerName/@VALUE"/>

#
# The following directives define some format nicknames for use with
# a CustomLog directive (see below).
#
<xsl:for-each select="LogFormat">LogFormat "<xsl:value-of select="@VALUE" />"
</xsl:for-each>

#
# Customizable error responses come in three flavors:
# 1) plain text 2) local redirects 3) external redirects
#
# Some examples:
#ErrorDocument 500 "The server made a boo boo."
#ErrorDocument 404 /missing.html
#ErrorDocument 404 "/cgi-bin/missing_handler.pl"
#ErrorDocument 402 http://www.example.com/subscription_info.html
#
<xsl:for-each select="errordocuments/errordocument">ErrorDocument <xsl:value-of select="Code/@VALUE"/> "<xsl:value-of select="Document//@VALUE"/>" 
</xsl:for-each>

#
# Use name-based virtual hosting.
#
<xsl:for-each select="namevirtualhosts/NameVirtualHost">NameVirtualHost <xsl:value-of select="@VALUE" />
</xsl:for-each>

# Defaults for virtual hosts
<xsl:for-each select="SSLCertificateFile">SSLCertificateFile <xsl:value-of select="@VALUE" /></xsl:for-each>
<xsl:for-each select="SSLCertificateKeyFile">SSLCertificateKeyFile <xsl:value-of select="@VALUE" /></xsl:for-each>
<xsl:for-each select="SSLCertificateChainFile">SSLCertificateChainFile <xsl:value-of select="@VALUE" /></xsl:for-each>
<xsl:for-each select="SSLCACertificatePath">SSLCACertificatePath <xsl:value-of select="@VALUE" /></xsl:for-each>

# Logs
<xsl:for-each select="TransferLog">TransferLog <xsl:value-of select="@VALUE" /></xsl:for-each>

</xsl:template>

<xsl:template match="apache/virtualhosts" xml:space="preserve"> 
#
# Virtual hosts
#
<xsl:for-each select="virtualhost">
# Virtual host <xsl:value-of select="VHName/@VALUE" />
<xsl:text disable-output-escaping="yes">&lt;</xsl:text>VirtualHost <xsl:for-each select="Address"><xsl:value-of select="@VALUE" /></xsl:for-each>&gt;
 	<xsl:for-each select="DocumentRoot">DocumentRoot <xsl:value-of select="@VALUE" /> </xsl:for-each>
 	<xsl:for-each select="ErrorLog">ErrorLog <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="ServerAdmin">ServerAdmin <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="ServerName"><xsl:if test="not(@VALUE = '_default_')">ServerName <xsl:value-of select="@VALUE"/></xsl:if>
	</xsl:for-each>
<xsl:for-each select="serveraliases/ServerAlias">
        ServerAlias <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="ServerSignature">ServerSignature <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="TransferLog">TransferLog <xsl:value-of select="@VALUE" /></xsl:for-each>
	<xsl:for-each select="DirectoryIndex">DirectoryIndex <xsl:value-of select="@VALUE" /> </xsl:for-each>
	<xsl:for-each select="directories/directory">
	<xsl:text disable-output-escaping="yes">&lt;</xsl:text>Directory "<xsl:for-each select="Dir"><xsl:value-of select="@VALUE" /></xsl:for-each>"&gt;
		<xsl:for-each select="Options">Options <xsl:value-of select="@VALUE" />
		</xsl:for-each>
	 	<xsl:for-each select="AllowOverride">AllowOverride <xsl:value-of select="@VALUE" /></xsl:for-each>
 		<xsl:for-each select="Allow">Allow from <xsl:value-of select="@VALUE" /></xsl:for-each>
		<xsl:for-each select="Deny">Deny from <xsl:value-of select="@VALUE" /></xsl:for-each>
		<xsl:for-each select="Order">Order <xsl:value-of select="@VALUE" /></xsl:for-each>
	<xsl:text disable-output-escaping="yes">&lt;</xsl:text>/Directory&gt; 
	</xsl:for-each>
	<xsl:for-each select="errordocuments/errordocument">ErrorDocument <xsl:value-of select="Code/@VALUE"/> "<xsl:value-of select="Document/@VALUE"/>"
	</xsl:for-each>
 	<xsl:for-each select="SSLEngine">SSLEngine <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="SSLCertificateFile">SSLCertificateFile <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="SSLCertificateKeyFile">SSLCertificateKeyFile <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="SSLCertificateChainFile">SSLCertificateChainFile <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="SSLCACertificateFile">SSLCACertificateFile <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="SSLCACertificatePath">SSLCACertificatePath <xsl:value-of select="@VALUE" /></xsl:for-each>
        <xsl:for-each select="SSLOptions">SSLOptions <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="LogFormat">LogFormat "<xsl:value-of select="@VALUE" />"</xsl:for-each>
 	<xsl:for-each select="TransferLog">TransferLog <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="ErrorLog">ErrorLog <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="LogLevel">LogLevel <xsl:value-of select="@VALUE" /></xsl:for-each>
 	<xsl:for-each select="HostNameLookups">HostNameLookups <xsl:value-of select="@VALUE" /></xsl:for-each>
	<xsl:for-each select="environment/env[EnvType/@VALUE='pass']">PassEnv "<xsl:value-of select="Var/@VALUE" />"
	</xsl:for-each>
	<xsl:for-each select="environment/env[EnvType/@VALUE='unset']">UnsetEnv "<xsl:value-of select="Var/@VALUE" />"
	</xsl:for-each>
	<xsl:for-each select="environment/env[EnvType/@VALUE='set']">SetEnv "<xsl:value-of select="Var/@VALUE" />" "<xsl:value-of select="Value/@VALUE" />"
	</xsl:for-each>

<xsl:text disable-output-escaping="yes">&lt;</xsl:text>/VirtualHost&gt;
</xsl:for-each>
</xsl:template>

<xsl:template match="apache/directories" xml:space="preserve">
#
# Each directory to which Apache has access can be configured with respect
# to which services and features are allowed and/or disabled in that
# directory (and its subdirectories). 
#
# Note that from this point forward you must specifically allow
# particular features to be enabled - so if something's not working as
# you might expect, make sure that you have specifically enabled it
# below.
#
<xsl:for-each select="directory">
<xsl:text disable-output-escaping="yes">&lt;</xsl:text>Directory "<xsl:for-each select="Dir"><xsl:value-of select="@VALUE" /></xsl:for-each>"&gt;
        <xsl:for-each select="Options">Options <xsl:value-of select="@VALUE" />
        </xsl:for-each>
        <xsl:for-each select="AllowOverride">AllowOverride <xsl:value-of select="@VALUE" /></xsl:for-each>
        <xsl:for-each select="Allow">Allow from <xsl:value-of select="@VALUE" />
</xsl:for-each>
        <xsl:for-each select="Deny">Deny from <xsl:value-of select="@VALUE" />
</xsl:for-each>
        <xsl:for-each select="Order">Order <xsl:value-of select="@VALUE" /></xsl:for-each>
<xsl:text disable-output-escaping="yes">&lt;</xsl:text>/Directory&gt;
</xsl:for-each>
</xsl:template>

</xsl:stylesheet>
