# Download Wav2Vec2 Model for SLAQ

This script downloads the required Wav2Vec2 model from Hugging Face for stuttering analysis.

## Model Information

**Model:** `facebook/wav2vec2-base-960h`
- **Size:** ~360 MB
- **Purpose:** Speech-to-text transcription for stutter detection
- **Source:** Hugging Face Transformers

## Option 1: Automatic Download (Recommended)

The model will be **automatically downloaded** the first time you run the analysis. This is handled by the Hugging Face `transformers` library.

### How it works:
1. When you first process an audio file, the AI engine will call:
   ```python
   from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
   
   processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
   model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
   ```

2. The model downloads to your system's cache directory:
   - **Windows:** `C:\Users\YourUsername\.cache\huggingface\`
   - **Linux/Mac:** `~/.cache/huggingface/`

3. Subsequent uses load from cache (instant)

### Advantages:
- ✅ No manual setup required
- ✅ Automatic version management
- ✅ Works out of the box

## Option 2: Pre-download Model (Optional)

If you want to download the model in advance (useful for offline development or faster first run):

### Method A: Using Python Script

Run this script to pre-download:

```bash
python download_model.py
```

(Script created in next step - see `download_model.py`)

### Method B: Using Transformers CLI

```bash
# Install transformers first
pip install transformers torch

# Download model
python -c "from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor; Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h'); Wav2Vec2ForCTC.from_pretrained('facebook/wav2vec2-base-960h'); print('✅ Model downloaded successfully!')"
```

### Method C: Manual Download (Advanced)

1. Visit: https://huggingface.co/facebook/wav2vec2-base-960h
2. Download all model files:
   - `config.json`
   - `preprocessor_config.json`
   - `pytorch_model.bin`
   - `special_tokens_map.json`
   - `tokenizer_config.json`
   - `vocab.json`
3. Place them in: `ml_models/wav2vec2/`
4. Update `diagnosis/ai_engine/model_loader.py` to load from local path

## Option 3: Custom Model Location

To use a specific directory for models, update your `.env` file:

```env
# Custom model cache directory
TRANSFORMERS_CACHE=/path/to/your/ml_models/cache
HF_HOME=/path/to/your/ml_models/cache
```

Then the models will download there instead of the default cache.

## Verifying Model Download

After downloading, verify with:

```bash
python -c "from transformers import Wav2Vec2ForCTC; model = Wav2Vec2ForCTC.from_pretrained('facebook/wav2vec2-base-960h'); print(f'✅ Model loaded! Parameters: {model.num_parameters():,}')"
```

Expected output:
```
✅ Model loaded! Parameters: 95,040,385
```

## Storage Requirements

- **Model Size:** ~360 MB
- **Cache Size:** ~400 MB (with tokenizer and config)
- **Recommended Free Space:** 1 GB (for safe operation)

## Network Requirements

**Initial Download:**
- Time: 2-5 minutes (depends on internet speed)
- Bandwidth: ~360 MB

**After First Download:**
- No network needed (loads from cache)

## Troubleshooting

### Issue: Slow Download
**Solution:** Use a VPN or mirror, or download during off-peak hours

### Issue: Download Fails
**Solutions:**
1. Check internet connection
2. Try different network
3. Manually download from Hugging Face website
4. Use `HF_ENDPOINT` environment variable for mirrors

### Issue: Out of Disk Space
**Solution:** Free up at least 1 GB before downloading

### Issue: Model Not Found
**Solution:** Ensure `transformers` is installed:
```bash
pip install transformers torch
```

## Alternative Models (Future)

For MVP, we use only `wav2vec2-base-960h`. Future versions may include:

- `facebook/wav2vec2-large-960h-lv60-self` (1.18 GB) - Higher accuracy
- `jonatasgrosman/wav2vec2-large-xlsr-53-english` (1.18 GB) - Multilingual

## Important Notes

1. ⚠️ **First run will be slower** due to model download
2. ⚠️ **Requires internet** for first-time setup
3. ✅ **Subsequent runs use cached model** (fast)
4. ✅ **No need to manually download** unless you want to

## Recommended Approach

**For Development:**
Just run your app! The model downloads automatically on first use.

**For Production:**
Pre-download the model during deployment:
```bash
python download_model.py
```

---

**Next Steps:**
1. Ensure you have `transformers` and `torch` installed
2. Run your application
3. Upload an audio file
4. Model downloads automatically during first analysis
5. Enjoy instant analysis on subsequent uploads!
