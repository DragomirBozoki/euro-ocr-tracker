# euro-ocr-tracker
```
→ OCR: 1,092.9
→ OCR: 1,103.7
→ OCR: 1,113.4
→ OCR: 1,122.4
⚠︎ Invalid OCR result. Reusing last stable value:
  → 1,122.4
→ OCR: 1,154.7
⚠︎ Value dropped from 1218.4 to 140.0. Keeping last stable value:
  → 1,218.4
```

The system automatically detects when OCR output is likely incorrect and logs a warning while displaying the last stable value instead.


This prevents sudden drops or misreadings (e.g., from noise or partial screenshots) from affecting the results.

### Accuracy of OCR Detection

In the sample session, out of **65** captured screenshots:
- 62 were successfully and correctly parsed.
- ⚠2 were marked as invalid and ignored.

**OCR stability rate: 96.88%**
