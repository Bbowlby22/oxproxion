import io.github.stardomains3.oxproxion.LlmModel
import kotlinx.serialization.json.Json

fun main() {
    // Create a LAN model like fetchOllamaModels does
    val lanModel = LlmModel(
        displayName = "llama3.2",
        apiIdentifier = "llama3.2",
        isVisionCapable = false,
        isImageGenerationCapable = false,
        isReasoningCapable = false,
        created = System.currentTimeMillis() / 1000,
        isFree = true,
        isLANModel = true
    )
    
    println("Original model: $lanModel")
    println("isLANModel in original: ${lanModel.isLANModel}")
    
    // Simulate serialization (like saveCustomModels does)
    val json = Json { prettyPrint = true }
    val serialized = json.encodeToString(LlmModel.serializer(), lanModel)
    println("\nSerialized JSON:\n$serialized")
    
    // Simulate deserialization (like getCustomModels does)
    val deserialized = json.decodeFromString(LlmModel.serializer(), serialized)
    println("\nDeserialized model: $deserialized")
    println("isLANModel in deserialized: ${deserialized.isLANModel}")
    
    // Verify the flag is preserved
    if (deserialized.isLANModel == true) {
        println("\n✅ SUCCESS: isLANModel flag is preserved through serialization!")
    } else {
        println("\n❌ ERROR: isLANModel flag was lost during serialization!")
    }
}
