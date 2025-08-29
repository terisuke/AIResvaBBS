# Investigation of Gemini 2.5 Flash API Issues

**Date:** 2025-08-29

## 1. Summary (TL;DR)

The `gemini-2.5-flash` model consistently fails during basic API calls in our test environment. The error indicates the response is being blocked by Google's backend for policy reasons (`finish_reason: RECITATION`), not due to a configuration error on our side.

**The application's stability is not affected.** Our `GeminiClient` has a built-in fallback mechanism that automatically switches to `gemini-1.5-pro` when `gemini-2.5-flash` fails, ensuring service continuity.

## 2. Problem Description

When making an API call to the `gemini-2.5-flash` model using the `google-generativeai` library, the request fails. The library throws an `Invalid operation` error because the API returns no content (`Part`).

The candidate object in the API response contains `finish_reason: 2`, which corresponds to `RECITATION`. This means the response was blocked because it was flagged as a direct recitation from a source, even for simple, non-copyrighted prompts like "こんにちは" or "自己紹介をしてください。".

## 3. Investigation Steps

The following steps were taken to diagnose and resolve the issue, none of which were successful:

1.  **Verified Model Name:** Confirmed `gemini-2.5-flash` is the correct and intended model identifier.
2.  **Adjusted `safety_settings`:** Set all `HarmCategory` thresholds to `BLOCK_NONE`, the most permissive setting. The issue persisted, indicating it is not a standard safety filter block.
3.  **Modified Test Prompts:** Changed the test prompt from a simple greeting ("こんにちは") to a more open-ended request ("自己紹介をしてください。") to avoid potential "canned response" triggers. The blocking behavior remained unchanged.
4.  **Reviewed `thinkingConfig`:** Investigated using `thinkingConfig` as suggested by some documentation, but it did not resolve the issue and its usage in the library was not straightforward for this problem.

## 4. Root Cause Analysis

The `finish_reason: RECITATION` strongly suggests the blocking is happening on Google's backend due to a strict, non-configurable policy specific to the `gemini-2.5-flash` model. This policy appears to be overly sensitive in our test cases, flagging even benign, simple prompts. The issue does not seem to be solvable through standard API parameter adjustments.

## 5. Current Status & Mitigation

- **Current Status:** `gemini-2.5-flash` remains the first model in the `google` fallback list in `ai_clients.py` but is expected to fail in many cases.
- **Mitigation:** The `GeminiClient` is robust. Upon failure, it automatically proceeds to the next model in the list (`gemini-1.5-pro`), which has been tested and is stable. Therefore, end-users should not experience any disruption.

## 6. Recommended Next Steps

- **Monitor:** Keep `gemini-2.5-flash` in the fallback list and monitor its performance. The blocking behavior might change with future updates from Google.
- **Contact Support (Optional):** If consistent performance from `gemini-2.5-flash` becomes a priority, consider contacting Google Cloud support with the specific error details (`finish_reason: RECITATION`) to inquire about the blocking policy.
