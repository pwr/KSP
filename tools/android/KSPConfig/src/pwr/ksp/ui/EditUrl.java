package pwr.ksp.ui;

import android.app.Dialog;
import android.content.DialogInterface;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import pwr.ksp.KSPConfig;
import pwr.ksp.R;

import java.net.MalformedURLException;
import java.net.URL;

public class EditUrl extends Dialog implements DialogInterface.OnShowListener, View.OnClickListener, TextWatcher {
	private final KSPConfig ksp;
	private final EditText editUrl;
	private final Button testButton;

	public EditUrl(KSPConfig _ksp) {
		super(_ksp);

		ksp = _ksp;

		setTitle(R.string.edit_url_title);
		setContentView(R.layout.edit_url);
		setOnShowListener(this);
		setCancelable(true);

		editUrl = (EditText) findViewById(R.id.edit_url);
		editUrl.addTextChangedListener(this);

		testButton = (Button) findViewById(R.id.test_new_url);
		testButton.setOnClickListener(this);

		final Button cancel = (Button) findViewById(R.id.cancel_edit_url);
		cancel.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				cancel();
			}
		});
	}

	@Override
	public void onShow(DialogInterface _intf) {
		String serviceURL = ksp.getConfig().getServiceURL();
		if (serviceURL == null || serviceURL.length() == 0) {
			serviceURL = "https://";
		}
		editUrl.setText(serviceURL);
		editUrl.setSelection(serviceURL.length());
	}

	@Override
	public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {
		//nothing
	}

	@Override
	public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
		//nothing
	}

	@Override
	public void afterTextChanged(Editable editable) {
		String url = editable.toString();
		if (url.length() > 0) {
			try {
				new URL(url);
				testButton.setEnabled(true);
				return;
			} catch (MalformedURLException ex) {
				// nothing
			}
		}
		testButton.setEnabled(false);
	}

	@Override
	public void onClick(View view) {
		String url = editUrl.getText().toString();
		if (url.length() > 0) {
			ksp.ping(url);
		}
		dismiss();
	}
}
