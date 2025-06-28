# """
# Turn anything places in this folder into an MCP resource
# """
# from mcp.types import Resource

# class Resource(BaseModel):
#     """A known resource that the server is capable of reading."""

#     uri: Annotated[AnyUrl, UrlConstraints(host_required=False)]
#     """The URI of this resource."""
#     name: str
#     """A human-readable name for this resource."""
#     description: str | None = None
#     """A description of what this resource represents."""
#     mimeType: str | None = None
#     """The MIME type of this resource, if known."""
#     size: int | None = None
#     """
#     The size of the raw resource content, in bytes (i.e., before base64 encoding
#     or any tokenization), if known.

#     This can be used by Hosts to display file sizes and estimate context window usage.
#     """
#     annotations: Annotations | None = None
#     model_config = ConfigDict(extra="allow")


# def match_resource_to_resource_type(uri: str) -> list[Resource]:
#     """
#     source: https://modelcontextprotocol.io/docs/concepts/resources , 6-25-2025

#     Resources represent any kind of data that an MCP server wants to make available to clients.
#     This can include:
#         - File contents
#         - Database records
#         - API responses
#         - Live system data
#         - Screenshots and images
#         - Log files
#         - And more

#     Resources are identified using URIs that follow this format:
#     [protocol]://[host]/[path]

#     For example:
#         - file:///path/to/file.txt
#         - postgres://user:password@localhost:5432/mydatabase/table_name
#         - screen://localhost:8080/display1

#     Resources can contain two types of content:

#     Text resources contain UTF-8 encoded text data. These are suitable for:
#         - Source code
#         - Configuration files
#         - Log files
#         - JSON/XML data
#         - Plain text

#     Binary resources contain raw binary data encoded in base64. These are suitable for:
#         - Images
#         - PDFs
#         - Audio files
#         - Video files
#         - Other non-text formats

#     Args:
#         path (str): The URI to the resource. Can be an actual path, URL, URI, etc. Anything that points to a specific

#     Returns:


#     """
#     pass


# def guess_what_this_resource_is(uri: str) -> str:
#     """
#     Guess what this resource is based on its URI.

#     This function attempts to determine the type of resource based on the URI scheme and path.
#     It returns a description of the resource type.

#     Args:
#         uri (str): The URI of the resource.

#     Returns:
#         Resource: A Resource object with guessed metadata.
    
#     Example:
#         >>> # 
#         >>> guess_what_this_resource_is("file:///path/to/file.txt")
#         'Text file containing a small quantity of text.'
#     """
#     # Parse the URI protocol. [protocol]://[host]/[path]
#     protocol = uri.split("://")[0]
#     host = uri.split("://")[1].split("/")[0]
#     path = "/".join(uri.split("://")[1].split("/")[1:])

#     heuristic_dict = {
#         "protocol": _protocol_heuristic_checks(protocol),
#         "host": _host_heuristic_checks(host),
#         "path": path,
#     }

# def _host_heuristic_checks(host: str) -> str:
#     """
#     Provides heuristic information about hosts based on their names.

#     This function looks up host information from a predefined dictionary of common hosts.
#     It returns a description of the host or "Unknown host '{host}'." if no information is found.

#     Args:
#         host (str): The host name to look up (e.g., 'localhost', 'example.com')

#     Returns:
#         str: A descriptive string explaining what the host is used for, or 
#              "Unknown host '{host}'." if no information is found
#     """
#     # Predefined dictionary of common hosts and their descriptions
#     host_descriptions = {
#         "localhost": "The local machine, often used for development and testing.",
#         "127.0.0.1": "IPv4 loopback address, refers to the local machine.",
#         "::1": "IPv6 loopback address, refers to the local machine.",
#         "0.0.0.0": "All available network interfaces on the local machine.",
#         "example.com": "A placeholder domain often used in documentation.",
#         "github.com": "A platform for version control and collaboration, primarily for code repositories.",
#         "gitlab.com": "A web-based DevOps lifecycle tool that provides Git repository management.",
#         "bitbucket.org": "A Git-based source code repository hosting service.",
#         "google.com": "The main domain for Google services, including search and various web applications.",
#         "youtube.com": "Video sharing platform owned by Google.",
#         "gmail.com": "Google's email service.",
#         "stackoverflow.com": "A question and answer site for programmers and developers.",
#         "reddit.com": "A social news aggregation and discussion website.",
#         "wikipedia.org": "A free online encyclopedia with articles on various topics.",
#         "amazon.com": "E-commerce platform and cloud computing services provider.",
#         "aws.amazon.com": "Amazon Web Services, cloud computing platform.",
#         "microsoft.com": "Microsoft's main website for products and services.",
#         "azure.microsoft.com": "Microsoft's cloud computing platform.",
#         "office.com": "Microsoft Office online applications and services.",
#         "apple.com": "Apple Inc.'s main website for products and services.",
#         "facebook.com": "Social networking platform owned by Meta.",
#         "instagram.com": "Photo and video sharing social networking service.",
#         "twitter.com": "Social media platform for microblogging and social networking.",
#         "x.com": "Rebranded Twitter social media platform.",
#         "linkedin.com": "Professional networking platform.",
#         "discord.com": "Voice, video, and text communication service for communities.",
#         "slack.com": "Business communication platform for teams.",
#         "zoom.us": "Video conferencing and communication platform.",
#         "dropbox.com": "Cloud storage service for file synchronization and sharing.",
#         "onedrive.live.com": "Microsoft's cloud storage service.",
#         "drive.google.com": "Google Drive cloud storage service.",
#         "netflix.com": "Streaming service for movies and TV shows.",
#         "spotify.com": "Music streaming platform.",
#         "twitch.tv": "Live streaming platform primarily for gaming content.",
#         "paypal.com": "Online payment system and money transfer service.",
#         "stripe.com": "Online payment processing platform for businesses.",
#         "shopify.com": "E-commerce platform for online stores and retail point-of-sale systems.",
#         "wordpress.com": "Website building and hosting platform.",
#         "medium.com": "Online publishing platform for articles and blogs.",
#         "hackernews.com": "Social news website focusing on computer science and entrepreneurship.",
#         "docker.com": "Containerization platform for application deployment.",
#         "kubernetes.io": "Container orchestration platform.",
#         "jenkins.io": "Open-source automation server for CI/CD.",
#         "jira.atlassian.com": "Issue tracking and project management tool.",
#         "confluence.atlassian.com": "Collaboration wiki platform.",
#         "notion.so": "All-in-one workspace for notes, tasks, and collaboration.",
#         "figma.com": "Collaborative design and prototyping tool.",
#         "canva.com": "Graphic design platform for creating visual content.",
#         "unsplash.com": "Photography platform providing free high-resolution images.",
#         "pexels.com": "Free stock photo and video platform.",
#         "api.github.com": "GitHub's REST API for programmatic access to repositories.",
#         "api.twitter.com": "Twitter's API for accessing platform data and functionality.",
#         "jsonplaceholder.typicode.com": "Fake online REST API for testing and prototyping.",
#         "httpbin.org": "HTTP request and response testing service.",
#         "postman-echo.com": "Testing service that echoes back request data.",
#         "mockapi.io": "Mock API service for testing and development.",
#         "reqres.in": "Test API with real response codes and data.",
#         "cdn.jsdelivr.net": "Free CDN for open source projects.",
#         "unpkg.com": "Fast, global content delivery network for npm packages.",
#         "fonts.googleapis.com": "Google Fonts API for web font delivery.",
#         "fonts.gstatic.com": "Google's font hosting service.",
#         "cdnjs.cloudflare.com": "Free and open source CDN service.",
#     }
#     return host_descriptions.get(host, f"Unknown host '{host}'.")


# def _protocol_heuristic_checks(protocol: str) -> str:
#     """
#     Provides heuristic information about URI schemes and protocols.

#     This function looks up protocol information from multiple sources in order of precedence:
#     1. Official IANA URI schemes from a CSV file (uri-schemes-1.csv)
#     2. Unofficial schemes from a predefined dictionary from Wikipedia
#     3. Misc. common protocols and services from a comprehensive "hail mary" dictionary

#     Args:
#         protocol (str): The protocol/URI scheme to look up (e.g., 'http', 'ftp', 'ssh')

#     Returns:
#         str: A descriptive string explaining what the protocol is used for, or 
#              "Unknown protocol '{protocol}'." if no information is found

#     Note:
#         - CSV source: https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml (6-25-2025)
#         - Unofficial schemes source: https://en.wikipedia.org/wiki/List_of_URI_schemes (6-25-2025)
#         - The function requires a CSV file named 'uri-schemes-1.csv' in the same directory
#         - Includes extensive coverage of database, messaging, storage, version control, 
#           browser, gaming, communication, and networking protocols
#     """
#     from pathlib import Path
#     import csv
#     # load the CSV file containing protocol heuristics
#     this_dir = Path(__file__).parent
#     csv_file = this_dir / "uri-schemes-1.csv"
#     with open(csv_file, 'r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             if row['URI Scheme'] == protocol:
#                 return row['heuristic']

#     # If the protocol is not found in the CSV, check for the unofficial ones.
#     unofficial_schemes = {
#         "admin": "URL scheme in the GNOME desktop environment to access file(s) with administrative permissions with GUI applications in a safer way, instead of sudo, gksu & gksudo, which may be considered insecure",
#         "app": "URL scheme can be used by packaged applications to obtain resources that are inside a container",
#         "freeplane": "Open a Freemind/Freeplane .mm file in the locally installed Freeplane application and optionally highlight a node in the opened mindmap.",
#         "geo": "Open a geographic location in a two or three-dimensional coordinate reference system on your preferred maps application.",
#         "javascript": "Execute JavaScript code.",
#         "jdbc": "Connect a database with Java Database Connectivity technology.",
#         "msteams": "Used by Microsoft to launch the Microsoft Teams desktop client",
#         "ms-access": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-excel": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-infopath": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-powerpoint": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-project": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-publisher": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-spd": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-visio": "Used by Microsoft to launch Microsoft Office applications",
#         "ms-word": "Used by Microsoft to launch Microsoft Office applications",
#         "odbc": "Open Database Connectivity",
#         "psns": "Used by PlayStation consoles to open the PS Store application, also used by Media Go",
#         "rdar": "URL scheme used by Apple's internal issue-tracking system",
#         "s3": "Used to interact programmatically with Amazon S3 bucket",
#         "shortcuts": "A scheme used by Apple to execute a Shortcut from apps that support links",
#         "slack": "Used by Slack to launch the Slack client",
#         "stratum": "Connectivity URI for the Stratum protocol, used for proof-of-work coordination in pooled cryptocurrency mining",
#         "trueconf": "Used by TrueConf Server to interact with client applications",
#         "viber": "Open the locally installed Viber application to link to a view or perform an action, such as share an URL to a contact.",
#         "web+": "Effectively namespaces web-based protocols from other, potentially less web-secure, protocols",
#         "zoommtg": "Used by Zoom conferencing software to launch the Zoom client",
#         "zoomus": "Used by Zoom conferencing software to launch the Zoom client"
#     }
#     if protocol in unofficial_schemes:
#         return unofficial_schemes[protocol]

#     # If the protocol is not found in the CSV or unofficial schemes, try some hail mary checks.
#     hail_mary = {
#         "postgres": "PostgreSQL database connection",
#         "mysql": "MySQL database connection",
#         "sqlite": "SQLite database connection",
#         "mongodb": "MongoDB database connection",
#         "redis": "Redis in-memory data structure store",
#         "cassandra": "Apache Cassandra distributed database",
#         "elasticsearch": "Elasticsearch search and analytics engine",
#         "oracle": "Oracle database connection",
#         "mssql": "Microsoft SQL Server database connection",
#         "db2": "IBM DB2 database connection",
#         "mariadb": "MariaDB database connection",
#         "clickhouse": "ClickHouse analytical database",
#         "influxdb": "InfluxDB time series database",
#         "couchdb": "Apache CouchDB document database",
#         "neo4j": "Neo4j graph database",
#         "kafka": "Apache Kafka streaming platform",
#         "rabbitmq": "RabbitMQ message broker",
#         "amqp": "Advanced Message Queuing Protocol",
#         "mqtt": "Message Queuing Telemetry Transport protocol",
#         "websocket": "WebSocket real-time communication protocol",
#         "ws": "WebSocket connection",
#         "wss": "Secure WebSocket connection",
#         "ssh": "Secure Shell remote access protocol",
#         "sftp": "SSH File Transfer Protocol",
#         "scp": "Secure Copy Protocol",
#         "rsync": "Remote synchronization protocol",
#         "nfs": "Network File System",
#         "smb": "Server Message Block protocol",
#         "cifs": "Common Internet File System",
#         "ldap": "Lightweight Directory Access Protocol",
#         "ldaps": "LDAP over SSL/TLS",
#         "snmp": "Simple Network Management Protocol",
#         "telnet": "Telnet remote terminal protocol",
#         "rlogin": "Remote login protocol",
#         "vnc": "Virtual Network Computing protocol",
#         "rdp": "Remote Desktop Protocol",
#         "x11": "X Window System protocol",
#         "xmpp": "Extensible Messaging and Presence Protocol",
#         "irc": "Internet Relay Chat protocol",
#         "sip": "Session Initiation Protocol",
#         "rtsp": "Real Time Streaming Protocol",
#         "rtmp": "Real-Time Messaging Protocol",
#         "hls": "HTTP Live Streaming protocol",
#         "dash": "Dynamic Adaptive Streaming over HTTP",
#         "magnet": "Magnet link for peer-to-peer file sharing",
#         "torrent": "BitTorrent protocol",
#         "ed2k": "eDonkey2000 network protocol",
#         "bitcoin": "Bitcoin cryptocurrency protocol",
#         "ethereum": "Ethereum blockchain protocol",
#         "ipfs": "InterPlanetary File System",
#         "docker": "Docker container registry protocol",
#         "k8s": "Kubernetes cluster resource",
#         "vault": "HashiCorp Vault secrets management",
#         "consul": "HashiCorp Consul service discovery",
#         "etcd": "etcd distributed key-value store",
#         "zookeeper": "Apache Zookeeper coordination service",
#         "hdfs": "Hadoop Distributed File System",
#         "s3": "Amazon S3 object storage",
#         "gs": "Google Cloud Storage",
#         "azure": "Microsoft Azure storage",
#         "dropbox": "Dropbox cloud storage",
#         "onedrive": "Microsoft OneDrive cloud storage",
#         "gdrive": "Google Drive cloud storage",
#         "box": "Box cloud storage",
#         "webdav": "Web Distributed Authoring and Versioning",
#         "caldav": "Calendaring Extensions to WebDAV",
#         "carddav": "vCard Extensions to WebDAV",
#         "git": "Git version control system",
#         "svn": "Subversion version control system",
#         "cvs": "Concurrent Versions System",
#         "hg": "Mercurial version control system",
#         "bzr": "Bazaar version control system",
#         "p4": "Perforce version control system",
#         "chrome": "Google Chrome browser internal protocol",
#         "firefox": "Mozilla Firefox browser internal protocol",
#         "safari": "Safari browser internal protocol",
#         "edge": "Microsoft Edge browser internal protocol",
#         "steam": "Steam gaming platform protocol",
#         "discord": "Discord chat application protocol",
#         "spotify": "Spotify music streaming protocol",
#         "skype": "Skype communication protocol",
#         "teams": "Microsoft Teams collaboration protocol",
#         "whatsapp": "WhatsApp messaging protocol",
#         "telegram": "Telegram messaging protocol",
#         "signal": "Signal secure messaging protocol",
#         "matrix": "Matrix decentralized communication protocol",
#         "slack": "Slack team communication protocol",
#         "zoom": "Zoom video conferencing protocol",
#         "webex": "Cisco Webex conferencing protocol",
#         "gotomeeting": "GoToMeeting conferencing protocol",
#         "jitsi": "Jitsi open-source video conferencing",
#         "mumble": "Mumble voice chat protocol",
#         "teamspeak": "TeamSpeak voice communication protocol",
#         "ventrilo": "Ventrilo voice chat protocol",
#         "rtp": "Real-time Transport Protocol",
#         "srt": "Secure Reliable Transport protocol",
#         "udp": "User Datagram Protocol connection",
#         "tcp": "Transmission Control Protocol connection",
#         "sctp": "Stream Control Transmission Protocol",
#         "icmp": "Internet Control Message Protocol",
#         "igmp": "Internet Group Management Protocol",
#         "ospf": "Open Shortest Path First routing protocol",
#         "bgp": "Border Gateway Protocol",
#         "rip": "Routing Information Protocol",
#         "dhcp": "Dynamic Host Configuration Protocol",
#         "dns": "Domain Name System protocol",
#         "ntp": "Network Time Protocol",
#         "radius": "Remote Authentication Dial-In User Service",
#         "tacacs": "Terminal Access Controller Access-Control System",
#         "kerberos": "Kerberos authentication protocol",
#         "saml": "Security Assertion Markup Language",
#         "oauth": "OAuth authorization protocol",
#         "openid": "OpenID authentication protocol",
#         "jwt": "JSON Web Token protocol",
#         "rest": "Representational State Transfer API",
#         "soap": "Simple Object Access Protocol",
#         "graphql": "GraphQL query language protocol",
#         "grpc": "gRPC remote procedure call protocol",
#         "jsonrpc": "JSON-RPC remote procedure call protocol",
#         "xmlrpc": "XML-RPC remote procedure call protocol",
#         "corba": "Common Object Request Broker Architecture",
#         "dcom": "Distributed Component Object Model",
#         "rmi": "Java Remote Method Invocation",
#         "jms": "Java Message Service",
#         "ejb": "Enterprise JavaBeans protocol",
#         "jndi": "Java Naming and Directory Interface",
#         "screen": "Screen sharing protocol, often used in remote desktop applications",
#         "vnc": "Virtual Network Computing protocol, used for remote desktop sharing",
#         "rdp": "Remote Desktop Protocol, used for remote desktop access",
#         "ssh": "Secure Shell protocol, used for secure remote access to systems",
#         "screenshots": "Screenshots and images, often used in documentation or support",
#         "screenshot": "Screenshots and images, often used in documentation or support",
#     }
#     if protocol in hail_mary:
#         return hail_mary[protocol]
#     return f"Unknown protocol '{protocol}'."

