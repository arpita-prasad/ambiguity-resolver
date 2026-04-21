# ArthaBot – Hindi Ambiguity Resolver
### End-to-End NLP Project | Text Analytics

---

## Getting Your FREE Gemini API Key

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Click "Create API Key"
5. Copy the key (starts with AIzaSy...)
6. Done!

---

## Local Setup

### Step 1 – Install
```bash
npm install
```

### Step 2 – Create .env file
```bash
# Create a file called .env in the project root and add:
VITE_GEMINI_API_KEY=your_key_here
```

### Step 3 – Run
```bash
npm run dev
# Open http://localhost:5173
```

---

## Deploy on Vercel
1. Push to GitHub
2. vercel.com → New Project → Import repo
3. Add env variable: VITE_GEMINI_API_KEY = your key
4. Deploy!

## Ambiguity Types Covered
1. Lexical         – word has multiple meanings (आम = mango OR common)
2. Syntactic       – sentence structure parsed multiple ways
3. Semantic        – meaning unclear even with clear structure
4. Pragmatic       – intent/context changes meaning
5. Referential     – pronoun points to multiple entities
6. Scope           – negation/quantifier scope unclear
7. Phonological    – same sound, different meaning (Hinglish)
8. Morphological   – multiple morpheme analyses