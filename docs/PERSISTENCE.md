# 💾 Conversation Persistence Guide

## Overview

Both the Flask and Streamlit applications now support **conversation persistence**, allowing your chat history to survive page refreshes while maintaining complete privacy.

---

## 🔐 Privacy First

All conversation data remains **100% local** on your machine:
- ✅ **Flask**: Uses browser `localStorage` (stored in your browser)
- ✅ **Streamlit**: Uses a local JSON file in your home directory
- ✅ **No Cloud**: Nothing is sent to external servers
- ✅ **No Tracking**: Your conversations remain completely private

---

## Flask Application

### How It Works

The Flask app uses **browser localStorage** to automatically save and restore conversations.

### Storage Location
```
Browser localStorage
Key: 'ollama_chat_history'
```

### Features

1. **Automatic Saving**
   - Every message (user and bot) is automatically saved to localStorage
   - No manual action required

2. **Automatic Loading**
   - When you refresh the page or return later, your conversation is automatically restored
   - All message formatting and timestamps are preserved

3. **Clear Conversation**
   - Click the "Clear Chat History" button (🗑️)
   - Confirms before clearing
   - Removes both UI messages and localStorage data

### Developer Notes

```javascript
// Storage key
this.storageKey = 'ollama_chat_history';

// Saved data structure
{
    "messages": [
        {
            "id": "message-0",
            "role": "user",
            "content": "Hello!",
            "timestamp": "2:30 PM"
        },
        {
            "id": "message-1",
            "role": "bot",
            "content": "Hi! How can I help?",
            "timestamp": "2:30 PM"
        }
    ],
    "messageCounter": 2,
    "timestamp": "2024-11-10T14:30:00.000Z"
}
```

### Browser Compatibility

localStorage is supported in all modern browsers:
- ✅ Chrome/Edge (v4+)
- ✅ Firefox (v3.5+)
- ✅ Safari (v4+)
- ✅ Opera (v10.5+)

### Storage Limits

- Typical limit: **5-10 MB** per domain
- Sufficient for thousands of messages
- If limit is reached, older conversations should be cleared manually

---

## Streamlit Application

### How It Works

The Streamlit app uses a **local JSON file** to save and restore conversations across sessions.

### Storage Location
```
~/.ollama_streamlit_cache.json
(Your home directory)
```

### Features

1. **Automatic Saving**
   - Conversations are saved after each bot response
   - File is updated in real-time

2. **Automatic Loading**
   - On first run, checks for cached conversations
   - Restores all messages and metadata if found
   - Seamless experience across page refreshes

3. **Clear Conversation**
   - Click "🗑️ Clear Chat History" in sidebar
   - Removes both session state and cache file
   - Fresh start guaranteed

4. **Storage Indicator**
   - Sidebar shows "💾 Conversation saved locally" when cache exists
   - Shows "📝 Start chatting to save" when no cache

### File Structure

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is Python?"
    },
    {
      "role": "assistant",
      "content": "Python is a high-level programming language..."
    }
  ],
  "totalMessages": 2,
  "timestamp": "2024-11-10T14:30:00.000000"
}
```

### Manual Management

You can manually manage the cache file:

```bash
# View cache location
echo ~/.ollama_streamlit_cache.json

# View contents
cat ~/.ollama_streamlit_cache.json

# Manually delete cache
rm ~/.ollama_streamlit_cache.json

# Check file size
ls -lh ~/.ollama_streamlit_cache.json
```

---

## Comparison

| Feature | Flask | Streamlit |
|---------|-------|-----------|
| **Storage** | Browser localStorage | JSON file (~/) |
| **Persistence** | Per-browser | System-wide |
| **Size Limit** | 5-10 MB | No practical limit |
| **Portability** | Browser-specific | Shareable file |
| **Clearing** | UI button | UI button or manual |
| **Privacy** | Local browser | Local filesystem |

---

## Use Cases

### Flask (localStorage)
- ✅ Best for: Single-browser usage
- ✅ Persists across browser restarts
- ✅ Different browsers = different histories
- ✅ No filesystem access needed

### Streamlit (File-based)
- ✅ Best for: System-wide persistence
- ✅ Same history across all browsers
- ✅ Easy to backup/restore
- ✅ Can be version controlled (if desired)

---

## Data Privacy & Security

### What's Stored?
- Message content (user and bot)
- Message timestamps
- Message metadata (role, ID)

### What's NOT Stored?
- Personal information (unless you include it in messages)
- API keys (none used)
- Usage analytics
- Model weights or data

### Security Considerations

1. **Browser localStorage** (Flask)
   - Accessible to JavaScript on the same domain
   - Not encrypted by default
   - Protected by browser security policies

2. **JSON File** (Streamlit)
   - Stored in your home directory
   - Unix permissions: readable by your user
   - Not encrypted by default

### Recommendations

For sensitive conversations:
- ✅ Don't include passwords, keys, or secrets
- ✅ Clear history after sensitive sessions
- ✅ Use disk encryption (FileVault, BitLocker)
- ✅ Set appropriate file permissions

```bash
# Make cache file private (Streamlit)
chmod 600 ~/.ollama_streamlit_cache.json
```

---

## Troubleshooting

### Flask: Conversations Not Saving

1. **Check Browser Settings**
   - Ensure localStorage is enabled
   - Check if cookies/storage is blocked

2. **Check Console**
   - Open browser DevTools (F12)
   - Look for JavaScript errors
   - Check "Application" tab → "Local Storage"

3. **Clear Corrupted Data**
   ```javascript
   // In browser console
   localStorage.removeItem('ollama_chat_history');
   ```

### Streamlit: Cache Not Loading

1. **Check File Exists**
   ```bash
   ls -la ~/.ollama_streamlit_cache.json
   ```

2. **Check File Permissions**
   ```bash
   # Should be readable
   cat ~/.ollama_streamlit_cache.json
   ```

3. **Check JSON Validity**
   ```bash
   # Validate JSON
   python -m json.tool ~/.ollama_streamlit_cache.json
   ```

4. **Check Logs**
   ```bash
   tail -f logs/streamlit_app.log
   ```

---

## Migration & Backup

### Export Flask History

```javascript
// In browser console
const history = localStorage.getItem('ollama_chat_history');
console.log(history);
// Copy and save to file
```

### Backup Streamlit Cache

```bash
# Create backup
cp ~/.ollama_streamlit_cache.json ~/ollama_backup_$(date +%Y%m%d).json

# Restore from backup
cp ~/ollama_backup_20241110.json ~/.ollama_streamlit_cache.json
```

---

## Performance Impact

### Flask
- ✅ Minimal: localStorage operations are very fast
- ✅ Sync: No noticeable delay
- ✅ Size: Even with 1000s of messages, < 1 MB

### Streamlit
- ✅ Minimal: File I/O is fast for small JSON
- ✅ Async: Doesn't block UI
- ✅ Size: Scales well with message count

---

## Future Enhancements

Potential improvements:
- [ ] Export conversations to various formats (MD, TXT, PDF)
- [ ] Import conversations from files
- [ ] Multiple conversation threads
- [ ] Search within conversation history
- [ ] Encryption at rest
- [ ] Compression for large histories

---

## Summary

✅ **Conversations now persist** across page refreshes in both apps
✅ **100% Private** - all data stays on your machine
✅ **Automatic** - no manual saving required
✅ **Easy to Clear** - one-click removal of history
✅ **No Configuration** - works out of the box

Enjoy seamless conversation continuity! 🎉

