package pwr.ksp;

import android.view.View;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.TextView;
import pwr.ksp.ui.EditUrl;

public class KSPUI {
	private final KSPConfig ksp;

	private final TextView loadError;

	private final View currentConfigurationBox;
	private final TextView currentConfiguration;
	private final TextView currentUrl;

	private final View buttonsBox;
	private final Button editURLButton;
	private final Button clearButton;

	private final View newConfigurationBox;
	private final TextView newConfiguration;
	private final TextView newUrl;
	private final Button applyButton;

	private final TextView applyError;
	private final TextView kindleRunning;

	private final Animation fade_in;
	private final Animation fade_out;

	KSPUI(final KSPConfig _ksp) {
		ksp = _ksp;

		loadError = (TextView) ksp.findViewById(R.id.load_error);

		currentConfigurationBox = ksp.findViewById(R.id.current_config_box);
		currentConfiguration = (TextView) ksp.findViewById(R.id.current_config);
		currentUrl = (TextView) ksp.findViewById(R.id.current_url);

		buttonsBox = ksp.findViewById(R.id.buttons_box);

		editURLButton = (Button) ksp.findViewById(R.id.change_service_url);
		editURLButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				new EditUrl(ksp).show();
			}
		});

		clearButton = (Button) ksp.findViewById(R.id.clear_config);
		clearButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				ksp.clearConfiguration();
			}
		});

		newConfigurationBox = ksp.findViewById(R.id.new_config_box);

		newConfiguration = (TextView) ksp.findViewById(R.id.new_config);
		newUrl = (TextView) ksp.findViewById(R.id.new_url);

		applyButton = (Button) ksp.findViewById(R.id.apply_config);
		applyButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View view) {
				fade(applyError, false);
				ksp.applyConfiguration();
			}
		});

		applyError = (TextView) ksp.findViewById(R.id.apply_error);

		kindleRunning = (TextView) ksp.findViewById(R.id.kindle_running);

		fade_in = AnimationUtils.loadAnimation(ksp, android.R.anim.fade_in);
		fade_in.setDuration(300);
		fade_out = AnimationUtils.loadAnimation(ksp, android.R.anim.fade_out);
		fade_out.setDuration(200);
	}

	private void fade(View _v, boolean _visible) {
		boolean currentlyVisible = _v.getVisibility() == View.VISIBLE;
		if (_visible) {
			if (!currentlyVisible) {
				_v.startAnimation(fade_in);
				_v.setVisibility(View.VISIBLE);
			}
		} else {
			if (currentlyVisible) {
				_v.startAnimation(fade_out);
				_v.setVisibility(View.GONE);
			}
		}
	}

	public void reset() {
		fade(kindleRunning, false);
		fade(applyError, false);

		fade(applyButton, false);
		applyButton.setEnabled(false);

		fade(newConfigurationBox, false);
		newConfiguration.setText(null);
		newUrl.setText(null);
		newUrl.setVisibility(View.GONE);

		fade(buttonsBox, false);
		editURLButton.setEnabled(false);
		clearButton.setEnabled(false);

		fade(currentConfigurationBox, false);
		currentConfiguration.setText(null);
		currentUrl.setText(null);
		currentUrl.setVisibility(View.GONE);

		fade(loadError, false);
	}

	public void configurationChanged(String _url) {
		boolean noChanges = (_url == null && currentUrl.getText().length() == 0) || (_url != null && _url.equals(currentUrl.getText()));

		fade(applyError, false);
		clearButton.setEnabled(_url != null);

		if (noChanges) {
			fade(kindleRunning, false);

			fade(applyButton, false);
			applyButton.setEnabled(false);

			fade(newConfigurationBox, false);
			newConfiguration.setText(null);
			newUrl.setText(null);
			newUrl.setVisibility(View.GONE);

			return;
		}

		newConfiguration.setText(ksp.getString(_url == null ? R.string.new_configuration_default : R.string.new_configuration_url));
		newUrl.setText(_url);
		newUrl.setVisibility(_url == null ? View.GONE : View.VISIBLE);
		fade(newConfigurationBox, true);

		applyButton.setEnabled(true);
		fade(applyButton, true);

		fade(kindleRunning, K4A.isRunning(ksp));
	}

	public void configurationLoaded(String _url) {
		fade(loadError, false);

		currentUrl.setVisibility(_url == null ? View.GONE : View.VISIBLE);
		currentUrl.setText(_url);
		currentConfiguration.setText(ksp.getString(_url == null ? R.string.current_configuration_default : R.string.current_configuration_url));
		fade(currentConfigurationBox, true);

		editURLButton.setEnabled(true);
		clearButton.setEnabled(_url != null);
		fade(buttonsBox, true);
	}

	public void fatal(int _stringId, boolean _initial) {
		if (_initial) {
			loadError.setText(ksp.getString(_stringId));
			fade(loadError, true);
		} else {
			fade(kindleRunning, false);
			applyError.setText(ksp.getString(_stringId));
			fade(applyError, true);
		}
	}
}

