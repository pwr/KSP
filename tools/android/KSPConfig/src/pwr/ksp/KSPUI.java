package pwr.ksp;

import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import pwr.ksp.ui.Dialogs;

public class KSPUI {
	private final KSPConfig ksp;

	private final Button editURLButton;
	private final Button clearButton;
	private final Button applyButton;

	private final TextView currentConfiguration;
	private final TextView currentUrl;
	private final TextView newConfiguration;
	private final TextView newUrl;

	KSPUI(final KSPConfig _ksp) {
		ksp = _ksp;

		editURLButton = (Button) ksp.findViewById(R.id.change_service_url);
		editURLButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				Dialogs.create(Dialogs.EDIT_URL, ksp).show();
			}
		});

		clearButton = (Button) ksp.findViewById(R.id.clear_config);
		clearButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				ksp.clearConfiguration();
			}
		});

		applyButton = (Button) ksp.findViewById(R.id.apply_config);
		applyButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				ksp.applyConfiguration();
			}
		});

		currentConfiguration = (TextView) ksp.findViewById(R.id.current_config);
		currentUrl = (TextView) ksp.findViewById(R.id.current_url);
		newConfiguration = (TextView) ksp.findViewById(R.id.new_config);
		newUrl = (TextView) ksp.findViewById(R.id.new_url);
	}

	public void reset() {
		editURLButton.setEnabled(false);
		clearButton.setEnabled(false);
		applyButton.setEnabled(false);

		currentConfiguration.setText("");
		newConfiguration.setText("");
	}

	public void configurationChanged(String _url) {
		applyButton.setEnabled(true);

		if (_url == null && currentUrl.getVisibility() == View.GONE) {
			newConfiguration.setText("");
			clearButton.setEnabled(false);
			newUrl.setText("");
			newUrl.setVisibility(View.GONE);
			return;
		}

		if (_url != null && currentUrl.getVisibility() == View.VISIBLE) {
			String current = currentUrl.getText().toString();
			if (_url.equals(current)) {
				newConfiguration.setText("");
				clearButton.setEnabled(true);
				newUrl.setText("");
				newUrl.setVisibility(View.GONE);
				return;
			}
		}

		if (_url == null) {
			newConfiguration.setText("Kindle for Android will use the default (Amazon) service.");
			clearButton.setEnabled(false);
			newUrl.setText("");
			newUrl.setVisibility(View.GONE);
		} else {
			newConfiguration.setText("Kindle for Android will use this service URL:");
			clearButton.setEnabled(true);
			newUrl.setText(_url);
			newUrl.setVisibility(View.VISIBLE);
		}
	}

	public void configurationLoaded(String _url) {
		editURLButton.setEnabled(true);
		applyButton.setEnabled(false);

		if (_url == null) {
			clearButton.setEnabled(false);
			currentConfiguration.setText("Kindle for Android is using the default (Amazon) service.");
			currentUrl.setText(null);
			currentUrl.setVisibility(View.GONE);
		} else {
			clearButton.setEnabled(true);
			currentConfiguration.setText("Kindle for Android is using this service URL:");
			currentUrl.setText(_url);
			currentUrl.setVisibility(View.VISIBLE);
		}
	}
}

