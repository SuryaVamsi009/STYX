# Use a one-time Gate 0 capital exception

Route B normally uses Surya-approved planning capital, but the single Gate 0 isolation test uses the explicitly approved ₹1,00,000 (1 lakh) at 1× so the safety exercise does not rely on the ₹1 Cr default or planning capital. This exception applies only to the specified virtual MIS order, is recorded in `evidence/gate_0.json`, cannot be used as strategy evidence, and requires a reset to approved planning capital before Gate 3 or any research or strategy run.

₹2,000 was the first approved test capital. OpenAlgo's sandbox only allows ₹1L, ₹5L, ₹10L, ₹25L, ₹50L or ₹1Cr, so Surya approved ₹1,00,000, the smallest allowed value, on 10 Nov 2026. Patching OpenAlgo to allow ₹2,000 was rejected, because Gate 0 must test the unmodified installed version.
