package io.github.stardomains3.omnichat

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.DialogFragment
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import androidx.core.graphics.drawable.toDrawable

class OmniLoreConfigDialog : DialogFragment() {

    companion object {
        const val TAG = "OmniLoreConfigDialog"
        const val DEFAULT_ENDPOINT = "http://10.0.0.181:8420"
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.dialog_save_lan, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        dialog?.window?.setBackgroundDrawable(Color.TRANSPARENT.toDrawable())
        dialog?.window?.setDimAmount(0.8f)

        val prefs = SharedPreferencesHelper(requireContext())
        
        val editTextUrl = view.findViewById<TextInputEditText>(R.id.edit_text_lan_url)
        val editTextApiKey = view.findViewById<TextInputEditText>(R.id.edit_text_lan_api_key)
        val btnSave = view.findViewById<MaterialButton>(R.id.button_save_lan)
        val btnCancel = view.findViewById<MaterialButton>(R.id.button_cancel_lan)

        // Hide provider selection - this is OmniLore only
        view.findViewById<View>(R.id.checkbox_ollama).visibility = View.GONE
        view.findViewById<View>(R.id.checkbox_lm_studio).visibility = View.GONE
        view.findViewById<View>(R.id.checkbox_llama_cpp).visibility = View.GONE
        view.findViewById<View>(R.id.checkbox_mlx_lm).visibility = View.GONE

        // Load current OmniLore endpoint or use default
        val currentEndpoint = prefs.getOmniLoreEndpoint()
        editTextUrl.setText(currentEndpoint)
        editTextApiKey.setText("(No API key required for local OmniLore)")
        editTextApiKey.isEnabled = false

        btnSave.setOnClickListener {
            val url = editTextUrl.text?.toString()?.trim().orEmpty()

            when {
                url.isBlank() -> {
                    editTextUrl.error = "Please enter OmniLore endpoint URL"
                }
                url.startsWith("http://") || url.startsWith("https://") || url.contains("://") -> {
                    prefs.setOmniLoreEndpoint(url)
                    Toast.makeText(
                        requireContext(),
                        "OmniLore endpoint saved: $url",
                        Toast.LENGTH_SHORT
                    ).show()
                    dismiss()
                }
                else -> {
                    editTextUrl.error = "URL must contain a scheme (e.g. http://)"
                }
            }
        }

        btnCancel.setOnClickListener {
            dismiss()
        }

        editTextUrl.requestFocus()
    }
}
