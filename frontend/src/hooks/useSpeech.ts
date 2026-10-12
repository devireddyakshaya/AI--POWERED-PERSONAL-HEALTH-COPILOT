import { useCallback, useEffect, useRef, useState } from 'react';
import { LanguageCode, getLanguage } from '../i18n/translations';
import { VoiceType } from '../types';

// Minimal typings for the Web Speech API (not part of the default TS lib)
interface SpeechRecognitionResultLike {
  transcript: string;
}
interface SpeechRecognitionEventLike {
  results: ArrayLike<ArrayLike<SpeechRecognitionResultLike>>;
}
interface SpeechRecognitionLike {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: ((event: { error?: string }) => void) | null;
  onend: (() => void) | null;
}

const getRecognitionCtor = (): (new () => SpeechRecognitionLike) | null => {
  const w = window as unknown as {
    SpeechRecognition?: new () => SpeechRecognitionLike;
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  };
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
};

export interface SpeakOptions {
  rate?: number;
  pitch?: number;
  onEnd?: () => void;
  /** Override the active language for this utterance (useful right after changing language) */
  langCode?: LanguageCode;
}

export const useSpeech = (language: LanguageCode, voiceType: VoiceType = 'system') => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);
  const [sttSupported, setSttSupported] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const speakTimerRef = useRef<number | null>(null);
  const endTimerRef = useRef<number | null>(null);

  useEffect(() => {
    const synth = typeof window !== 'undefined' ? window.speechSynthesis : undefined;
    setTtsSupported(!!synth);
    setSttSupported(getRecognitionCtor() !== null);

    if (synth) {
      // Voices are often loaded asynchronously. Listen for them so that the
      // assistant can speak in Indian locales right away.
      const loadVoices = () => setVoices(synth.getVoices());
      loadVoices();
      synth.addEventListener?.('voiceschanged', loadVoices);
      const retry = window.setTimeout(loadVoices, 400);
      return () => {
        window.clearTimeout(retry);
        synth.removeEventListener?.('voiceschanged', loadVoices);
        try {
          synth.cancel();
          recognitionRef.current?.abort();
        } catch {
          /* noop */
        }
      };
    }

    return () => {
      try {
        recognitionRef.current?.abort();
      } catch {
        /* noop */
      }
    };
  }, []);

  const clearSpeakTimers = useCallback(() => {
    if (speakTimerRef.current !== null) {
      window.clearTimeout(speakTimerRef.current);
      speakTimerRef.current = null;
    }
    if (endTimerRef.current !== null) {
      window.clearTimeout(endTimerRef.current);
      endTimerRef.current = null;
    }
  }, []);

  const pickVoice = (
    speechCode: string,
    list: SpeechSynthesisVoice[]
  ): SpeechSynthesisVoice | undefined => {
    if (!list.length) return undefined;
    const code = speechCode.toLowerCase();
    const base = code.split('-')[0];
    const matchesLanguage = list.filter((v) => {
      const lang = (v.lang || '').toLowerCase();
      return lang === code || lang.replace('_', '-') === code || lang.startsWith(base);
    });
    const pool = matchesLanguage.length ? matchesLanguage : list;

    // Best-effort gender match using well-known voice names per platform.
    if (voiceType !== 'system') {
      const femaleTokens = [
        'female', 'woman', 'zira', 'samantha', 'susan', 'karen', 'tessa',
        'moira', 'fiona', 'veena', 'heera', 'swara', 'kalpana', 'google हिन्दी'
      ];
      const maleTokens = [
        'male', 'man', 'david', 'daniel', 'alex', 'fred', 'rishi',
        'ravi', 'prabhat', 'hemant', 'madhur', 'microsoft रवि'
      ];
      const tokens = voiceType === 'female' ? femaleTokens : maleTokens;
      const gendered = pool.find((v) =>
        tokens.some((token) => (v.name || '').toLowerCase().includes(token))
      );
      if (gendered) return gendered;
    }

    return pool[0] || list.find((v) => v.default) || undefined;
  };

  const speak = useCallback(
    (text: string, options: SpeakOptions = {}) => {
      const synth = typeof window !== 'undefined' ? window.speechSynthesis : undefined;
      if (!text || !synth) {
        options.onEnd?.();
        return;
      }

      const finish = () => {
        setIsSpeaking(false);
        options.onEnd?.();
      };

      try {
        clearSpeakTimers();
        // Cancel any queued or paused speech first. Without this, Chrome can
        // silently drop the next utterance (the "records but never answers" bug).
        synth.cancel();

        const start = () => {
          speakTimerRef.current = null;
          try {
            const utterance = new SpeechSynthesisUtterance(text);
            const langOption = getLanguage(options.langCode || language);
            utterance.lang = langOption.speechCode;
            const voice = pickVoice(langOption.speechCode, synth.getVoices());
            if (voice) utterance.voice = voice;
            utterance.rate = options.rate ?? 0.98;
            utterance.pitch = options.pitch ?? 1;
            utterance.volume = 1;

            let ended = false;
            const end = () => {
              if (ended) return;
              ended = true;
              if (endTimerRef.current !== null) {
                window.clearTimeout(endTimerRef.current);
                endTimerRef.current = null;
              }
              finish();
            };

            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = end;
            utterance.onerror = end;

            utteranceRef.current = utterance;
            try {
              synth.resume();
            } catch {
              /* noop */
            }
            synth.speak(utterance);
            setIsSpeaking(true);

            // Safety net: some browsers never fire onend for a queued utterance.
            const estimated = Math.min(90000, 3000 + text.length * 90);
            endTimerRef.current = window.setTimeout(end, estimated);
          } catch {
            finish();
          }
        };

        // Chrome drops an utterance spoken in the same tick as cancel().
        speakTimerRef.current = window.setTimeout(start, 80);
      } catch {
        finish();
      }
    },
    [clearSpeakTimers, language, voiceType]
  );

  const stopSpeaking = useCallback(() => {
    clearSpeakTimers();
    try {
      window.speechSynthesis?.cancel();
    } catch {
      /* noop */
    }
    setIsSpeaking(false);
  }, [clearSpeakTimers]);

  const stopListening = useCallback(() => {
    try {
      recognitionRef.current?.stop();
    } catch {
      /* noop */
    }
    setIsListening(false);
  }, []);

  const listen = useCallback(
    (onResult: (transcript: string) => void, onError?: (message: string) => void) => {
      const Ctor = getRecognitionCtor();
      if (!Ctor) {
        onError?.('unsupported');
        return () => undefined;
      }
      stopSpeaking();
      try {
        recognitionRef.current?.abort();
      } catch {
        /* noop */
      }
      const recognition = new Ctor();
      recognition.lang = getLanguage(language).speechCode;
      recognition.interimResults = false;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = (event) => {
        try {
          const transcript = event.results[0][0].transcript;
          if (transcript) onResult(transcript);
        } catch {
          /* noop */
        }
      };
      recognition.onerror = (event) => {
        setIsListening(false);
        onError?.(event?.error || 'error');
      };
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
      try {
        recognition.start();
        setIsListening(true);
      } catch {
        setIsListening(false);
        onError?.('error');
      }

      return () => {
        try {
          recognition.abort();
        } catch {
          /* noop */
        }
        setIsListening(false);
      };
    },
    [language, stopSpeaking]
  );

  return {
    speak,
    stopSpeaking,
    listen,
    stopListening,
    isSpeaking,
    isListening,
    ttsSupported,
    sttSupported,
    hasVoices: voices.length > 0
  };
};
