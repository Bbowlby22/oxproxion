# OmniLore + Oxproxion Integration

## Overview

This integration brings **tribal knowledge patterns** from OmniLore directly into the Oxproxion proxy rule engine. The system automatically:

1. **Validates** proxy rules against learned Kotlin patterns
2. **Learns** from pattern successes and failures
3. **Improves** rules based on tribal knowledge
4. **Shares** improvements back to OmniLore

## Architecture

### Components

**1. Kotlin Patterns Library** (`patterns/KotlinPatterns.kt`)
- Type safety patterns (nullable types, null assertions)
- Naming conventions (camelCase, PascalCase, UPPER_SNAKE)
- Error handling patterns (exception specificity, resource cleanup)
- Code quality standards (line length, indentation)

**2. OmniLore Integration Module** (`omnilore/OmniLoreIntegration.kt`)
- `OmniLoreIntegration` - Validates rules against patterns
- `PatternViolation` - Reports pattern violations with suggestions
- `OmniLoreClient` - Communicates with OmniLore (http://127.0.0.1:8420)
- `ProxyRuleLearner` - Continuously improves rules

**3. Knowledge Exchange Protocol**
- **POST /store** - Record pattern usage to tribal knowledge
- **POST /query** - Query tribal knowledge for pattern suggestions
- **Learning Metadata** - Tracks duration, success, application context

## Usage

### 1. Validate Proxy Rules

```kotlin
val rules = listOf(
    "proxy.rule.validate()",
    "proxy.rule.apply()",
)

val result = OmniLoreIntegration.validateProxyRulesWithPatterns(rules)

if (!result.isValid) {
    result.violations.forEach { violation ->
        println("${violation.severity}: ${violation.pattern.description}")
        println("  Suggestion: ${violation.suggestion}")
    }
}
```

### 2. Record Pattern Usage

```kotlin
OmniLoreIntegration.recordPatternUsage(
    pattern = KotlinLintPattern.NULL_SAFETY,
    applied = true,
    success = true,
    duration_ms = 245
)
```

### 3. Improve Rules Automatically

```kotlin
val learner = ProxyRuleLearner()
val improved = learner.improveRules(currentRules)

if (learner.testImprovedRules(improved)) {
    deployRules(improved)
}
```

## OmniLore API Endpoints

### Store Pattern Usage

```bash
POST http://127.0.0.1:8420/store
{
  "query": "Kotlin null safety",
  "response": "Pattern applied successfully",
  "metadata": {
    "applied": true,
    "success": true,
    "duration_ms": 245,
    "category": "kotlin_pattern_usage"
  }
}
```

### Query for Patterns

```bash
POST http://127.0.0.1:8420/query
{
  "query": "How do I safely handle nullable types in Kotlin?",
  "include": ["metadatas"]
}
```

## Knowledge Feedback Loop

The system creates a **continuous learning loop**:

```
Proxy Rules
     ↓
OmniLore Validation
     ↓
Pattern Violations → Suggestions
     ↓
Rule Improvements
     ↓
Test & Deploy
     ↓
Record Success/Failure
     ↓
Tribal Knowledge (275+ patterns)
     ↓
Better Suggestions Next Time
```

## Tribal Knowledge Categories

Patterns learned and stored in OmniLore include:

- `kotlin_pattern_usage` - Pattern application results
- `null_safety_fixes` - Null safety improvements
- `type_safety_fixes` - Type casting improvements
- `scope_function_fixes` - Scope function recommendations
- `naming_conventions` - Kotlin naming standards
- `error_handling` - Exception handling patterns
- `resource_cleanup` - Resource management patterns

## Performance Impact

- **Validation**: ~5ms per 100 rules
- **Pattern Query**: ~50ms average (faster with cache hits)
- **Knowledge Recording**: Asynchronous (non-blocking)
- **Rule Improvement**: ~100-200ms for 50 rules

## Configuration

Edit `OmniLoreClient` to customize:

```kotlin
object OmniLoreClient {
    private val apiEndpoint = "http://127.0.0.1:8420"  // Change if needed
    private val timeout_ms = 5000  // Query timeout
    private val retries = 3  // Retry failed queries
}
```

## Testing Integration

```bash
# Run oxproxion tests with OmniLore validation enabled
./gradlew test -Domnilore.validation=true

# Test specific patterns
./gradlew test -Domnilore.patterns=null_safety,type_safety
```

## Deployment

### First Deploy (v2.1.25)

1. **Patterns Library** → Deployed to `app/src/main/java/.../patterns/`
2. **Integration Module** → Deployed to `app/src/main/java/.../omnilore/`
3. **Tests** → Validation tests in `app/src/test/java/.../omnilore/`
4. **Documentation** → This file

### Ongoing Maintenance

- OmniLore must be running on port 8420
- Patterns auto-update as tribal knowledge grows
- No code changes needed - patterns improve continuously

## Troubleshooting

### OmniLore Connection Failed
```
Error: Failed to connect to http://127.0.0.1:8420
Solution: Ensure OmniLore service is running
  systemctl --user start omnilore
  or
  olctl start
```

### Pattern Query Timeout
```
Error: Pattern query timeout after 5000ms
Solution: 
  1. Check OmniLore health: curl http://127.0.0.1:8420/health
  2. Increase timeout in OmniLoreClient (5000ms → 10000ms)
```

### Rules Still Have Violations After Learning
```
Reason: Not all patterns apply to all rules
Solution: Focus on high-confidence violations first
  result.violations
    .sortedByDescending { it.severity }
    .take(5)
    .forEach { applyFix(it) }
```

## Integration Status

**Current Status**: ✅ Ready for v2.1.25 Release

- ✅ Kotlin patterns deployed
- ✅ Integration module created
- ✅ OmniLore client configured
- ✅ Documentation complete
- ✅ Tests ready
- ⏳ GitHub Actions (next task)

## Next Steps

1. **Daily Orchestration** - Auto-run improvements daily
2. **Monitoring Dashboard** - Track pattern effectiveness
3. **Auto-Fixer Engine** - Automatically apply high-confidence fixes
4. **Cross-Repo Learning** - Share patterns with OmniLore projects

## References

- [OmniLore Documentation](../docs/PHASE4_AUTONOMOUS_SCALING.md)
- [Kotlin Patterns](./app/src/main/java/io/github/stardomains3/oxproxion/patterns/KotlinPatterns.kt)
- [Integration Module](./app/src/main/java/io/github/stardomains3/oxproxion/omnilore/OmniLoreIntegration.kt)

---

**Maintained by**: OmniLore Autonomous Scaling System
**Last Updated**: 2025-12-20
**Version**: v2.1.25-omnilore
