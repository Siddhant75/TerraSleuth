---
name: quota-defense-guardrail
enabled: true
event: all
conditions:
  - field: content
    operator: regex_match
    pattern: (api_key\s*=\s*["'][a-zA-Z0-9_-]{20,}["']|https://serpapi\.com/search\?.*api_key=)
---

⚠️ **CRITICAL QUOTA & CREDENTIAL GUARDRAIL TRIGGERED**

Direct, un-cached SerpApi API calls or unmasked API credentials detected.
All SerpApi requests in TerraSleuth MUST be routed through `backend.app.services.cache_service.CacheService` to protect free plan search credits and maintain deterministic testing!
