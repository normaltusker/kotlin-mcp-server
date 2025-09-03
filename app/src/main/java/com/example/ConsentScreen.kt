package com.example.compliance

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ConsentScreen(onConsent: (Boolean) -> Unit) {
    var accepted by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("We value your privacy", style = MaterialTheme.typography.headlineSmall)
        Text("Please review and accept our data policy to continue.")

        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = accepted, onCheckedChange = { accepted = it })
            Text("I agree to the data policy", modifier = Modifier.padding(start = 8.dp))
        }

        Button(
            onClick = { onConsent(accepted) },
            enabled = accepted
        ) { Text("Continue") }
    }
}
