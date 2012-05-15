#
# A few switches that enable or disable certain features in the proxy.
#
# *** Don't forget to restart KSP after modifying this file! ***
#

# The default supported book formats are (in this order):
#supported_formats = [ 'MOBI', 'AZW', 'PRC', 'PDF' ]
# If you want to only serve a subset of these, set this option (case does not matter).
# NOTE: when multiple supported formats are available for a book, only the first one in the list above will be served to the kindle device.
# Also, if you download a book in one format, then another format with a higher priority appears for that book,
#   you'll just confuse the hell out of the kindle...
# NOTE: KSP will only 'see' MOBI books with the proper ASIN tag -- see docs/library.md for details.

# New revisions of books are automatically downloaded by the device.
# WARNING: updating a book file on the device will reset the last-read-position, and delete the notes and highlights for the book!
download_updated_books = False

# If set, does its best to scrub information uploaded to Amazon of unnecessary stuff (like what non-Kindle Store books you have on the device).
# It's not really necessary, but adds a bit of privacy.
# Even if this is False, calls that make no sense to upstream will be filtered
#   (like the device informing upstream it has completed downloading a book from your library).
scrub_uploads = True

# If False, intercept calls to device-messaging and det servers (log uploads).
# It's not really necessary, but adds a bit of privacy.
allow_logs_upload = False

# Set this to True to allow automatic firmware updates.
# Most likely you want to leave this to False, because firmware updates will undo your device customizations.
allow_firmware_updates = False

# Create collections based on certain book tags.  See docs/collections.md for details.
collection_tags = [ 'first tag', 'second tag', 'third tag' ]
