# MediMitra AI — Demo Video Script (Onboarding + Global Voice Assistant)

A shot-by-shot recording guide. Total runtime ~2:30–3:00. Aim for a **mobile phone feel**.

---

## 0. Setup (do this before recording)

1. Run the launchers from the project root:
   ```powershell
   .\start.ps1
   ```
   Wait until you see `backend: healthy` and the frontend URL `http://localhost:5173`.
2. Open **Chrome or Edge** (best Web Speech API support).
3. Press `F12` → click the **device toolbar** icon (or `Ctrl+Shift+M`) → choose **iPhone 12 Pro** (390 × 844). This gives the phone look.
4. When the browser asks for **Microphone access**, click **Allow**. (Needed for the voice commands later.)
5. Clear previous setup so onboarding always shows:
   - In the Console tab run: `localStorage.removeItem('hs_language'); localStorage.removeItem('hs_gender'); location.reload();`
6. Turn on **Do Not Disturb**; close other tabs. Set screen recorder to capture just the browser window at 1080×1920 (portrait) if possible.

> Tip: speak slowly and clearly on the voice shots. The browser's speech engine needs a clear accent-neutral phrase.

---

## Shot 1 — Cold open / Welcome (0:00–0:12)

- **Action:** Start recording. Show the welcome step of onboarding (logo + "Tap to start").
- **On screen:** MediMitra AI logo, app name, a big round **Tap to start** button.
- **Narration (EN):**
  > "Many people can't read a lab report — or see it. MediMitra AI talks to them, in their own language."
- **Telugu narration (optional):**
  > "చాలా మందికి ల్యాబ్ రిపోర్ట్ చదవడం రాదు. హెల్త్‌సాథీ AI వారి భాషలో మాట్లాడుతుంది."

---

## Shot 2 — Voice onboarding: language selection (0:12–0:42)

- **Action:** Tap **Tap to start**. The assistant speaks the welcome and asks for a language. Point the cursor at the **English / తెలుగు / हिन्दी / தமிழ் / ಕನ್ನಡ / മലയാളം** choices.
- **Demonstrate voice:** Tap the mic, then say clearly:
  > **"Telugu"**
- **On screen:** The Telugu tile highlights, the confirmation is spoken in Telugu.
- **Narration (EN):**
  > "No typing, no reading. You just say your language."

---

## Shot 3 — Voice onboarding: gender selection (0:42–1:00)

- **Action:** The gender step appears and is spoken aloud. Say:
  > **"Female"**  (or tap **Female** to show the no-voice path)
- **On screen:** Selection confirms, spoken affirmation in Telugu, then it moves to the upload screen.
- **Narration (EN):**
  > "One more question — then we're in. Everything is confirmed out loud."

---

## Shot 4 — Upload a report (1:00–1:30)

- **Action:** On **Upload & Review**, drag/drop or pick a sample report (PDF/JPG/PNG). Let the trust-check/parse animation play.
- **On screen:** Extracted values appear with **NORMAL / HIGH / LOW** tags; uncertain fields are flagged for verification.
- **Narration (EN):**
  > "Upload any report. MediMitra reads it, shows every value with its reference range, and flags anything uncertain — it never invents numbers."

---

## Shot 5 — The global voice assistant (1:30–2:10)

- **Action:** Tap the floating **mic launcher** (bottom corner). With hands-free on, say:
  > **"Read my report"**
- **On screen:** The assistant panel opens and reads the summary aloud in Telugu; the read-aloud button on the summary card lights up.
- **Then** say a navigation command:
  > **"Show my medications"**
- **On screen:** The app switches to the medication schedule; the assistant confirms.
- **Narration (EN):**
  > "This works anywhere in the app, hands-free. For a blind user, someone with low literacy, or someone who can't use their hands — the whole app is voice-controlled."

---

## Shot 6 — Multilingual proof + accessibility recap (2:10–2:40)

- **Action:** Open the report explainer. Use the language **dropdown** to switch: Telugu → Hindi → Tamil → Kannada → Malayalam. Each time, tap **Read aloud** so the summary is spoken.
- **On screen:** The same report summarized concisely in each language; test names and values stay in English for accuracy.
- **Narration (EN):**
  > "One report, six languages. The medical values stay exact — only the explanation changes."

---

## Shot 7 — Close (2:40–3:00)

- **Action:** Return to the dashboard. Show the disclaimer/trust badge.
- **Narration (EN):**
  > "MediMitra AI — a health report assistant that speaks your language, and never makes up a number. Always consult your doctor."

---

## Speaking cheat-sheet (say these exactly)

| Goal | Say |
|---|---|
| Pick language | "Telugu" (also try "Hindi", "English") |
| Pick gender | "Male" / "Female" |
| Read report | "Read my report" |
| Go to meds | "Show my medications" |
| Go to timeline | "Show my timeline" |
| Stop speaking | "Stop" |

If a command is missed, tap the mic again and repeat once. Background noise is the usual cause.

## Recording settings
- **Resolution:** 1080×1920 portrait (or 1125×2436), 30 fps.
- **Audio:** record system audio **and** mic separately if possible, then mix; voice prompts are the star.
- **Do not** speed up the voice shots — let the TTS finish each sentence.

## Fallback if speech isn't recognized
1. Confirm mic permission is **Allowed** for `localhost:5173`.
2. Use Chrome/Edge (Firefox/Safari STT support is limited).
3. If still stuck, show the **tap** path on camera and narrate that voice is optional — accessibility includes both.
