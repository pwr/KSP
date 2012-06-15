package ksp;

import ksp.sys.Configuration;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Properties;

class Pinger extends Thread {
	private static final String SERVICE_REFRESH = "/getItems?reason=ServiceRefresh";

	private final Log LOG = new Log(Pinger.class);

	private final KSPKindlet ksp;
	private String url;

	Pinger(KSPKindlet _ksp, String _url) {
		super("ping [" + _url + "]");

		ksp = _ksp;
		url = _url;
	}

	public void run() {
		if (!ksp.checkConnected()) {
			return;
		}

		ksp.progress("Checking...");

		if (url.endsWith("/")) {
			url = url.substring(0, url.length() - 1);
		}

		Scfg result = null;
		Exception fail = null;

		while (result == null && fail == null && !interrupted()) {
			try {
				URL u = new URL(url);
				ping(u);
			} catch (Redirect ex) {
				url = ex.getMessage();
			} catch (Scfg ex) {
				result = ex;
			} catch (Exception ex) {
				LOG.e("checking url " + url + " failed", ex);
				fail = ex;
			}
		}

		ksp.progress(null);

		if (result != null) {
			ksp.act.changeUrl(result.props);
		} else if (fail != null) {
			ksp.ui.alert(UI.INVALID_URL_ + fail.getMessage());
		} else {
			ksp.ui.alert(UI.INVALID_URL);
		}
	}

	void ping(URL _u) throws Exception {
		URL sr = new URL(_u + ServiceConfig.FIONA_TODO_LIST_PROXY + SERVICE_REFRESH);

		LOG.w("requesting " + sr);

		HttpURLConnection uc = (HttpURLConnection) sr.openConnection();
		uc.connect();

		try {
			int status = uc.getResponseCode();
			LOG.i("got status " + status + " " + uc.getResponseMessage());
			if (status != 200) {
				throw new IllegalArgumentException("server replied with an invalid status: " + uc.getResponseMessage());
			}

			String scfg = readScfg(uc.getInputStream());
			if (scfg == null) {
				throw new IllegalArgumentException("no SCFG item found in ServiceRefresh response");
			}

			LOG.i("SCFG:" + scfg);
			Properties p = new Properties();
			p.load(new ByteArrayInputStream(scfg.getBytes()));
			LOG.i("SCFG:" + p);

			String urlTodo = p.getProperty(Configuration.KEY_URL_TODO);
			if (urlTodo == null) {
				LOG.w("no " + Configuration.KEY_URL_TODO + " found in SCFG: " + p);
				throw new IllegalArgumentException("no " + Configuration.KEY_URL_TODO + " found in dynamic configuration");
			}

			String serviceUrl = urlTodo;
			if (serviceUrl.endsWith(ServiceConfig.FIONA_TODO_LIST_PROXY)) {
				serviceUrl = serviceUrl.substring(0, serviceUrl.length() - ServiceConfig.FIONA_TODO_LIST_PROXY.length());
			}

			if (!serviceUrl.equals(_u.toString())) {
				throw new Redirect(serviceUrl);
			}

			LOG.w("url validated: " + url);
			throw new Scfg(p);
		} finally {
			uc.disconnect();
		}
	}

	private String readScfg(InputStream _is) throws Exception {
		DocumentBuilder db = DocumentBuilderFactory.newInstance().newDocumentBuilder();
		Document doc = db.parse(_is);
		Node x_item = getTag(doc.getDocumentElement(), new String[]{"response", "items", "item"}, 0);
		if (x_item != null) {
			NamedNodeMap atts = x_item.getAttributes();
			if (atts.getNamedItem("action") != null &&  //
				atts.getNamedItem("action").getNodeValue().equals("SET") && //
				atts.getNamedItem("type") != null && //
				atts.getNamedItem("type").getNodeValue().equals("SCFG")) {
				if (x_item.getFirstChild() != null) {
					return x_item.getFirstChild().getNodeValue();
				}
			}
		}
		return null;
	}

	private Node getTag(Node _root, String[] _path, int _pathIndex) {
		//LOG.i("" + _pathIndex + " node " + _root + " " + _root.getNodeName() + " " + _root.getNodeType());
		if (_root.getNodeType() != Node.ELEMENT_NODE || !_root.getNodeName().equals(_path[_pathIndex])) {
			return null;
		}
		if (_pathIndex == _path.length - 1) {
			return _root;
		}

		NodeList nodes = _root.getChildNodes();
		for (int i = 0; i < nodes.getLength(); i++) {
			Node n = getTag(nodes.item(i), _path, _pathIndex + 1);
			if (n != null) {
				return n;
			}
		}

		return null;
	}

	private static final class Redirect extends Exception {
		Redirect(String _url) {
			super(_url);
		}
	}

	private static final class Scfg extends Exception {
		final Properties props;
		Scfg(Properties _p) {
			props = _p;
		}
	}
}
