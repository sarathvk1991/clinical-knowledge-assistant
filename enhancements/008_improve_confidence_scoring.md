Improve the confidence scoring logic in confidence_service.py.

Requirements:

1. Keep existing structure but enhance scoring using:

   - average similarity
   - chunk count
   - similarity variance (NEW)
   - agreement score (NEW)

2. Compute:
   - variance of similarity scores
   - invert it to produce variance_score
   - agreement score based on how many chunks are close to top similarity

3. Final score:
   score =
     0.4 * avg_similarity +
     0.2 * chunk_count_score +
     0.2 * variance_score +
     0.2 * agreement_score

4. Clamp score to [0, 1]

5. Update level mapping:
   - high ≥ 0.75
   - medium ≥ 0.4
   - low < 0.4

6. Improve reasoning string to include:
   avg similarity, variance, agreement, chunk count

7. Keep function signature unchanged

8. Keep implementation simple and readable

Return full updated confidence_service.py