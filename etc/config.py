#
# KSP server configuration
#
# *** Don't forget to restart KSP after modifying this file! ***
#

# Port on which to listen.  The default value is recommended, unless you want to tweak your setup in a certain way.
server_port = 45350
# IP to bind to, leave empty to bind to all network interfaces.
server_host = ''

# if you set this option, and point it to a SSL PEM file, the server will only accept HTTPS connections
server_certificate = None

# Under what url is the device calling the server.
# WARNING: MUST be matched by the changes in ServerConfig.conf on the device!
# NOTE: This is the url of the front-facing HTTPS server, not KSP's url!
server_url = 'https://<your_ssl_server>/KSP'

# The folder where the logs will be written; auto-created if it does not exists.
# MUST be writable.
logs_path = 'logs/'

# minimum log level
log_level = 'INFO'

# The folder where KSP keeps its databases; auto-created on the first run if it does not exist.
# MUST be writable.
database_path = 'db/'

# Path to the Calibre library to use.
# NOTE: If multiple devices use this proxy, they will all share the same library!
# MUST exist -- and contain a Calibre library, ofcourse.
calibre_library = '<path to your calibre library>'
