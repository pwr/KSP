import logging

from handlers import Upstream, DummyResponse, ExceptionResponse, is_uuid
from handlers import WWW, STORE_PATH
import calibre, qxml


class Store (Upstream):
	_NO_INFO = '''
<root version="2.0" defaultDiv="id_b7566331-9ce8-4a75-b4dc-30808e6196d2" ttl="2400" cacheFile="book_details_b7566331-9ce8-4a75-b4dc-30808e6196d2.xml">
<menu-items>
<menu-item name="Kindle Storefront" div="storefront_A1LN8BAO1O3KNG" link="/gp/g7g/xyml1/storefront.xml/ref=kinx_gw_menu_1/180-1711742-2923121" />
<menu-item name="Books " div="browse_subcat_0_154606011_0_"
link="/gp/g7g/xyml1/browse_subcat.xml/ref=kinx_gw_storefrontc_2/180-1711742-2923121?nodeid=154606011" />
<menu-item name="Newspapers" div="browse_subcat_0_165389011_0_"
link="/gp/g7g/xyml1/browse_subcat.xml/ref=kinx_gw_storefrontc_3/180-1711742-2923121?nodeid=165389011" />
<menu-item name="Magazines" div="browse_subcat_0_241646011_0_"
link="/gp/g7g/xyml1/browse_subcat.xml/ref=kinx_gw_storefrontc_4/180-1711742-2923121?nodeid=241646011" />
<menu-item name="Kindle Singles" div="browse_0_2486013011_0" link="/gp/g7g/xyml1/browse_items.xml/ref=kinx_gw_storefrontc_7/180-1711742-2923121?nodeid=2486013011" />
<menu-item name="Kindle Best Sellers" div="browse_1_358606011_0" link="/gp/g7g/xyml1/topsellers.xml/ref=kinx_gw_menu_2/180-1711742-2923121" />
<menu-item name="Recommended for You" div="rec_0" link="/gp/g7g/xyml1/recommendations.xml/ref=kinx_gw_menu_4/180-1711742-2923121" />
<menu-item name="Your Wish List" link="/gp/g7g/xyml1/wishlist.xml/ref=kinx_gw_menu_5/180-1711742-2923121" />
<menu-item name="Your Recent History" link="/gp/xyml/history.xyml/ref=kinx_gw_menu_7/180-1711742-2923121" />
</menu-items>
<instructions>
<div name="id_b7566331-9ce8-4a75-b4dc-30808e6196d2">
<text x="64" y="72" lineMargin="24">
No further information is available
</text>
</div>
</instructions>
</root>
	'''

	def __init__(self):
		Upstream.__init__(self, WWW, STORE_PATH)

	def call(self, request, device):
		if device.is_provisional():
			return None

		q = request.get_query_params()
		asin = q.get('ASIN')
		if not asin:
			return 400

		if is_uuid(asin): # yay
			return process(self, request, device)

		del request.headers['Referer']
		request.headers['Referer'] = 'https://www.amazon.com'
		return self.call_upstream(request, device)

	def process(self, request, device):
		return None
