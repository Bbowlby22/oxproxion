/**
 * OmniLore Kotlin Patterns Library
 * Auto-generated from tribal knowledge - Do not edit manually.
 */

package com.omnilore.patterns

/**
 * Kotlin code quality patterns
 */
enum class KotlinLintPattern(val description: String) {
    // Type safety patterns
    NULLABLE_TYPE("Use ? for nullable types"),
    NON_NULL_ASSERTION("Use !! only when certain"),
    SCOPE_FUNCTIONS("Prefer let, run, with, apply, also"),

    // Naming conventions
    CAMEL_CASE("Use camelCase for variables"),
    PASCAL_CASE("Use PascalCase for classes"),
    UPPER_SNAKE("Use UPPER_SNAKE_CASE for constants"),

    // Error patterns
    NULL_SAFETY("Always check for null before access"),
    EXCEPTION_HANDLING("Catch specific exceptions"),
    RESOURCE_MANAGEMENT("Use use() for resource cleanup");
}

/**
 * Common Kotlin error fixes
 */
object KotlinErrorFixes {

    /**
     * Fix: Null safety
     */
    fun fixNullSafety(): String {
        return """
// Before:
val value = getValue()
val result = value!!.process()

// After:
val value = getValue()
val result = value?.process() ?: defaultValue()
""".trimIndent()
    }

    /**
     * Fix: Type safety
     */
    fun fixTypeSafety(): String {
        return """
// Before:
fun process(obj: Any): String {
    return (obj as String).uppercase()
}

// After:
fun <T> process(obj: T): String {
    return when (obj) {
        is String -> obj.uppercase()
        else -> "invalid"
    }
}
""".trimIndent()
    }

    /**
     * Fix: Scope functions
     */
    fun fixScopeFunctions(): String {
        return """
// Before:
val person = Person()
person.name = "John"
person.age = 30
val result = person.validate()

// After:
val result = Person().apply {
    name = "John"
    age = 30
}.validate()
""".trimIndent()
    }
}

/**
 * Pattern database
 */
object KotlinPatterns {
    val style = mapOf(
        "indent" to 4,
        "maxLineLength" to 120,
        "nullSafety" to true
    )

    val naming = mapOf(
        "variables" to "camelCase",
        "classes" to "PascalCase",
        "constants" to "UPPER_SNAKE_CASE"
    )

    val types = mapOf(
        "explicitTypes" to true,
        "nonNullByDefault" to true
    )
}

/**
 * Get a specific pattern
 */
fun getPattern(category: String, name: String): String? {
    return when (category) {
        "style" -> KotlinPatterns.style[name].toString()
        "naming" -> KotlinPatterns.naming[name]
        "types" -> KotlinPatterns.types[name].toString()
        else -> null
    }
}
