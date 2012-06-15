package ksp;

import com.amazon.kindle.kindlet.ui.*;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Font;

class UI {
	private static final int THIN_BORDER = 12;
	private static final int BORDER = 24;
	private static final int SPACER = 45;
	private static final int LARGE_SPACER = 70;

	private static final KindletUIResources KUI = KindletUIResources.getInstance();

	private static final Color HIGHLIGHT = KUI.getBackgroundColor(KindletUIResources.KColorName.GRAY_02);
	private static final Font TEXT_FONT = KUI.getFont(KindletUIResources.KFontFamilyName.SERIF, 24, KindletUIResources.KFontStyle.ITALIC);
	private static final Font URL_FONT = KUI.getFont(KindletUIResources.KFontFamilyName.SANS_SERIF, 26);

	private static final String APP_DESCRIPTION = //
			"This Kindlet allows changing the service URL " + //
			"your Kindle device will use to download books and save annotations.";

	private static final String CURRENT_CONFIG_DEFAULT = "Your Kindle is using\nthe standard (Amazon) services.";
	private static final String CURRENT_CONFIG_CUSTOM = "Your Kindle is using a custom service URL:";

	private static final String NEW_CONFIG_DEFAULT = "Your Kindle will use\nthe standard (Amazon) services.";
	private static final String NEW_CONFIG_CUSTOM = "Your Kindle will use a custom service URL:";

	private static final String EDIT_URL = "URL: ";

	static final String INVALID_URL = "The given URL is invalid or the server did not respond.";
	static final String INVALID_URL_ = "The given URL is invalid or the server did not respond.\n\n";

	static final String CONFIG_SAVED = "The new services configuration has been applied.";
	static final String CONFIG_LOAD_FAILED = "Failed to load services configuration.";
	static final String CONFIG_SAVE_FAILED = "Failed to apply services configuration.";

	private final KLabel crtDescLabel = new KLabelMultiline();
	private final KLabel crtUrlLabel = new KLabel();

	private final KButton changeUrlButton = new KButton("Change service URL");
	private final KButton useDefaultButton = new KButton("Use standard service");

	private final KLabel newDescLabel = new KLabelMultiline();
	private final KLabel newUrlLabel = new KLabel();

	private final KButton apply = new KButton("Apply changes");

	private final KOptionPane.MessageDialogListener DISMISS = new KOptionPane.MessageDialogListener() {
		public void onClose() {
			//
		}
	};

	private final KOptionPane.InputDialogListener CHANGE_URL_LISTENER = new KOptionPane.InputDialogListener() {
		public void onClose(String _result) {
			act.checkAndChangeUrl(_result);
		}
	};

	private final Actions act;
	private final Container root;

	UI(Container _c, Actions _act) {
		act = _act;
		root = _c;
		buildInto(root);

		crtUrlLabel.setVisible(false);
		newUrlLabel.setVisible(false);

		changeUrlButton.setEnabled(false);
		useDefaultButton.setEnabled(false);
		apply.setEnabled(false);
	}

	void configurationLoaded(ServiceConfig _config) {
		String url = _config.getServiceUrl();

		crtDescLabel.setText(url == null ? CURRENT_CONFIG_DEFAULT : CURRENT_CONFIG_CUSTOM);
		crtUrlLabel.setText(url);
		crtUrlLabel.setVisible(url != null);

		changeUrlButton.setEnabled(true);
		changeUrlButton.requestFocus();
		useDefaultButton.setEnabled(url != null);

		newDescLabel.setText(null);
		newUrlLabel.setText(null);
		apply.setEnabled(false);
	}

	void newConfiguration(ServiceConfig _config) {


		String url = _config.getServiceUrl();

		useDefaultButton.setEnabled(url != null);

		newDescLabel.setText(url == null ? NEW_CONFIG_DEFAULT : NEW_CONFIG_CUSTOM);
		newUrlLabel.setText(url);
		newUrlLabel.setVisible(url != null);

		apply.setEnabled(true);
		apply.requestFocus();
	}

	void openChangeUrlPanel(String _url) {
		KOptionPane.showInputDialog(root, EDIT_URL, _url, CHANGE_URL_LISTENER);
	}

	void alert(String _message) {
		try {
			KOptionPane.showMessageDialog(root, _message, DISMISS);
		} catch (Exception ex) {
			ex.printStackTrace();
			// whatever
		}
	}

	//
	//
	//

	private void buildInto(Container c) {
		KBox main = new KBox(KBoxLayout.PAGE_AXIS);

		KLabel description = new KLabelMultiline(APP_DESCRIPTION);
		description.setFont(TEXT_FONT);

		main.add(description);
		main.add(KBox.createVerticalStrut(LARGE_SPACER));

		crtDescLabel.setFont(TEXT_FONT);
		crtDescLabel.setHorizontalAlignment(KTextComponent.CENTER);

		crtUrlLabel.setFont(URL_FONT);

		main.add(vbox(crtDescLabel, crtUrlLabel, HIGHLIGHT));

		main.add(KBox.createVerticalStrut(SPACER));
		main.add(lineBox(changeUrlButton, useDefaultButton, null));
		main.add(KBox.createVerticalStrut(LARGE_SPACER));

		newDescLabel.setFont(TEXT_FONT);
		newDescLabel.setHorizontalAlignment(KTextComponent.CENTER);

		newUrlLabel.setFont(URL_FONT);

		Component newBox = vbox(newDescLabel, newUrlLabel, HIGHLIGHT);
		main.add(newBox);

		main.add(KBox.createVerticalStrut(SPACER));
		main.add(lineBox(apply, null, null));

		main.add(KBox.createVerticalStrut(LARGE_SPACER));
		main.add(KBox.createVerticalGlue());

		c.add(main);
		addBorders(c, BORDER);

		c.setFocusTraversalPolicy(new LogicalFocus2DTraversalPolicy(new Component[][]{ //
																					   {changeUrlButton, useDefaultButton}, //
																					   {apply, apply} //
		}));

		changeUrlButton.addActionListener(act.editUrlAction);
		useDefaultButton.addActionListener(act.useDefaults);
		apply.addActionListener(act.applyAction);
	}

	private static Component lineBox(KComponent c1, KComponent c2, Color _background) {
		KBox box = new KBox(KBoxLayout.LINE_AXIS);
		box.setBackground(_background);

		box.add(KBox.createHorizontalGlue());
		box.add(c1);
		box.add(KBox.createHorizontalGlue());
		if (c2 != null) {
			box.add(c2);
			box.add(KBox.createHorizontalGlue());
		}
		return box;
	}

	private static Component vbox(KLabel c1, KLabel c2, Color _background) {
		KPanel inner = new KPanel(new BorderLayout());
		inner.setBackground(_background);

		inner.add(c1);
		c1.setBackground(_background);

		inner.add(lineBox(c2, null, _background), BorderLayout.SOUTH);

		KPanel p = new KPanel(new BorderLayout());
		p.setBackground(_background);
		p.setEnabled(false);

		addBorders(p, THIN_BORDER);
		p.add(inner);

		return p;
	}

	private static void addBorders(Container _c, int _border) {
		Dimension d = new Dimension(_border, _border);

		Component b = KBox.createRigidArea(d);
		b.setBackground(_c.getBackground());
		_c.add(b, BorderLayout.NORTH);
		b = KBox.createRigidArea(d);
		b.setBackground(_c.getBackground());
		_c.add(b, BorderLayout.SOUTH);
		b = KBox.createRigidArea(d);
		b.setBackground(_c.getBackground());
		_c.add(b, BorderLayout.WEST);
		b = KBox.createRigidArea(d);
		b.setBackground(_c.getBackground());
		_c.add(b, BorderLayout.EAST);
	}
}
