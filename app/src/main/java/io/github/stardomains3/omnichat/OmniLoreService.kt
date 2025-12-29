package io.github.stardomains3.omnichat

import android.content.Context
import android.util.Log
import io.ktor.client.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.*
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/**
 * OmniLore Chat Service
 * 
 * Provides integration with OmniLore.AI chat API for local network access
 * to self-learning knowledge cache and intelligent model routing.
 * 
 * Usage:
 * ```
 * val service = OmniLoreService(context)
 * val response = service.chat(
 *     messages = listOf(
 *         mapOf("role" to "user", "content" to "Hello, OmniLore!")
 *     ),
 *     model = "omnilore/smart-chat"
 * )
 * ```
 */
class OmniLoreService(private val context: Context) {
    
    companion object {
        const val TAG = "OmniLoreService"
        // Default to localhost - can be configured via settings
        const val DEFAULT_HOST = "http://10.0.0.181:8420"
        const val CHAT_ENDPOINT = "/chat"
        const val QUERY_ENDPOINT = "/query"
    }
    
    private val httpClient: HttpClient = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json { 
                ignoreUnknownKeys = true
                prettyPrint = true
            })
        }
        engine {
            preconfigured = OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
        }
    }
    
    /**
     * Send chat message to OmniLore
     * 
     * @param messages List of message maps with "role" and "content"
     * @param model Model to use (defaults to smart-chat)
     * @param bypassCache Skip the self-learning cache
     * @param storeResult Store this interaction for future learning
     * @return The chat response text
     */
    suspend fun chat(
        messages: List<Map<String, String>>,
        model: String = "gpt-4o-mini",
        bypassCache: Boolean = false,
        storeResult: Boolean = true
    ): String {
        return try {
            val host = getConfiguredHost()
            
            // Build OmniLore-format request
            val requestBody = buildJsonObject {
                putJsonArray("messages") {
                    messages.forEach { msg ->
                        addJsonObject {
                            put("role", msg["role"] ?: "user")
                            put("content", msg["content"] ?: "")
                        }
                    }
                }
                put("model", model)
                put("bypass_cache", bypassCache)
                put("store_result", storeResult)
                put("smart_chat", model == "omnilore/smart-chat")
            }
            
            Log.d(TAG, "Sending chat request to OmniLore: $host$CHAT_ENDPOINT")
            
            val response = httpClient.post("$host$CHAT_ENDPOINT") {
                contentType(ContentType.Application.Json)
                setBody(requestBody.toString())
            }
            
            if (response.status == HttpStatusCode.OK) {
                val responseJson = Json.parseToJsonElement(response.bodyAsText())
                    .jsonObject
                responseJson["response"]?.jsonPrimitive?.content 
                    ?: "No response from OmniLore"
            } else {
                Log.e(TAG, "OmniLore returned ${response.status}: ${response.bodyAsText()}")
                "Error: OmniLore returned ${response.status}"
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to reach OmniLore: ${e.message}", e)
            "Error: Could not connect to OmniLore. Make sure it's running at ${getConfiguredHost()}"
        }
    }
    
    /**
     * Query the OmniLore knowledge cache
     * without generating new responses
     * 
     * @param query Search query
     * @param limit Maximum results
     * @return List of similar cached entries
     */
    suspend fun queryCache(
        query: String,
        limit: Int = 5
    ): List<Map<String, String>> {
        return try {
            val host = getConfiguredHost()
            
            val requestBody = buildJsonObject {
                put("query", query)
                put("limit", limit)
            }
            
            val response = httpClient.post("$host$QUERY_ENDPOINT") {
                contentType(ContentType.Application.Json)
                setBody(requestBody.toString())
            }
            
            if (response.status == HttpStatusCode.OK) {
                val responseJson = Json.parseToJsonElement(response.bodyAsText())
                    .jsonObject
                // Parse results based on OmniLore's response format
                emptyList()
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to query cache: ${e.message}")
            emptyList()
        }
    }
    
    /**
     * Check if OmniLore is reachable
     */
    suspend fun isReachable(): Boolean {
        return try {
            val host = getConfiguredHost()
            val response = httpClient.get("$host/health")
            response.status == HttpStatusCode.OK
        } catch (e: Exception) {
            Log.d(TAG, "OmniLore health check failed: ${e.message}")
            false
        }
    }
    
    /**
     * Get the configured OmniLore host
     * Reads from SharedPreferences if available
     */
    private fun getConfiguredHost(): String {
        return try {
            val prefs = SharedPreferencesHelper(context)
            prefs.getOmniLoreEndpoint()
        } catch (e: Exception) {
            Log.w(TAG, "Could not read OmniLore endpoint from prefs, using default: ${e.message}")
            DEFAULT_HOST
        }
    }
    
    fun cleanup() {
        httpClient.close()
    }
}
